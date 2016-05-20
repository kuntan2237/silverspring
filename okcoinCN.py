# This file includes okcoin.cn APIs
# API: https://www.okcoin.cn/about/rest_api.do
# Error code : https://www.okcoin.cn/about/rest_request.do

from common import *

class okcoinCN:
    # Quotation
    __TICKER   = '/api/v1/ticker.do'
    # Transaction
    __USERINFO = '/api/v1/userinfo.do'
    __TRADE    = '/api/v1/trade.do'

    def __init__(self, param):
        self.__url = 'www.okcoin.cn'
        self.__apiKey = param['apikey']
        self.__secretKey = param['secretkey']

    def __API_ticker(self,symbol = ''):
        params=''
        if symbol:
            params = 'symbol=%(symbol)s' %{'symbol':symbol}
        return httpsGet(self.__url, self.__TICKER, params)

    def __API_userinfo(self):
        params ={}
        params['api_key'] = self.__apiKey
        params['sign'] = signMd5(params, self.__secretKey)
        return httpsPost(self.__url, self.__USERINFO, params)

    def __API_trade(self, symbol, tradeType, amount, price=''):
        params = {
            'api_key' : self.__apiKey,
            'symbol' : symbol,
            'type' : tradeType
        }
        if price:
            params['price'] = price
        if amount:
            params['amount'] = "%.2f" % amount
            
        params['sign'] = signMd5(params, self.__secretKey)
        return httpsPost(self.__url, self.__TRADE, params)
    
    def getAccount(self):
        account = {}
        data = self.__API_userinfo()
        account['usd'] = 0.0
        for x in ['cny', 'btc', 'ltc']:
            account[x] = float(data['info']['funds']['free'][x] \
                               + data['info']['funds']['freezed'][x])
        return account

    def getSpotQuote(self):
        quote = {}
        data = self.__API_ticker()
        quote['date'] = int(data['date'])
        for x in ['buy', 'sell', 'last']:
            quote[x] = float(data['ticker'][x])
        return quote

    def tradeMarketPrice(self, symbol, amount):
        tradeType = 'sell_market' if amount > 0 else 'buy_market'
        result = self.__API_trade(symbol, tradeType, amount)
        return result
