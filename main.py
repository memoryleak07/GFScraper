import time
import threading
import concurrent.futures
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium_scraper import SeleniumScraper
from google_flight import *
from utils import *
from logging_config import setup_logger

MAX_WORKERS = 10
SELECTORS = {
        "price": 'div.YMlIz.FpEdX > span',
        "airline": 'div.sSHqwe.tPgKwe.ogfYpf',
        "time": 'div.zxVSec.YMlIz.tPgKwe.ogfYpf > span',
        "duration": 'div.Ak5kof > div',
        "type": 'div.EfT7Ae.AdWm1c.tPgKwe > span'
    }
logger = setup_logger('GFS')
stop_event = threading.Event()

def print_configurations(search_params, urls):
    """Print the script configurations."""
    logger.info("Configuration:")
    logger.info(f"    From Airports        : {', '.join(search_params['FromAirports'])}")
    logger.info(f"    To Airports          : {', '.join(search_params['ToAirports'])}")
    logger.info(f"    First Departure Date : {search_params['FirstDepartureDate']}")
    logger.info(f"    Last Departure Date  : {search_params['LastDepartureDate']}")
    logger.info(f"    How Many Days        : {search_params['HowManyDays']}")
    logger.info(f"    Flex Days            : {search_params['FlexDays']}")
    logger.info(f"    Only Weekend         : {search_params['OnlyWeekend']}")
    logger.info(f"    Total Combinations   : {len(urls)}")
    logger.info(f"    Max Workers          : {MAX_WORKERS}")
    logger.info(f"    Workers Needed       : {len(urls) // MAX_WORKERS + 1}")

def print_summary(summary):
    """Print the summary of the scraping process."""
    logger.info("Summary:")
    logger.info(f"    Total URLs           : {summary['total_urls']}")
    logger.info(f"    Successful URLs      : {summary['successful']}")
    logger.info(f"    Failed URLs          : {summary['failed']}")
    logger.info(f"    Total Duration (s)   : {summary['total_duration_seconds']:.2f}")
    logger.info(f"    Average Time/URL (s) : {summary['average_time_per_url']:.2f}")
    
def extract_flight_data(scraper: SeleniumScraper, timestamp: float) -> Dict[str, Any]:
    """Extract and clean flight information from the current page."""    
    results = {}
    scraper.accept_google_cookies()
    for key, selector in SELECTORS.items():
        elements = scraper.wait_for_elements(By.CSS_SELECTOR, selector)
        results[key] = [clean_text(elem.text) for elem in elements if elem.text]

    screenshot = scraper.take_screenshot(f"{config.CURRENT_RESULTS_FOLDER}/screenshots/{timestamp}.png")
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
    
    return result

