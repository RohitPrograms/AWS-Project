import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def lambda_handler(event, context):
    
    # Connect to MySQL DB
    MySQL_connection = None
    
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            # Store somewhere else, this is public information you don't want to store anywhere.
            host = "your host here"
            user = "your username here"
            password = "your password here"
            MySQL_connection = mysql.connector.connect(user = user, password = password, host = host, database = 'name of your DB here')
            
            if MySQL_connection.is_connected():
                
                cursor = MySQL_connection.cursor()
                body = event.get('body')
                data = body.get('data')
                
                quote_time = data[next(iter(data))]['quote']['quoteTime']
                quote_time = datetime.fromtimestamp(quote_time // 1000)
       
                for symbol in data.keys():
        
                    bid = data[symbol]['quote']['bidPrice']
                    ask = data[symbol]['quote']['askPrice']
        
                    if data[symbol]['assetMainType'] == "FUTURE":
                        openInterest = data[symbol]['quote']['openInterest']
                        cursor.execute("INSERT INTO quotes (symbol, quoteTime, bidPrice, askPrice, openInterest) VALUES (%s, %s, %s, %s, %s)", (symbol, str(quote_time), bid, ask, openInterest))
                        MySQL_connection.commit()
                        print('Added Future')
                    
                    elif data[symbol]['assetMainType'] == "EQUITY":
                        cursor.execute("INSERT INTO quotes (symbol, quoteTime, bidPrice, askPrice) VALUES (%s, %s, %s, %s)", (symbol, str(quote_time), bid, ask))
                        MySQL_connection.commit()
                        print('Added Equity')
    
                MySQL_connection.close()
                break

        except Error as e:
            print(f'Error {e}')
            attempt += 1
    
    
        
