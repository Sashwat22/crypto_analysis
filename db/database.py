# database.py
import sqlite3

def get_connection(db_path='crypto_data.db'):
    return sqlite3.connect(db_path)

def create_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS crypto_prices (
            symbol TEXT,
            price REAL,
            volume_24h REAL,
            volume_24h_to REAL,
            market_cap REAL,
            circulating_supply REAL,
            total_supply REAL,
            transaction_volume REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
if __name__ == '__main__':
    create_table()

    

