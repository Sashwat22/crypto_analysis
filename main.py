# main.py
import sys
from db.database import get_connection
from services.analysis import get_data_from_db, decision_maker
from services.data_fetcher import fetch_and_store_crypto_data

if __name__ == '__main__':
    symbol = sys.argv[1]  # Ask comand line about a symbol
    

    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT DISTINCT symbol FROM crypto_prices')
    symbols = c.fetchall()
    conn.close()
    symbol_list = [symbol[0] for symbol in symbols]
    print(symbol_list)

    #if not add it, if so let em know
    if symbol not in symbol_list:
        fetch_and_store_crypto_data(symbol)
        print("Data fetched and stored for", symbol, "must wait 3 days for data collection")
    else:
        df = get_data_from_db(symbol)
        if(len(df) < 14):
            fetch_and_store_crypto_data(symbol)
            print("still collecting data on coin")
        else:
            decision, position_size, confidence = decision_maker(df, symbol, 100000)
            print(f"Decision for {symbol}: {decision}")
            if decision == "BUY":
                print(f"Position size to buy: {position_size:.2f} units with confidence {confidence:.2f}")
            elif decision == "SELL":
                print(f"Position size to sell: {position_size:.2f} units with confidence {confidence:.2f}")
            else:
                print(f"Hold the current position with confidence {confidence:.2f}")