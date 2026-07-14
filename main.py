import argparse
import json
from typing import Dict, Any, List
from google_flight import generate_google_flight_urls
from utils import (
    create_results_folder,
    save_summary_to_json,
    is_date_range_valid,
    append_result_to_json,
    append_result_to_csv,
)
from selenium_scraper import SeleniumScraper
from logging_config import setup_logger, configure_logging, parse_log_level
from scraper_worker import process_urls_concurrently, stop_event
from reports import print_configurations, print_summary, get_scraping_summary
import config

MAX_WORKERS = 10
logger = setup_logger('GFS')

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run the Google Flights scraping workflow.'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level for the application.',
    )
    return parser.parse_args()


def save_worker_result(result: Dict[str, Any]) -> None:
    """Save the result to JSON and CSV files."""
    append_result_to_json(result)
    append_result_to_csv(result)

def pre_initialize_chromedriver() -> None:
    """
    Pre-initialize ChromeDriver before spawning worker threads.
    
    This prevents race conditions when webdriver-manager attempts to extract
    and rename chromedriver.exe simultaneously from multiple threads.
    All subsequent worker threads will find the driver already initialized.
    
    Raises:
        Exception: If ChromeDriver initialization fails
    """
    logger.debug("Pre-initializing ChromeDriver to avoid thread race conditions...")
    try:
        temp_scraper = SeleniumScraper(logger=logger)
        temp_scraper.initialize_driver()
        if temp_scraper.driver:
            temp_scraper.driver.quit()
        logger.debug("ChromeDriver pre-initialization completed successfully.")
    except Exception as e:
        logger.error(f"Failed to pre-initialize ChromeDriver: {e}")
        raise

def setup_scraping_environment(search_params: Dict[str, Any]) -> None:
    """
    Set up the scraping environment before processing URLs.
    
    Initializes configuration, creates result folders, and pre-initializes
    the ChromeDriver to avoid threading issues.
    
    Args:
        search_params: Dictionary containing search parameters from settings
        
    Raises:
        Exception: If any setup step fails
    """
    logger.debug("Setting up scraping environment...")
    config.init()
    create_results_folder()
    pre_initialize_chromedriver()

def main():
    args = parse_args()
    configure_logging(args.log_level)
    logger.setLevel(parse_log_level(args.log_level))
    logger.info("Log level set to %s", args.log_level)

    try:
        with open('settings.json', 'r') as file:
            search_params = json.load(file)
        
        if not search_params:
            logger.warning("No settings.json found. Exiting.")
            return

        if not is_date_range_valid(search_params):
            logger.warning("Dates from settings.json are invalid. Exiting.")
            return

        urls = generate_google_flight_urls(search_params)
        if not urls:
            logger.warning("No URLs generated. Exiting.")
            return

        logger.info("Starting scraping with %d URLs", len(urls))
        print_configurations(search_params, urls, MAX_WORKERS)
        user_confirm = lambda prompt: input(prompt).strip().lower() in ['', 'y', 'yes']
        if not user_confirm("Do you want to continue? (y/n): "):
            logger.warning("User chose not to continue. Exiting.")
            return
        
        setup_scraping_environment(search_params)

        results = process_urls_concurrently(urls, max_workers=MAX_WORKERS, result_callback=save_worker_result)
        if not results:
            logger.warning("No results obtained. Exiting.")
            return

        logger.info("Scraping completed with %d result groups", len(results))
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