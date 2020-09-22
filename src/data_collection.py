import pandas as pd
import sqlite3

def stocks(year):
    conn = sqlite3.connect('../data/stocks.db')
    stocks = pd.read_sql(f'''
                  SELECT open,
                         close,
                         date,
                         name
                  FROM price
                  JOIN date
                  ON price.date_id = date.id
                  JOIN company
                  ON price.company_id = company.id
                  WHERE date BETWEEN 
                  date('{year}-01-01') and date('{year+1}-01-01')''', conn)
    
    stocks.date = pd.to_datetime(stocks.date)
    return stocks