from os import getenv
import datetime
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

API_KEY = getenv('API_KEY')

#base_url = f'https://financialmodelingprep.com/api/v4/income-statement-bulk?year=2024&period=quarter&apikey={API_KEY}'


todays_consts_url = f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={API_KEY}"
todays_consts = requests.get(todays_consts_url).json()
historical_consts_url = f"https://financialmodelingprep.com/api/v3/historical/sp500_constituent?apikey={API_KEY}"
historical_consts = requests.get(historical_consts_url).json()
todays_symbols = [i.get("symbol") for i in todays_consts]

dates = pd.date_range(end=datetime.date.today(), periods=365, freq="D")[::-1]

historical_symbols = {str(dates[0].date()): todays_symbols}
current_symbols = set(todays_symbols)


for date in dates[1:]:
    
    added_symbols = [
        i.get("symbol") for i in historical_consts if i.get('date') == str(date.date()) and i.get("addedSecurity") != ""
    ]
    removed_symbols = [
        i.get("removedTicker") for i in historical_consts if i.get('date') == str(date.date()) and i.get("removedSecurity") != ""
    ]
    
    if added_symbols:
        #print(date, 'added', added_symbols)
        current_symbols = current_symbols.difference(set(added_symbols))
        historical_symbols[str(date.date())] = current_symbols
        
    if removed_symbols:
        #print(date, 'removed', removed_symbols)
        current_symbols = current_symbols.union(set(removed_symbols))
        historical_symbols[str(date.date())] = current_symbols

all_tickers = set()
for symbols in historical_symbols.values():
    all_tickers = all_tickers.union(symbols)


print('all tickers', len(all_tickers))


r1 = pd.read_csv('src/2023_income_statement_quarter.csv')
r2 = pd.read_csv('src/2024_income_statement_quarter.csv')
r1 = r1.loc[:, ['symbol', 'fillingDate', 'calendarYear', 'period']]
r2 = r2.loc[:, ['symbol', 'fillingDate', 'calendarYear', 'period']]
r1 = r1.query("symbol in @all_tickers")
r2 = r2.query("symbol in @all_tickers")

r = pd.concat([r1, r2]).reset_index(drop=True)
