from datetime import datetime, timedelta
import time
import itertools
import json

GOOGLE_FLIGHTS_BASE_URL = "https://www.google.com/travel/flights?q=Flights%20to%20{TO}%20from%20{FROM}%20on%20{OUTBOUND}%20through%20{INBOUND}"

def generate_google_flight_urls(search_params, base_url=GOOGLE_FLIGHTS_BASE_URL):
    """
    Generate a list of Google Flight URLs based on search parameters.
    
    Args:
        search_params (dict): Dictionary containing flight search parameters
        base_url (str): URL template with placeholders for FROM, TO, OUTBOUND, and INBOUND
        
    Returns:
        list: List of generated Google Flight URLs
    """
    # Extract parameters
    from_airports = search_params.get("FromAirports", [])
    to_airports = search_params.get("ToAirports", [])
    first_departure_date = datetime.strptime(search_params.get("FirstDepartureDate"), "%Y-%m-%d")
    last_departure_date = datetime.strptime(search_params.get("LastDepartureDate"), "%Y-%m-%d")
    how_many_days = search_params.get("HowManyDays", 0)
    flex_days = search_params.get("FlexDays", 0)
    only_weekend = search_params.get("OnlyWeekend", False)
    
    # Generate all possible date combinations
    departure_dates = []
    current_date = first_departure_date
    
    while current_date <= last_departure_date:
        # If only weekend is selected, check if the day is Saturday or Sunday
        if only_weekend and current_date.weekday() not in [5, 6]:  # 5=Saturday, 6=Sunday
            current_date += timedelta(days=1)
            continue
            
        departure_dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Generate flexible departure dates
    flexible_departures = []
    for date in departure_dates:
        for flex in range(-flex_days, flex_days + 1):
            flex_date = date + timedelta(days=flex)
            # Ensure the flexible date is within the original date range
            if first_departure_date <= flex_date <= last_departure_date:
                flexible_departures.append(flex_date)
    
    # Remove duplicates and sort
    flexible_departures = sorted(list(set(flexible_departures)))
    
    # Generate return dates for each departure date
    date_pairs = []
    for dep_date in flexible_departures:
        return_date = dep_date + timedelta(days=how_many_days)
        date_pairs.append((dep_date, return_date))
    
    # Generate all URL combinations
    urls = []
    for from_airport, to_airport in itertools.product(from_airports, to_airports):
        for outbound_date, inbound_date in date_pairs:
            outbound_str = outbound_date.strftime("%Y-%m-%d")
            inbound_str = inbound_date.strftime("%Y-%m-%d")
            
            url = base_url.replace("{FROM}", from_airport)\
                          .replace("{TO}", to_airport)\
                          .replace("{OUTBOUND}", outbound_str)\
                          .replace("{INBOUND}", inbound_str)
            
            urls.append({
                "from": from_airport,
                "to": to_airport, 
                "outbound": outbound_str,
                "inbound": inbound_str,
                "url": url
            })
    
    return urls


def print_results(urls, max_urls=5):
    """
    Print the generated URLs in a readable format.
    
    Args:
        urls (list): List of generated URLs
    """
    print(f"Generated {len(urls)} URLs:")
    for i, url_data in enumerate(urls[:max_urls], 1):
        print(f"\n{i}. From: {url_data['from']} To: {url_data['to']}")
        print(f"   Outbound: {url_data['outbound']} Inbound: {url_data['inbound']}")
        print(f"   URL: {url_data['url']}")
    
    if len(urls) > max_urls:
        print(f"\n... and {len(urls) - max_urls} more URLs")

def save_results_to_json(urls, filename=f"{time.time()}_urls.json"):
    """
    Save the generated URLs to a JSON file with a summary.
    
    Args:
        urls (list): List of generated URLs
        filename (str): Name of the JSON file to save the results
    """
    summary = {
        "timestamp": time.time(),
        "total_urls": len(urls),
        "first_url": urls[0] if urls else None,
        "last_url": urls[-1] if urls else None
    }
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump({"summary": summary, "urls": urls}, jsonfile, indent=2, ensure_ascii=False)

    print(f"Results saved to {filename}")


# Example usage
if __name__ == "__main__":
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
            "GIG", # Rio de Janeiro–Galeão International Airport (Rio de Janeiro, Brazil)
            "GRU", # São Paulo/Guarulhos–Governador André Franco Montoro International Airport (São Paulo, Brazil)
            "SDU", # Santos Dumont Airport (Rio de Janeiro, Brazil)
            ####################### ASIA #######################
            "ICN", # Incheon International Airport (Seoul, South Korea)
            "GMP", # Gimpo International Airport (Seoul, South Korea)
            "PUS", # Gimhae International Airport (Busan, South Korea)
            "CJU", # Jeju International Airport (Jeju, South Korea)
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
            "NRT", # Narita International Airport (Tokyo, Japan)
            "HND", # Haneda Airport (Tokyo, Japan)
            "KIX", # Kansai International Airport (Osaka, Japan)
            "NGO", # Chubu Centrair International Airport (Nagoya, Japan)
            "FUK", # Fukuoka Airport (Fukuoka, Japan) 
            "CMB", # Bandaranaike International Airport (Colombo, Sri Lanka)
            "MRIA", # Mattala Rajapaksa International Airport (Hambantota, Sri Lanka)
            "MNL", # Ninoy Aquino International Airport (Manila, Philippines)
            "CEB", # Mactan-Cebu International Airport (Cebu, Philippines)
            "DVO", # Francisco Bangoy International Airport (Davao, Philippines)
            "PPS", # Puerto Princesa International Airport (Palawan, Philippines)
            "CRK", # Clark International Airport (Angeles/Mabalacat, Philippines)
        ],
        "FirstDepartureDate": "2025-08-02",
        "LastDepartureDate": "2025-08-10",
        "HowManyDays": 15,
        "FlexDays": 6,
        "OnlyWeekend": False
    }
    
    urls = generate_google_flight_urls(search_params)
    print_results(urls, 5)
    save_results_to_json(urls)
