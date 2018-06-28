# coding=utf-8
# Author: Winter_pig 2018-06-27


import ccxt
import time
from datetime import datetime
import math

#取消全部委托单
def CancelPendingOrders(exchange,symbol):
    now = datetime.now()
    orders = getOpenOrders(exchange,symbol)
    for order in orders:
        try:
            if ((now - timestamp_datetime(order['timestamp'])).seconds > 10):
                exchange.cancel_order(order['id'], symbol)
            else:
                continue
        except Exception as e:
            print("Cancel Error: {}".format(e))
        else:
            time.sleep(0.5)

#计算下单价格
def GetPrice(exchange,symbol):
    try:
        orderbook = exchange.fetchOrderBook(symbol)
        bid = orderbook['bids'][1][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][1][0] if len(orderbook['asks']) > 0 else None
        spread = (orderbook['asks'][0][0]  - orderbook['bids'][0][0])/2 if (bid and ask) else None
        print (exchange.id, 'market price', {'bid': bid, 'ask': ask, 'spread': spread})
        buy_price = bid + spread
        sell_price = ask - spread
        return buy_price, sell_price
    except Exception as e:
        print("GetPrice Error: {}".format(e))
    else:
        return None,None

def GetTickerPrice(exchange,symbol):
    try:
        #orderbook = exchange.fetchOrderBook(symbol)
        #bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        #ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        ticker = exchange.fetch_ticker(symbol)
        bid = ticker['bid']
        ask = ticker['ask']
        spread = (ask  - bid)/2 if (bid and ask) else None
        print (exchange.id, 'market price', {'bid': bid, 'ask': ask, 'spread': spread})
        return bid, ask, spread
    except Exception as e:
        print("GetPrice Error: {}".format(e))
    else:
        return None,None
#timestamp转换成日期
def timestamp_datetime(ts):
     if isinstance(ts, (int, float, str)):
         try:
             ts = int(ts)
         except ValueError:
             raise

         if len(str(ts)) == 13:
             ts = int(ts / 1000)
         if len(str(ts)) != 10:
             raise ValueError
     else:
        raise ValueError()
     return datetime.fromtimestamp(ts)

def my_create_limit_order(type, symbol, amount, price):
    if exchange.has['createLimitOrder']:
        if type == 'ORDER_TYPE_BUY' :
            myorder = exchange.create_limit_buy_order(symbol, amount, price)
            return myorder
        if type == 'ORDER_TYPE_SELL':
            myorder = exchange.create_limit_sell_order(symbol, amount, price)
            return myorder
    else:
        return None

def getAccount(exchange):
    try:
        account = exchange.fetchBalance()
        return account
    except Exception as e:
        print("getAccount Error: {}".format(e))
    else:
        time.sleep(3)
        return getAccount(exchange)

def getOpenOrders(exchange, symbol):
    try:
        orders = None
        orders = exchange.fetchOpenOrders(symbol)
        return orders
    except Exception as e:
        print("getOpenOrders Error: {}".format(e))
    else:
        time.sleep(3)
        return getOpenOrders(exchange,symbol)

def adjustFloat(v) :
    return math.floor(v*100)/100

def onTick():
    account = getAccount(exchange)
    if( account == None):
        print('account is none')
        return
    orders = getOpenOrders(exchange,target)
    if( orders == None):
        print('orders is none')
        return
    #更新收益
    #if( LastOrdersLength <> None && LastOrdersLength <> len(orders) ):
    #    print("ha")

    LastOrdersLength = len(orders)

    buy_price, sell_price = GetPrice(exchange,target)
    print (exchange.id, 'My price', {'buy_price': buy_price, 'buy_price': sell_price})

    bid, ask, spread = GetTickerPrice(exchange, target)
    mid = adjustFloat(bid + spread)
    #numBuy = int(min(MaxNets / 2, (mid - bid) / Step,  account[symbolB]['free'] / bid / Lot))
    numBuy = int(min(MaxNets / 2,   account[symbolB]['free'] / bid / Lot))
    numSell = int(min(MaxNets / 2, account[symbolA]['free'] / Lot))
    num = max(numBuy, numSell)
    print (exchange.id, 'My Amount', {'numBuy': numBuy, 'numSell': numSell})

    ordersKeep = []
    queue = []
    for i in range(num):
        buyPrice = adjustFloat(mid - (i * Step))
        sellPrice = adjustFloat(mid + (i * Step))
        alreadyBuy = False
        alreadySell = False
        for j in range( len(orders) ):
            if (orders[j]['side'] == ORDER_TYPE_BUY) :
                if (math.fabs( float(orders[j]['price']) - buyPrice) < (Step / 2)) :
                    alreadyBuy = True
                    ordersKeep.append(orders[j]['id'])
            else:
                if (math.fabs(float(orders[j]['price']) - sellPrice) < (Step / 2)) :
                    alreadySell = True
                    ordersKeep.append(orders[j]['id'])

        if ((alreadyBuy == False) and (i < numBuy)) :
            queue.append([buyPrice, ORDER_TYPE_BUY])

        if ((alreadySell == False) and (i < numSell)) :
            queue.append([sellPrice, ORDER_TYPE_SELL])

    for i in range(len(orders)):
        keep = False
        for  j in range( len(ordersKeep)):
            if (orders[i]['id'] == ordersKeep[j]) :
                keep = True

        if ( keep==False ):
            try:
                exchange.cancel_order(orders[i]['id'], target)
                LastOrdersLength = LastOrdersLength - 1
            except Exception as e:
                print("cancel_order Error: {}".format(e))


    for i in range( len(queue)):
        if (queue[i][1] == ORDER_TYPE_BUY) :
            try:
                exchange.create_limit_buy_order(target, Lot, queue[i][0])
            except Exception as e:
                print("create_limit_buy_order Error: {}".format(e))
        else :
            try:
                exchange.create_limit_sell_order(target, Lot, queue[i][0])
            except Exception as e:
                print("create_limit_sell_order Error: {}".format(e))

        LastOrdersLength  = LastOrdersLength + 1



ORDER_TYPE_BUY = 'buy'
ORDER_TYPE_SELL = 'sell'

#_______________________________________________
#_____________需要手工设置的参数__________________
#________________________________________________
#API的账户密码，后面把他移到外面的json串里去
exchange = ccxt.bitz({
    'apiKey': '446e725f166e40a22e37a4d54f7e8553',
    'secret': 'ROYKE93dipQ6C9LwySapZNeyJTn3zKcJ2UvEqeTJK2xrha5M7L8qG0zEN4kFpj3B',
})
exchange.password = '589621g'
exchange.verbose = True


symbolA = 'BTC'
symbolB = 'USDT'
target = symbolA + '/' + symbolB
LastOrdersLength = None

#网格交易参数
MaxNets = 20
Step = 0.02
Lot = 0.05

LoopInterval = 7
MinStock = 0.01


LoopInterval = max(LoopInterval, 1)
Lot = max(MinStock, Lot)

#检测一下该站点支持的API
exchange.describe()

while True:
    onTick()
    time.sleep(LoopInterval)


