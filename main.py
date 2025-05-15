import time
import threading
import concurrent.futures
from typing import List, Dict, Any
from selenium.webdriver.common.by import By

from selenium_scraper import SeleniumScraper
from google_flight import *
from utils import *
from logging_config import setup_logger

logger = setup_logger('GFS')
stop_event = threading.Event()
MAX_WORKERS = 5
SELECTORS = {
        "price": 'div.YMlIz.FpEdX > span',
        "airline": 'div.sSHqwe.tPgKwe.ogfYpf',
        "time": 'div.zxVSec.YMlIz.tPgKwe.ogfYpf > span',
        "duration": 'div.Ak5kof > div',
        "type": 'div.EfT7Ae.AdWm1c.tPgKwe > span'
    }

def print_configurations(search_params, urls):
    """Print the script configurations."""
    logger.info("Configuration:")
    logger.info(f"  From Airports       : {', '.join(search_params['FromAirports'])}")
    logger.info(f"  To Airports         : {', '.join(search_params['ToAirports'])}")
    logger.info(f"  First Departure Date: {search_params['FirstDepartureDate']}")
    logger.info(f"  Last Departure Date : {search_params['LastDepartureDate']}")
    logger.info(f"  How Many Days       : {search_params['HowManyDays']}")
    logger.info(f"  Flex Days           : {search_params['FlexDays']}")
    logger.info(f"  Only Weekend        : {search_params['OnlyWeekend']}")
    logger.info(f"  Total Combinations (URLs to scrape): {len(urls)}")

def print_summary(summary):
    """Print the summary of the scraping process."""
    logger.info("Summary:")
    logger.info(f"  Total URLs          : {summary['total_urls']}")
    logger.info(f"  Successful URLs     : {summary['successful']}")
    logger.info(f"  Failed URLs         : {summary['failed']}")
    logger.info(f"  Total Duration (s)  : {summary['total_duration_seconds']:.2f}")
    logger.info(f"  Average Time/URL (s): {summary['average_time_per_url']:.2f}")
    
def extract_flight_data(scraper: SeleniumScraper, timestamp: float) -> Dict[str, Any]:
    """Extract and clean flight information from the current page."""    
    results = {}
    scraper.accept_google_cookies()
    for key, selector in SELECTORS.items():
        elements = scraper.wait_for_elements(By.CSS_SELECTOR, selector)
        results[key] = [clean_text(elem.text) for elem in elements if elem.text]
           
    screenshot = scraper.take_screenshot(f"screenshot_{timestamp}.png")   
    return {
        "values": results,
        "screenshot": screenshot
    }

def process_url(url: str, max_retries: int = 2) -> Dict[str, Any]:
    """
    Process a single URL with a SeleniumScraper instance.
    This function will be called concurrently for different URLs.
    
    Args:
        url: The URL to process
        max_retries: Maximum number of retry attempts for failures
        
    Returns:
        Dictionary containing the processing results
    """
    timestamp = time.time()
    result = {
        "status": "failed",
        "url": url["url"],
        "from": url["from"],
        "to": url["to"],
        "outbound": url["outbound"],
        "inbound": url["inbound"],
        "timestamp": timestamp,
        "duration": 0,
        "attempts": 0,
        "screenshot": None,
        "data": None,
        "error": None
    }
        
    # Create a new scraper instance for this thread
    with SeleniumScraper() as scraper:
        attempts = 0
        success = False
        
        while attempts < max_retries and not success:
            attempts += 1
            if stop_event.is_set():
                scraper.logger.warning("Stop event set. Exiting thread.")
                return result
            try:
                # Run the complete scraping task using our generic scraper
                scraping_result = scraper.run_scraping_task(
                    url["url"], 
                    lambda s: extract_flight_data(s, timestamp))
                
                # Check if the scraping was successful
                if scraping_result["success"]:
                    result["status"] = "success"
                    result["data"] = scraping_result["data"]["values"]
                    result["screenshot"] = scraping_result["data"]["screenshot"]
                    # Append the result to CSV
                    append_result_to_csv(result)
                    success = True
                else:
                    scraper.logger.warning(f"Attempt {attempts} failed: {scraping_result['error']}")
                    if attempts < max_retries:
                        time.sleep(2)
            
            except Exception as e:
                scraper.logger.error(f"Error in attempt {attempts}: {str(e)}")
                result["error"] = str(e)
                if attempts < max_retries:
                    time.sleep(2)
    
    # Include retry information
    result["attempts"] = attempts
    result["duration"] = time.time() - timestamp
    
    # Append the result to JSON
    append_result_to_json(result)

    return result

def process_urls_concurrently(urls: List[str], max_workers: int = 5) -> Dict[str, Any]:
    """
    Process multiple URLs concurrently using ThreadPoolExecutor.
    
    Args:
        urls: List of URLs to process
        max_workers: Maximum number of concurrent workers
        
    Returns:
        List of result dictionaries for each URL
    """
    logger.info("Starting scraping...")

    start_time = time.time()
    results = []
    
    # Using ThreadPoolExecutor to run tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all URL processing tasks
        future_to_url = {executor.submit(process_url, url): url for url in urls}        
        try:
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                if stop_event.is_set(): 
                    break
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed: {url} - Status: {result['status']}")
                except Exception as e:
                    logger.exception(f"Thread for URL {url} generated an exception: {e}")
                    results.append({
                        "url": url, 
                        "status": "exception", 
                        "error": str(e)
                    })
        except KeyboardInterrupt:
            logger.warning("Keyboard interrupt received, shutting down executor...")
            stop_event.set()
            executor.shutdown(wait=False, cancel_futures=True)
            return
    
    # Add summary information
    end_time = time.time()
    duration = end_time - start_time    
    summary = {
        "total_urls": len(urls),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] != "success"),
        "total_duration_seconds": duration,
        "average_time_per_url": duration / len(urls) if urls else 0
    }

    logger.info("Scraping completed.")
    return summary

def main():
    search_params = {
        "FromAirports": ["FCO"],
        "ToAirports": [
            "AYT", # Antalya Airport (Turkish Riviera)
            "DLM", # Dalaman Airport (Turkish Riviera)
            "GZP", # Gazipaşa-Alanya Airport (Turkish Riviera)
            "BJV", # Milas-Bodrum Airport (Turkish Riviera)
            "RHO", # Rhodes International Airport Diagoras (Greek Island of Rhodi)
            "BOG", # El Dorado International Airport (Bogotá)
            "MDE", # José María Córdova International Airport (Medellín)
            "CLO", # Alfonso Bonilla Aragón International Airport (Cali)
            "CTG", # Rafael Núñez International Airport (Cartagena)
            "BAQ", # Ernesto Cortissoz International Airport (Barranquilla)    
            "CUN", # Cancún International Airport (Cancún, Mexico)
            "SJU", # Luis Muñoz Marín International Airport (San Juan, Puerto Rico)
            "GIG"  # Rio de Janeiro–Galeão International Airport (Rio de Janeiro, Brazil)
        ],
        "FirstDepartureDate": "2025-08-02",
        "LastDepartureDate": "2025-08-10",
        "HowManyDays": 15,
        "FlexDays": 6,
        "OnlyWeekend": False
    }

    try:            
        urls = generate_google_flight_urls(search_params)
        print_configurations(search_params, urls)
        summary = process_urls_concurrently(urls, max_workers=MAX_WORKERS)
        if not summary: 
            return
        save_summary_to_json(summary)
        print_summary(summary)       
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
        
if __name__ == "__main__":
    main()