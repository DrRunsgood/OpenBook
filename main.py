from binance.client import Client
import time
import requests
import hashlib
import hmac

TICK_INTERVAL = 60  # seconds


#TREX API INFO
API_KEY = 'my-api-key'
API_SECRET_KEY = b'my-secret-key'

#BINANCE API INFO
client = Client('API_KEY', 'API_SECRET_KEY')


def main():
    print('Starting trader bot...')

    while True:
        start = time.time()
        tick()
        end = time.time()

        # Sleep the thread if needed
        if end - start < TICK_INTERVAL:
            time.sleep(TICK_INTERVAL - (end - start))


def tick():
    print('Running routine')
    print('QTY' + '\tRate' +'\t\tValue' + '\tExchange')

    lst=[]  #declare our list, which will hold tuples of data (quantity, rate, btc sum)
    flst=[] #final aggregate list

# BITTREX LOGIC

    bookData = simple_request('https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=buy')

    p = 0
    while p < 10:  # p < BID DEPTH 
        qty = bookData['result'][p]['Quantity']
        rate = bookData['result'][p]['Rate']
        tot = qty*rate
        exch = 'TREX'

        lst2=["%.2f" % qty, "%.8f" % rate, "%.4f" % tot, exch]  #a new list for the row of data (tuple)

        lst.append(lst2)  #add the list of data above as an element of the main list

        p += 1


#BINANCE LOGIC    
        
    depth = client.get_order_book(symbol='LTCBTC', limit=10)

    i = 0
    while i < 10: # i < BID DEPTH
        bid = depth['bids'][i][0]
        qty = depth['bids'][i][1]
        bidz = float(bid)
        qtyz = float(qty)
        tot = bidz*qtyz
        exch = 'BINA'

        lst2=["%.2f" % qtyz, "%.8f" % bidz, "%.4f" % tot, exch]  #a new list for the row of data (tuple)

        lst.append(lst2)  #add the list of data above as an element of the final list
        i += 1

    #Output Display - top 10 closest bids, sorted by Rate (price), total sum of bids at bottom
    counter = 0
    bidTotal = 0

    flst = sorted(lst, key=lambda x: x[1], reverse=True)  #sort main list by price(rate), descending

    for s in flst:
        bidTotal = float(s[2]) + float(bidTotal)   # TOTAL VALUE OF BIDS WITHIN COUNTER RANGE - s[2] repesents the 3rd cell in each sub list - "tot"
        print("\t".join([str(i) for i in s]))
        counter += 1
        if counter >= 20:
            break

    print('Displayed Bid Total: ' + str(bidTotal))


def signed_request(url):
    now = time.time()
    url += '&nonce=' + str(now)
    signed = hmac.new(API_SECRET_KEY, url.encode('utf-8'), hashlib.sha512).hexdigest()
    headers = {'apisign': signed}
    r = requests.get(url, headers=headers)
    return r.json()

def simple_request(url):
    r = requests.get(url)
    return r.json()

def format_float(f):
    return "%.8f" % f

if __name__ == "__main__":
    main()
