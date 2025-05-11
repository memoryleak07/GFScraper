import re
import os
import json
import time
from typing import List, Dict, Any
from logging_config import setup_logger
import csv
from typing import Dict, Any

logger = setup_logger('Utils')

def clean_text(text: str) -> str:
    """Remove special characters and normalize whitespace."""
    text = re.sub(r'[\u202f\u2013\u20ac]', '', text)  # Remove special chars
    text = re.sub(r'"', '', text) # Remove double quotes
    text = ' '.join(text.split())  # Normalize whitespace
    return text.strip()

def save_results_to_json(results: List[Dict[str, Any]], summary: Dict[str, Any], filename: str = "results.json"):
    """
    Save the scraping results to a JSON file.
    
    Args:
        results: The scraping results
        summary: Summary information
        filename: Output filename
    """
    output = {
        "timestamp": time.time(),
        "summary": summary,
        "results": results
    }
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(output, file, indent=2)
    
    logger.info(f"Results saved to {filename}")

def append_result_to_json(result: Dict[str, Any], filename: str = "result.json") -> None:
    """Append a result dictionary to a JSON file as part of a list."""
    data = []

    # Load existing data if file exists
    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            try:
                data = json.load(jsonfile)
            except json.JSONDecodeError:
                data = []

    # Append the new result
    data.append(result)

    # Write updated data back to the file
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        

def append_result_to_csv(result: Dict[str, Any], filename: str = "results.csv") -> None:
    """Append flight data rows to a CSV file, including metadata."""

    if not result.get("data"):
        logger.info("No data to append.")
        return

    data = result["data"]

    # Combine metadata keys and data keys for CSV header
    fieldnames = ["timestamp", "from", "to",  "outbound", "inbound"] + list(data.keys())

    # Determine the number of rows to write
    max_len = max(len(v) for v in data.values())

    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for i in range(max_len):
            row = {}

            # Add metadata
            row["timestamp"] = result["timestamp"]
            row["from"] = result["from"]
            row["to"] = result["to"]
            row["outbound"] = result["outbound"]
            row["inbound"] = result["inbound"]

            # Add data values, filling missing ones with ''
            for key in data.keys():
                row[key] = data[key][i] if i < len(data[key]) else ''

            # Skip faulty lines: all fields should be non-empty (after stripping)
            if all(str(value).strip() for value in row.values()):
                writer.writerow(row)
