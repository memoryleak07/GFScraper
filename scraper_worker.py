import os
import time
import threading
import concurrent.futures

from typing import Dict, List, Any
from selenium.webdriver.common.by import By
from selenium_scraper import SeleniumScraper
from utils import clean_text
from logging_config import setup_logger
import config

# CSS selectors for extracting flight data from Google Flights
SELECTORS = {
    "price": 'div.YMlIz.FpEdX > span',
    "airline": 'div.sSHqwe.tPgKwe.ogfYpf',
    "time": 'div.zxVSec.YMlIz.tPgKwe.ogfYpf > span',
    "duration": 'div.Ak5kof > div',
    "type": 'div.EfT7Ae.AdWm1c.tPgKwe > span'
}

logger = setup_logger('Worker')
stop_event = threading.Event()


def extract_flight_data(scraper: SeleniumScraper, timestamp: float) -> Dict[str, Any]:
    """
    Extract and clean flight information from the current page.
    
    Args:
        scraper: SeleniumScraper instance for the current thread
        timestamp: Timestamp for organizing screenshots
        
    Returns:
        Dictionary containing extracted flight data and screenshot path
    """
    results = {}
    scraper.accept_google_cookies()
    for key, selector in SELECTORS.items():
        elements = scraper.wait_for_elements(By.CSS_SELECTOR, selector)
        results[key] = [clean_text(elem.text) for elem in elements if elem.text]

    screenshot = scraper.take_screenshot(
        f"{config.CURRENT_RESULTS_FOLDER}/screenshots/{timestamp}.png"
    )
    return {
        "values": results,
        "screenshot": screenshot
    }


def process_url(url: str, max_retries: int = 2) -> Dict[str, Any]:
    """
    Process a single URL with a SeleniumScraper instance.
    
    This function runs in a worker thread and handles retries for failed attempts.
    
    Args:
        url: Dictionary with URL and flight details
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


def process_urls_concurrently(
    urls: List[str], 
    max_workers: int = 5,
    result_callback: callable = None
) -> List[Dict[str, Any]]:
    """
    Process multiple URLs concurrently using ThreadPoolExecutor.
    
    Args:
        urls: List of URL dictionaries to process
        max_workers: Maximum number of concurrent worker threads
        result_callback: Optional callback function called for each result
        
    Returns:
        List of result dictionaries for each URL
    """
    logger.info("Starting concurrent URL processing...")
    results = []
    processed_urls = 0
    
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
                    logger.error(f"Thread for URL {url} generated an exception: {e}")
                    result = {"url": url, "status": "exception", "error": str(e)}
                finally:
                    if result_callback:
                        result_callback(result)
                    results.append(result)
                    processed_urls += 1
                    logger.debug(f"Thread for URL {url} completed. Status: {result['status']}")
                    logger.debug(
                        f"Processed: {processed_urls}/{len(urls)} - "
                        f"Remaining: {len(urls) - processed_urls}"
                    )

        except KeyboardInterrupt:
            logger.warning("Keyboard interrupt received, shutting down executor...")
            stop_event.set()
            executor.shutdown(wait=False, cancel_futures=True)
            os._exit(1)
        
    logger.info("Concurrent processing completed.")
    return results
