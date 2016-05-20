# This file impliments various trading strategies
# - 50-50 balanced

'''
def halfBalancedTrading(tradeParams):
    url = 'www.okcoin.cn'
    apikey = 'AAAAAA'
    secretKey = 'XXXXXX'
    target = okcoinSpot(url, apikey, secretKey)
    trans = halfHalfTrading()
    if trans.verify(target.userInfo()):
        target.trade(trans.trade())
        if trans.status():
            print('SUCCESS!')
        else:
            trans.cancel()

'''

# https://xueqiu.com/3483147395/62338841
def halfBalanced(subject):
    result = {}
    MIN_BTC = 0.01
    
    # get data
    info = subject.getAccount()
    price = subject.getSpotQuote()

    # check signal
    total = info['cny'] / price['last'] + info['btc']
    if abs(info['btc'] - total / 2) < MIN_BTC:
        # do nothing
        print("No trade - " + str(info['btc'] - total / 2))
        result['result'] = True
    else:
        # send out trade
        result = subject.tradeMarketPrice('btc_cny', \
                                          info['btc'] - total / 2)

    # check status
    return True if result['result'] else False
