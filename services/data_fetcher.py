import requests
from db.database import get_connection
           
API_URL = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD&api_key=49efe9fa73cb70826eaf73fa7b49c34d207e84300bfb8111cac1cbdcb258b414"

def fetch_and_store_crypto_data(symbols):
    result_string = ''.join(str(symbols).replace('[', '').replace(']', '').replace('\'', '').replace(' ', ''))
    url = API_URL.format(result_string)
    response = requests.get(url)
    data = response.json()['RAW']
    
    conn = get_connection()
    c = conn.cursor()

    for symbol in result_string.split(','):
        symbol_data = data[symbol]['USD']
        c.execute('''
            INSERT INTO crypto_prices (symbol, price, volume_24h, volume_24h_to, market_cap, circulating_supply, total_supply, transaction_volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, symbol_data['PRICE'], symbol_data['VOLUME24HOUR'], symbol_data['VOLUME24HOURTO'], symbol_data['MKTCAP'], symbol_data['SUPPLY'], symbol_data['TOTALVOLUME24H'], symbol_data['TOTALTOPTIERVOLUME24H']))

    conn.commit()
    conn.close()