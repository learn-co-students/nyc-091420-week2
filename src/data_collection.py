import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup

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

def holiday_api(year):
    us_holidays = requests.get(f'https://date.nager.at/Api/v1/Get/US/{year}').json()
    dates = [pd.to_datetime(holiday['date']) for holiday in us_holidays]
    zipped = list(zip([holiday['name'] for holiday in us_holidays],dates))
    df = pd.DataFrame(zipped)
    df.columns = ['holiday_name', 'date']
    return df

    
def timeanddate(year):
    # Make request to website
    req = requests.get(f'https://www.timeanddate.com/holidays/us/{year}')

    # Parse html
    soup = BeautifulSoup(req.text, 'html')

    # Turn <table> div into dataframe
    df = pd.read_html(str(soup.find('table')))[0]
    df.columns = df.columns.droplevel(0)

    # Drop Day of week column
    df.drop('Unnamed: 1_level_1', axis=1, inplace=True)
    # Function for cleaning column names
    column_format = lambda x: x.lower().strip().replace(' ', '_')
    # Clean function names
    df.columns = [column_format(x) for x in df.columns]
    # Change `name` column to `holiday_name` for merging
    df.rename({'name': 'holiday_name'}, axis=1, inplace=True)
    # Drop last row in webscraped table because it's not needed
    df.drop(df.index[-1], inplace=True)
    # Reformat date data so it can be changed to datetime
    df.date = df.date + f', {year}'
    # Change to datetime
    df.date = pd.to_datetime(df.date)
 #   df = df[df['type'] != 'State holiday']
    # Drop details column. It is mostly null.
    df.drop('details', axis=1, inplace=True)
    return df


def stocks_and_holidays(year):
    '''Joining of all holiday data and stocks data'''
    # Data Collection
    scraped = timeanddate(year)
    sql = stocks(year)
    api = holiday_api(year)
    
    # Add types to api table
    api = api\
    .merge(scraped[['date', 'type']], 
           on=['date'], how='left')\
    [['date', 'holiday_name', 'type']]\
    .drop_duplicates('date')
    
    # Append api table to top of scraped table. 
    # Drop duplicates
    holidays = pd.concat([api, scraped]).drop_duplicates('date')
    
    # Left join sql --> holidays
    return sql.merge(holidays, on='date', how='left')