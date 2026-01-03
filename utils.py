import re
import os
import csv
import json
import time
from datetime import date
from typing import Dict, Any
from typing import Dict, Any
from logging_config import setup_logger
import config

logger = setup_logger('Utils')

def create_results_folder() -> str:
    """
    Create a unique timestamped folder for this scraping run and set it as the global results folder.
    
    Returns:
        Path to the created folder
    """
    # Create base results directory if it doesn't exist
    base_dir = os.path.join("results")
    os.makedirs(base_dir, exist_ok=True)
    
    timestamp = str(time.time())
    run_dir = os.path.join(base_dir, timestamp)
    screen_dir = os.path.join(run_dir, "screenshots")
    
    # Create the folders
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(screen_dir, exist_ok=True)
    logger.info(f"Created results folder: {run_dir}")

    # Set the global variable
    config.CURRENT_RESULTS_FOLDER = run_dir
    
    return run_dir


def save_summary_to_json(summary: Dict[str, Any], filename: str = "summary.json"):
    """
    Save the scraping summary results to a JSON file.
    
    Args:
        summary: Summary information
        filename: Output filename
    """
    if not config.CURRENT_RESULTS_FOLDER:
        raise ValueError("Results folder not initialized. Call create_results_folder first.")
    
    filepath = os.path.join(config.CURRENT_RESULTS_FOLDER, filename)
    output = {
        "timestamp": time.time(),
        "summary": summary
    }

    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(output, file, indent=2)
    
    logger.info(f"Summary saved to {filename}")

def append_result_to_json(result: Dict[str, Any], filename: str = "result.json") -> None:
    """
    Append a result dictionary to a JSON file as part of a list.
    """
    if not config.CURRENT_RESULTS_FOLDER:
        raise ValueError("Results folder not initialized. Call create_results_folder first.")
    
    if not result:
        logger.warning("No result to write to JSON.")
        return
    
    filepath = os.path.join(config.CURRENT_RESULTS_FOLDER, filename)
    data = []
    # Load existing data if file exists
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as jsonfile:
            try:
                data = json.load(jsonfile)
            except json.JSONDecodeError:
                data = []

    # Append the new result
    data.append(result)

    # Write updated data back to the file
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        

def append_result_to_csv(result: Dict[str, Any], filename: str = "results.csv") -> None:
    """
    Append a result dictionary to a CSV file, including metadata and error info if present.
    """
    if not config.CURRENT_RESULTS_FOLDER:
        raise ValueError("Results folder not initialized. Call create_results_folder first.")
    if not result:
        logger.warning("No result to write to CSV.")
        return
    
    filepath = os.path.join(config.CURRENT_RESULTS_FOLDER, filename)
    file_exists = os.path.isfile(filepath)
    # Gather all possible keys
    base_keys = ['timestamp', 'url', 'status', 'from', 'to', 'outbound', 'inbound', 'error', 'attempts', 'duration']
    data_keys = list(result.get('data', {}).keys()) if result.get('data') else []
    fieldnames = base_keys + data_keys
    # Prepare row
    row = {k: result.get(k, '') for k in base_keys}
    for k in data_keys:
        v = result['data'][k]
        row[k] = v[0] if isinstance(v, list) and v else v if v else ''
    with open(filepath, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
        logger.info(f"Result written to CSV: {row}")

def clean_text(text: str) -> str:
    """Remove special characters, quotes, and normalize whitespace."""
    if not text: return ''
    text = re.sub(r'[\u202f\u2013\u20ac]', '', text) # Remove special Unicode characters
    text = ' '.join(text.split()) # Normalize whitespace
    return text.strip()

def is_date_range_valid(search_params: dict) -> bool:
    today = str(date.today())
    first = search_params["FirstDepartureDate"]
    last = search_params["LastDepartureDate"]
    if today < first < last:
        return True
    return False