# GoogleFlightsScraper 1.0

Scraper di voli per GoogleFlights.
Permette la ricerca dei prezzi e le informazioni sui voli andata e ritorno data una lista di aeroporti di partenza ed una lista di aeroporti di destinazione. È necessario selezionare il primo giorno utile per la partenza ed il totale dei giorni prima del volo di ritorno. Tutti gli altri parametri sono opzionali.

## Esempio parametri di default

```json
{
    //Codici degli aeroporti degli aeroporti di partenza
    "from": [
          "FCO",
          "NAP"
    ],
    //Codici degli aeroporti degli aeroporti di destinazione
    "to": [
          "MED",
          "BOG",
          "CTG"
    ],
    //Prima data utile per la partenza:
    "outbound": "2023-10-1",
    //Numero di giorni:
    "delta": 20,
    //Giorni flessibili per il ritorno:
    "flexdays": 3,
    //Ultima data utile per la partenza:
    "lastdate": "2023-12-1",
    //Se true non prende informazioni riguardo la durata e le fermate del volo di ritorno:
    "fastmode": true, 
    //Timeout elemento non trovato tra una ricerca e l'altra
    "timeout": 10,
    //Classe - NON GESTITO 1.0:
    "tclass": [
        "economy",
        "business",
        "first"
  ]
}
```

## Funzionamento

Facendo riferimento all'esempio sopra riportato l'applicazione effettuerà questo tipo di ricerca:

Proverà tutte le combinazioni dalla lista di aeroporti di partenza "from" alla lista di aeroporti di destinazione "to", con un intervallo di 20 giorni ("delta") tra il volo di andata ("outbound") ed il volo di ritorno ("inbound_"). Flessibile sul ritorno di +3 giorni ("flexdays"). Lo script si ferma quando tutte le combinazioni tra date e aeroporti sono terminate oppure se la data di partenza dell'ultima combinazione della lista di aeroporti è uguale a "lastdate".

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)