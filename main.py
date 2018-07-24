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
    print('BIDS' + '\t\t\t\t\t\t' + 'ASKS')
    print('QTY' + '\tRate' +'\t\tValue' + '\tExchange' + '\t' + 'QTY' + '\tRate' +'\t\tValue' + '\tExchange')

    blst=[]  #declare our bid list, which will hold tuples of data (quantity, rate, btc sum)
    alst=[] #declare out ask list
    fblst=[] #final aggregate bid list
    falst=[] #final aggregate ask list

# BITTREX LOGIC
# BID LOGIC
    bookData = simple_request('https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=buy')

    p = 0
    while p < 10:  # p < BID DEPTH 
        qty = bookData['result'][p]['Quantity']
        rate = bookData['result'][p]['Rate']
        tot = qty*rate
        exch = 'TREX'

        blst2=["%.2f" % qty, "%.8f" % rate, "%.4f" % tot, exch]  #a new list for the row of data (tuple)

        blst.append(blst2)  #add the list of data above as an element of the main list

        p += 1

# ASK LOGIC

    bookData = simple_request('https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=sell')

    p = 0
    while p < 10:  # p < BID DEPTH 
        qty = bookData['result'][p]['Quantity']
        rate = bookData['result'][p]['Rate']
        tot = qty*rate
        exch = 'TREX'

        alst2=["%.2f" % qty, "%.8f" % rate, "%.4f" % tot, exch]  #a new list for the row of data (tuple)

        alst.append(alst2)  #add the list of data above as an element of the main list

        p += 1



# BINANCE LOGIC
# BID LOGIC
    depth = client.get_order_book(symbol='LTCBTC', limit=10)

    r = 0
    while r < 10: # i < BID DEPTH
        bid = depth['bids'][r][0]
        qty = depth['bids'][r][1]
        bidz = float(bid)
        qtyz = float(qty)
        tot = bidz*qtyz
        exch = 'BINA'

        blst2=["%.2f" % qtyz, "%.8f" % bidz, "%.4f" % tot, exch]  #a new list for the row of data (tuple)

        blst.append(blst2)  #add the list of data above as an element of the final list
        r += 1

# ASK LOGIC

    depth = client.get_order_book(symbol='LTCBTC', limit=10)

    i = 0
    while i < 10: # i < ASK DEPTH
        ask = depth['asks'][i][0]
        qty = depth['asks'][i][1]
        askz = float(ask)
        qtyz = float(qty)
        tot = askz*qtyz
        exch = 'BINA'

        alst2=["%.2f" % qtyz, "%.8f" % askz, "%.4f" % tot, exch]  #a new list for the row of data (tuple)

        alst.append(alst2)  #add the list of data above as an element of the final list
        i += 1

    #Output Display - top 10 closest bids, sorted by Rate (price), total sum of bids at bottom
    counter = 0
    bidTotal = 0

    fblst = sorted(blst, key=lambda x: x[1], reverse=True)  #sort main list by price(rate), descending
    falst = sorted(alst, key=lambda x: x[1], reverse=False)  #sort main list by price(rate), ascending

    # old logic here
    counter = 0
    askTotal = 0

    for n,g in zip(fblst,falst):
        bidTotal = float(n[2]) + float(bidTotal)   # TOTAL VALUE OF BIDS WITHIN COUNTER RANGE - s[2] repesents the 3rd cell in each sub list - "tot"
        askTotal = float(g[2]) + float(askTotal)
        print("\t".join([str(i) for i in n]) + '\t\t' + "\t".join([str(i) for i in g]))
        counter += 1
        if counter >= 20:
            break

    print('Bid Total: ' + "%.4f" % bidTotal + ' BTC' + '\t\t\t\tAsk Total:' + "%.4f" % askTotal + ' BTC')


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
