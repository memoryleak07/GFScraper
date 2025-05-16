import re
import os
import csv
import json
import time
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
    Append a result dictionary to a CSV file, including metadata.
    """
    if not config.CURRENT_RESULTS_FOLDER:
        raise ValueError("Results folder not initialized. Call create_results_folder first.")
    
    if not result:
        logger.warning("No result to write to CSV.")
        return
    
    # Check if data exists and is not None
    if 'data' not in result or result['data'] is None:
        logger.warning(f"Result has no valid data to write to CSV: {result}")
        return
    
    # Extract data
    data = {k: v for k, v in result['data'].items()}
    if not data:
        logger.warning("No data to write to CSV.")
        return
    
    # Determine the number of rows (length of longest list)
    max_len = max(len(values) for values in data.values())
    
    # Prepare fieldnames 
    fieldnames = ['timestamp', 'from', 'to', 'outbound', 'inbound'] + list(data.keys())

    # Determine the number of rows to write
    max_len = max(len(v) for v in data.values())

    filepath = os.path.join(config.CURRENT_RESULTS_FOLDER, filename)
    file_exists = os.path.isfile(filepath)
    with open(filepath, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for i in range(max_len):
            row = {
                'timestamp': result['timestamp'],
                'from': result['from'],
                'to': result['to'],
                'outbound': result['outbound'],
                'inbound': result['inbound']
            }

            # Add data values, filling missing ones with ''
            for key in data.keys():
                row[key] = data[key][i] if i < len(data[key]) else ''

            # Skip faulty lines: all fields should be non-empty (after stripping)
            if all(str(value).strip() for value in row.values()):
                writer.writerow(row)
                logger.info(f"Row written to CSV: {row}")
            else:
                logger.warning(f"Row skipped due to empty fields: {row}")

def clean_text(text: str) -> str:
    """Remove special characters, quotes, and normalize whitespace."""
    if not text: return ''
    text = re.sub(r'[\u202f\u2013\u20ac]', '', text) # Remove special Unicode characters
    text = ' '.join(text.split()) # Normalize whitespace
    return text.strip()