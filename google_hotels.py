GOOGLE_HOTELS_BASE_URL = "https://www.google.com/travel/search?q=Hotels%20in%20{LOCATION}&check_in_date={CHECK_IN}&check_out_date={CHECK_OUT}&adults={ADULTS}"

def generate_google_hotels_url(search_params, base_url=GOOGLE_HOTELS_BASE_URL):
    """
    Generate a Google Hotels URL based on search parameters.
    
    Args:
        search_params (dict): Dictionary containing hotel search parameters
        base_url (str): URL template with placeholders for LOCATION, CHECK_IN, CHECK_OUT, and ADULTS
        
    Returns:
        str: Generated Google Hotels URL
    """
    # Extract parameters
    location = search_params.get("Location", "")
    check_in_date = search_params.get("CheckInDate", "")
    check_out_date = search_params.get("CheckOutDate", "")
    adults = search_params.get("Adults", 2)

    url = base_url.replace("{LOCATION}", location)\
                  .replace("{CHECK_IN}", check_in_date)\
                  .replace("{CHECK_OUT}", check_out_date)\
                  .replace("{ADULTS}", str(adults))
    
    return url

# Example usage
if __name__ == "__main__":
    search_params = {
        "Location": "Vienna",
        "CheckInDate": "2025-08-04",
        "CheckOutDate": "2025-08-07",
        "Adults": 2
    }

    url = generate_google_hotels_url(search_params)
    print(f"Generated Google Hotels URL: {url}")
