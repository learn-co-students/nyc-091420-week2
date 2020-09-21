import pandas as pd
import sqlite3
import os
import warnings
warnings.filterwarnings("ignore")
parent_directory = os.path.dirname(os.getcwd())


# ========================== CREATE TABLES =========================
print('Opening connection to database\n')
db_path = os.path.join(parent_directory, 'data', 'stocks.db')
conn = sqlite3.connect(db_path)

print('Creating date table.\n')
conn.execute('''DROP TABLE IF EXISTS date;''')
conn.execute('''
            CREATE TABLE date 
                (id INTEGER PRIMARY KEY,
                date DATE NOT NULL);''')

print('Creating company table.\n')
conn.execute('''DROP TABLE IF EXISTS company;''')
conn.execute('''
            CREATE TABLE company 
                (id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL UNIQUE);''')

print('Creating price table.\n')
conn.execute('''DROP TABLE IF EXISTS price;''')
conn.execute('''
            CREATE TABLE price (
                id INTEGER PRIMARY KEY,
                open DECIMAL,
                close  DECIMAL,
                company_id VARCHAR,
                date_id VARCHAR,
                CONSTRAINT company_id
                    FOREIGN KEY (company_id)
                    REFERENCES company(id)
                CONSTRAINT date_id
                    FOREIGN KEY (date_id)
                    REFERENCES date(id));''')

# ========================== IMPORT DATASET =========================

print('Loading data into SQL.\n')

stocks_dataset_path = os.path.join(parent_directory,'data','all_stocks_5yr.csv')
df = pd.read_csv(stocks_dataset_path)
df.date = pd.to_datetime(df.date)
df.sort_values(by='date', inplace=True)

# ========================= MOVE DATASET TO DB ===================

# DATE TABLE
df[['date']]\
    .drop_duplicates()\
    .to_sql('date', conn, index=False, if_exists='append')

# Collect date unique ids
dates = conn.execute('''select * from date''').fetchall()
date_map = {}
for date in dates:
    converted = pd.to_datetime(date[1])
    date_map[converted] = date[0]

# COMPANY TABLE
df[['Name']]\
    .drop_duplicates()\
    .to_sql('company', conn, index=False, if_exists='append')

# Collect company unique ids
companies = conn.execute('''select * from company''').fetchall()
company_map = {}
for company in companies:
    converted = company[1]
    company_map[converted] = company[0]

# OPEN TABLE
open_table = df[['open', 'close', 'date', 'Name']]
open_table['date_id'] = open_table.date.apply(lambda x: date_map[x])
open_table['company_id'] = open_table.Name.apply(lambda x: company_map[x])

open_table[['open', 'close', 'date_id', 'company_id']]\
    .to_sql('price', conn, 
            index=False, if_exists='append')