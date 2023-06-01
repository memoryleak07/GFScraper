# GoogleFlightsScraper 1.5

(AVOLOAVOLO.it TRIBUTE)

This simple python script scrape prices and informations about the first flight sorted on GoogleFlights and save data to CSV file.

From a given list of airport codes as departure flights and a list of ariport codes as arrival destinations, given the search date range the script will scrape all combination one by one and store the infromation.

The search parameters are in the settings.json file.

## Example of settings.json

```json
{
    //Departure airport codes list
    "from": [
          "FCO",
          "NAP"
    ],
    //Arrival airport codes list
    "to": [
          "MED",
          "BOG",
          "CTG"
    ],
    //First date for departure flight:
    "outbound": "2023-10-1",
    //Number of days before return flight:
    "delta": 20,
    //Day of flexibility for the return flight:
    "flexdays": 3,
    //Search only departure on Saturday:
    "weekend": false,
    //Ultima data utile per il volo di partenza:
    "lastdate": "2023-12-1",
    //If true does not click on first flight to save info about return flight:
    "fastmode": true, 
    //Timeout in secords for skip scrape if element not found 
    "timeout": 10,
    //Class - NOT IMPLEMENTED 1.5
    "tclass": [
        "economy",
        "business",
        "first"
  ]
}
```
