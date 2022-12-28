import pandas as pd
import csv
import requests
from binance_funding_rate import funding_binance


# Send the GET request to the URL
response = requests.get('https://fapi.binance.com/fapi/v1/fundingRate?symbol')

# Parse the response as JSON
data = response.json()

# Get the list of tickers
tickers = [item['symbol'] for item in data]


# Open the CSV file in write mode
with open('my_file.csv', 'w', newline='') as csv_file:
    # Create a CSV writer object
    writer = csv.writer(csv_file)
    
    # Iterate over the elements in the list and write each one to the CSV file
    for item in tickers:
        writer.writerow([item])

# Update the ticker.csv file with the tickers with the most negative funding rates: 
def sort_funding_rates():
    length= len(tickers)
    coin=[]
    for i in range(length):
        coin+= funding_binance(f'{tickers[i]}')
        coinrates= coin.get_single_ticker_funding(f'{tickers[i]}')
        coinrates.to_csv('tickers.csv', mode='w', header=False)
    coinrates.sort_values(by=['fundingRate'], ascending=True).apply(lambda x: x*100)
    return print(coinrates)

sort_funding_rates()