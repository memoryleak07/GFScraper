# GFScraper

A Python tool that scrapes Google Flights concurrently to find the best flight prices across multiple airport combinations and date ranges.

## Features

- Scrapes price, airline, departure/arrival times, duration, and flight type from Google Flights
- Generates all combinations of origin/destination airports and dates automatically
- Concurrent scraping with a configurable thread pool (default: 10 workers)
- Saves results incrementally to JSON and CSV as each URL is processed
- Takes a screenshot for every scraped page
- Supports flexible date ranges, trip duration, and weekend-only filtering
- Graceful shutdown on keyboard interrupt

## Requirements

- Python 3.x
- Google Chrome (ChromeDriver is downloaded automatically at startup via `webdriver-manager`)
- Dependencies listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

## Configuration

Edit `settings.json` before running:

```json
{
  "FromAirports": ["FCO", "MXP", "TRN"],
  "ToAirports": ["BOG", "MDE"],
  "FirstDepartureDate": "2026-03-01",
  "LastDepartureDate": "2026-12-28",
  "HowManyDays": 15,
  "FlexDays": 2,
  "OnlyWeekend": false
}
```

| Field | Description |
|---|---|
| `FromAirports` | List of origin IATA airport codes |
| `ToAirports` | List of destination IATA airport codes |
| `FirstDepartureDate` | Start of the search window (`YYYY-MM-DD`) |
| `LastDepartureDate` | End of the search window (`YYYY-MM-DD`) |
| `HowManyDays` | Trip duration in days |
| `FlexDays` | Flexibility in days around each departure date |
| `OnlyWeekend` | If `true`, only consider weekend departures |

## Usage

```bash
python main.py
```

The script will print the total number of URL combinations and ask for confirmation before starting. Results are saved in a timestamped folder under `results/`.

## Output

Each run produces:

- `results.json` — all scraped flight records
- `results.csv` — same data in CSV format
- `summary.json` — run statistics (total URLs, success/failure counts, timing)
- `screenshots/` — one PNG per scraped page

### results.csv sample

Each row represents one scraped Google Flights search (one origin/destination/date combination). The `price`, `airline`, `time`, `duration`, and `type` columns hold the first result returned by Google Flights for that query.

```csv
timestamp,url,status,from,to,outbound,inbound,error,attempts,duration,price,airline,time,duration,type
1748765432.12,https://www.google.com/travel/flights/...,success,FCO,BOG,2026-06-01,2026-06-16,,1,18.43,850,Avianca,10:25 – 06:30+1,19h 05m,1 stop
1748765451.88,https://www.google.com/travel/flights/...,success,MXP,MDE,2026-06-01,2026-06-16,,1,21.07,720,ITA Airways,07:10 – 18:45,23h 35m,1 stop
1748765473.55,https://www.google.com/travel/flights/...,success,TRN,BOG,2026-06-08,2026-06-23,,2,35.12,910,Air Europa,06:50 – 08:15+1,25h 25m,2 stops
1748765495.20,https://www.google.com/travel/flights/...,failed,FCO,CLO,2026-06-08,2026-06-23,Timeout waiting for element,2,42.60,,,,, 
```

| Column | Description |
|---|---|
| `timestamp` | Unix timestamp of when the URL was processed |
| `url` | The Google Flights URL that was scraped |
| `status` | `success` or `failed` |
| `from` | Origin airport IATA code |
| `to` | Destination airport IATA code |
| `outbound` | Departure date (`YYYY-MM-DD`) |
| `inbound` | Return date (`YYYY-MM-DD`) |
| `error` | Error message if the scrape failed, otherwise empty |
| `attempts` | Number of attempts before success or giving up |
| `duration` | Time spent processing this URL in seconds |
| `price` | Lowest price found (first result) |
| `airline` | Airline name (first result) |
| `time` | Departure and arrival times (first result) |
| `duration` | Flight duration (first result) |
| `type` | Stop description, e.g. `Nonstop`, `1 stop` (first result) |

## Project Structure

```
├── main.py               # Entry point; orchestrates concurrent scraping
├── google_flight.py      # URL generation logic for Google Flights
├── selenium_scraper.py   # Generic Selenium wrapper
├── config.py             # Paths and runtime configuration
├── utils.py              # Text cleaning and file I/O helpers
├── logging_config.py     # Logger setup
├── settings.json         # Search parameters (edit this)
└── requirements.txt
```

## Notes

**Fragility:** The CSS selectors in `main.py` are hardcoded against Google Flights' current DOM. Google updates its frontend frequently, so scrapes may silently return empty data or fail without warning. If results look wrong, inspect the selectors first.

**Bot detection:** Running 10 concurrent headless Chrome instances is aggressive and will likely trigger Google's bot detection, resulting in CAPTCHAs or IP-level blocks. If you hit this, try reducing `MAX_WORKERS`, adding delays between requests, or rotating user agents and proxies.

**Legal:** Google's Terms of Service prohibit automated scraping of their services. Use this tool for personal or research purposes only, and be aware that Google may block or rate-limit your IP at any time.

