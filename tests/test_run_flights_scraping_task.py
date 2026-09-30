import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
import sys
from pathlib import Path

# Adds project root (GFScraper) to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from selenium_scraper import SeleniumScraper
from google_flights import *
from utils import *

def extract_flight_data(scraper: SeleniumScraper) -> Dict[str, Any]:
    results = {}
    try:
        scraper.accept_google_cookies()
        # Example: Extract flight prices
        price_elements = scraper.wait_for_elements(By.CSS_SELECTOR, 'div.YMlIz.FpEdX > span')
        prices = [elem.text for elem in price_elements if elem.text]
        results["prices"] = prices
        
        # Example: Extract airlines
        airline_elements = scraper.wait_for_elements(By.CSS_SELECTOR, 'div.sSHqwe.tPgKwe.ogfYpf')
        airlines = [elem.text for elem in airline_elements if elem.text]
        results["airlines"] = airlines
        
        # Example: Extract flight time
        time_elements = scraper.wait_for_elements(By.CSS_SELECTOR, 'div.zxVSec.YMlIz.tPgKwe.ogfYpf > span')
        times = [elem.text for elem in time_elements if elem.text]
        results["time"] = times
        
        # Example: Extract flight duration
        duration_elements = scraper.wait_for_elements(By.CSS_SELECTOR, 'div.Ak5kof > div')
        durations = [elem.text for elem in duration_elements if elem.text]
        results["durations"] = durations

        # Example: Extract type of flight
        type_elements = scraper.wait_for_elements(By.CSS_SELECTOR, 'div.EfT7Ae.AdWm1c.tPgKwe > span')
        types = [elem.text for elem in type_elements if elem.text]
        results["types"] = types
        
        # # Take a screenshot for debugging or verification
        # screenshot_path = scraper.take_screenshot(f"flight_results_{int(time.time())}.png")
        # results["screenshot"] = screenshot_path
        
    except Exception as e:
        scraper.logger.error(f"Error extracting flight data: {str(e)}")
        results["error"] = str(e)
    
    return results


def main():
    max_retries = 2
    url = 'https://www.google.com/travel/flights?q=Flights%20to%20VIE%20from%20NAP%20on%202025-08-04%20through%202025-08-07'
    result = {
            "url": url,
            "timestamp": time.time(),
            "status": "failed",
            "data": None,
            "error": None
        }
    
    test_logger = setup_logger('Test')
    with SeleniumScraper(headless=False) as scraper:
        attempts = 0
        success = False
        
        while attempts < max_retries and not success:
            attempts += 1
            try:
                # Run the complete scraping task
                scraping_result = scraper.run_scraping_task(url, extract_flight_data)
                
                # Check if the scraping was successful
                if scraping_result["success"]:
                    result["status"] = "success"
                    result["data"] = scraping_result["data"]
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
                    
    print(result)


if __name__ == "__main__":
    main()