def get_scraping_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a summary of the scraping results."""
    summary = {
        "total_urls": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] != "success"),
        "total_duration_seconds": sum(r["duration"] for r in results),
        "average_time_per_url": sum(r["duration"] for r in results) / len(results) if results else 0
    }
    return summary
    
def process_urls_concurrently(urls: List[str], max_workers: int = 5) -> List[Dict[str, Any]]:
    """
    Process multiple URLs concurrently using ThreadPoolExecutor.
    
    Args:
        urls: List of URLs to process
        max_workers: Maximum number of concurrent workers
        
    Returns:
        List of result dictionaries for each URL
    """
    logger.info("Starting scraping...")
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
                except Exception as e:
                    logger.exception(f"Thread for URL {url} generated an exception: {e}")
                    result = {"url": url, "status": "exception",  "error": str(e)}
                finally:
                    save_worker_result(result)
                    results.append(result)
                    logger.info(f"Thread for URL {url} completed. Status: {result['status']}")
        except KeyboardInterrupt:
            logger.warning("Keyboard interrupt received, shutting down executor...")
            stop_event.set()
            executor.shutdown(wait=False, cancel_futures=True)
            return
        
    logger.info("Scraping completed.")
    return results

def save_worker_result(result: Dict[str, Any]) -> None:
    """Save the result to JSON and CSV files."""
    append_result_to_json(result)
    append_result_to_csv(result)

def main():
    search_params = {
        "FromAirports": ["FCO", "NAP", "TRN"],
        "ToAirports": [
            ################### EUROPE #######################
            "AYT", # Antalya Airport (Turkish Riviera)
            "DLM", # Dalaman Airport (Turkish Riviera)
            "GZP", # Gazipaşa-Alanya Airport (Turkish Riviera)
            "BJV", # Milas-Bodrum Airport (Turkish Riviera)
            "RHO", # Rhodes International Airport Diagoras (Greek Island of Rhodi)
            ################### AMERICA #######################
            "BOG", # El Dorado International Airport (Bogotá)
            "MDE", # José María Córdova International Airport (Medellín)
            "CLO", # Alfonso Bonilla Aragón International Airport (Cali)
            "CTG", # Rafael Núñez International Airport (Cartagena)
            "BAQ", # Ernesto Cortissoz International Airport (Barranquilla)    
            "CUN", # Cancún International Airport (Cancún, Mexico)
            "SJU", # Luis Muñoz Marín International Airport (San Juan, Puerto Rico)
            "SJO", # Santamaría International Airport (San José, Costa Rica)
            "GIG", # Rio de Janeiro–Galeão International Airport (Rio de Janeiro, Brazil)
            "GRU", # São Paulo/Guarulhos–Governador André Franco Montoro International Airport (São Paulo, Brazil)
            ####################### ASIA #######################
            "ICN", # Incheon International Airport (Seoul, South Korea)
            "GMP", # Gimpo International Airport (Seoul, South Korea)
            "PUS", # Gimhae International Airport (Busan, South Korea)
            "DAD", # Da Nang International Airport (Da Nang, Vietnam)
            "HAN", # Noi Bai International Airport (Hanoi, Vietnam)
            "SGN", # Tan Son Nhat International Airport (Ho Chi Minh City, Vietnam)
            "BKK", # Suvarnabhumi Airport (Bangkok, Thailand)
            "DMK", # Don Mueang International Airport (Bangkok, Thailand)
            "HKT", # Phuket International Airport (Phuket, Thailand)
            "CNX", # Chiang Mai International Airport (Chiang Mai, Thailand)
            "PEK", # Beijing Capital International Airport (Beijing, China)
            "PVG", # Shanghai Pudong International Airport (Shanghai, China)
            "CAN", # Guangzhou Baiyun International Airport (Guangzhou, China)
            "HGH", # Hangzhou Xiaoshan International Airport (Hangzhou, China)
            "CTU", # Chengdu Shuangliu International Airport (Chengdu, China)
            "HND", # Haneda Airport (Tokyo, Japan)
            "KIX", # Kansai International Airport (Osaka, Japan)
            "CMB", # Bandaranaike International Airport (Colombo, Sri Lanka)
            "MNL", # Ninoy Aquino International Airport (Manila, Philippines)
            "CEB", # Mactan-Cebu International Airport (Cebu, Philippines)
            "DVO", # Francisco Bangoy International Airport (Davao, Philippines)
        ],
        "FirstDepartureDate": "2025-08-02",
        "LastDepartureDate": "2025-08-10",
        "HowManyDays": 15,
        "FlexDays": 6,
        "OnlyWeekend": False
    }

    try: 
        urls = generate_google_flight_urls(search_params)
        if not urls:
            logger.warning("No URLs generated. Exiting.")
            return
        
        print_configurations(search_params, urls)
        user_confirm = lambda prompt: input(prompt).strip().lower() in ['', 'y', 'yes']
        if not user_confirm("Do you want to continue? (y/n): "):
            logger.warning("User chose not to continue. Exiting.")
            return
        
        config.init()
        create_results_folder()
        
        results = process_urls_concurrently(urls, max_workers=MAX_WORKERS)
        if not results:
            logger.warning("No results obtained. Exiting.")
            return
        
        summary = get_scraping_summary(results)
        if not summary: 
            logger.warning("No summary generated. Exiting.")
            return

        save_summary_to_json(summary)
        print_summary(summary)
    except KeyboardInterrupt:
        stop_event.set()
        logger.warning("Process interrupted by user.")

if __name__ == "__main__":
    main()