import schedule
import time
from db.database import get_connection
from services.data_fetcher import fetch_and_store_crypto_data

def job():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT DISTINCT symbol FROM crypto_prices')
    symbols = c.fetchall()
    conn.close()
    symbol_list = [symbol[0] for symbol in symbols]

    fetch_and_store_crypto_data(symbol_list)
    print("Data fetched and stored.")

# Setup the scheduler

schedule.every().day.at("00:00").do(job)
schedule.every().day.at("02:00").do(job)
schedule.every().day.at("04:00").do(job)
schedule.every().day.at("06:00").do(job)
schedule.every().day.at("08:00").do(job)
schedule.every().day.at("10:00").do(job)
schedule.every().day.at("12:00").do(job)
schedule.every().day.at("14:00").do(job)
schedule.every().day.at("16:00").do(job)
schedule.every().day.at("18:00").do(job)
schedule.every().day.at("20:00").do(job)
schedule.every().day.at("22:00").do(job)


if __name__ == '__main__':
    # Run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)
