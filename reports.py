from typing import Dict, Any, List


def get_scraping_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary of the scraping results.
    
    Args:
        results: List of result dictionaries from worker threads
        
    Returns:
        Dictionary containing aggregated scraping statistics
    """
    summary = {
        "total_urls": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] != "success"),
        "total_duration_seconds": sum(r["duration"] for r in results),
        "average_time_per_url": sum(r["duration"] for r in results) / len(results) if results else 0
    }
    return summary


def print_configurations(search_params: dict, urls: list, max_workers: int) -> None:
    """
    Print the script configurations and parameters.
    
    Args:
        search_params: Dictionary containing search parameters
        urls: List of generated URLs
        max_workers: Maximum number of concurrent workers
    """
    print("Configuration:")
    print(f"    From Airports        : {', '.join(search_params['FromAirports'])}")
    print(f"    To Airports          : {', '.join(search_params['ToAirports'])}")
    print(f"    First Departure Date : {search_params['FirstDepartureDate']}")
    print(f"    Last Departure Date  : {search_params['LastDepartureDate']}")
    print(f"    How Many Days        : {search_params['HowManyDays']}")
    print(f"    Flex Days            : {search_params['FlexDays']}")
    print(f"    Only Weekend         : {search_params['OnlyWeekend']}")
    print(f"    Total Combinations   : {len(urls)}")
    print(f"    Max Workers          : {max_workers}")
    print(f"    Workers Needed       : {len(urls) // max_workers + 1}")


def print_summary(summary: dict) -> None:
    """
    Print the summary of the scraping process.
    
    Args:
        summary: Dictionary containing scraping results summary
    """
    print("Summary:")
    print(f"    Total URLs           : {summary['total_urls']}")
    print(f"    Successful URLs      : {summary['successful']}")
    print(f"    Failed URLs          : {summary['failed']}")
    print(f"    Total Duration (s)   : {summary['total_duration_seconds']:.2f}")
    print(f"    Average Time/URL (s) : {summary['average_time_per_url']:.2f}")
