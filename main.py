import pandas as pd
import sqlite3
import os
from sqlite3 import Error
from sqlalchemy import create_engine
from fundingrate.dydx_funding_rate import funding_dydx
from fundingrate.binance_funding_rate import funding_binance



def create_db(db_file):
        
    """ create SQLite database """
    if not os.path.isfile(db_file): 
    
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    
    else:
        print(db_file + ' already exists')        
        
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn
            
def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)



if __name__ == '__main__':
    
    #Set cronjob here with specific python environment
    #~/anaconda3/envs/quant/bin/python /home/jirong/Desktop/github/fundingrate/main.py   
    create_db(r"./funding_rate.db")
    
    database = "./funding_rate.db"    
    conn = create_connection(database)
    
    # create tables
    if conn is not None:
        sql_create_table = """ CREATE TABLE IF NOT EXISTS funding_rates (
                                market TEXT NOT NULL,
                                rate NUMERIC ,
                                price NUMERIC ,
                                date TEXT NOT NULL,
                                hour NUMERIC,
                                UNIQUE(market,date,hour)
                            ); """           
        create_table(conn, sql_create_table)
    else:
        print("Error! cannot create the database connection.")
    
    #Create engine      
    engine = create_engine('sqlite:///funding_rate.db', echo=False)           
    
    #Query data from database. As data grows limit to data after certain date
    full_data = pd.read_sql_query('SELECT * FROM funding_rates', con=engine)        
    full_data.columns = ['market', 'rate_db', 'price_db', 'date', 'hour']
      

    #Obtain data from API
    tickers = pd.read_csv('ticker.csv')
    ticker_list = tickers.ticker.to_list()
    #dydx = funding_dydx(['BTC-USD','ETH-USD','SOL-USD','ADA-USD'])    
    dydx = funding_dydx(ticker_list)    
    new_rates = dydx.get_formatted_funding_rates()       
    new_rates['date'] = new_rates['date'].astype(str)
    new_rates = new_rates.reset_index()
    new_rates = new_rates.drop('index', 1)
    
    #Left join db into queried data (change column new)
    df_to_be_inserted = pd.merge(new_rates, full_data, how='left',
                                 on=['market','date','hour']
                                 )
    
    df_to_be_inserted = df_to_be_inserted[pd.isnull(df_to_be_inserted['rate_db'])]
    df_to_be_inserted = df_to_be_inserted[['market', 'rate', 'price', 'date', 'hour']]
    
    #Insert null rows into database
    df_to_be_inserted.to_sql('funding_rates', con=engine, if_exists='append', index = False)  

