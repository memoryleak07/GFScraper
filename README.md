# GoogleFlightsScraper 1.5

AVOLOAVOLO.it TRIBUTE

This simple python script scrape price and information about the first flight sorted on GoogleFlights and save data to CSV file.

Given a list of airport codes as departure flights option, a list of ariport codes as possible destinations and the search date range, the program will scrape all combination one by one, storing data of first A/R flight shown by GoogleFlights for each search.

The search parameters are in the settings.json file.

## Example of settings.json

```json
 ()){
    //Departure airport codes list (list)
    "from": [
          "FCO",
          "NAP"
    ],
    //Arrival airport codes list (list)
    "to": [
          "MED",
          "BOG",
          "CTG"
    ],
    //First date for departure flight: (str)
    "outbound": "2023-10-1",
    //Number of days before return flight: (int)
    "delta": 20,
    //Day of flexibility for the return flight: (int|None)
    "flexdays": 3,
    //Search only departure on Saturday: (bool|None)
    "weekend": false,
    //Ultima data utile per il volo di partenza: (str|None)
    "lastdate": "2023-12-1",
    //If true does not click on first flight to save info about return flight: (bool|None)
    "fastmode": true, 
    //Timeout in secords for skip scrape if element not found (int|None)
    "timeout": 10,
    //Class - NOT IMPLEMENTED 1.5
    "tclass": [
        "economy",
        "business",
        "first"
  ]
}
```
