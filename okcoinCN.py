# This file includes okcoin.cn APIs
# API: https://www.okcoin.cn/about/rest_api.do
# Error code : https://www.okcoin.cn/about/rest_request.do

from common import *

class okcoinCN:
    # Quotation
    __TICKER    = '/api/v1/ticker.do'
    # Transaction
    __USERINFO  = '/api/v1/userinfo.do'
    __TRADE     = '/api/v1/trade.do'
    __CNCLORDER = '/api/v1/cancel_order.do'
    __ORDERINFO = '/api/v1/order_info.do'

    def __init__(self, param, logger):
        self.__url = 'www.okcoin.cn'
        self.__apiKey = param['apikey']
        self.__secretKey = param['secretkey']
        self.__logger = logger

    def __API_ticker(self,symbol = ''):
        params=''
        if symbol:
            params = 'symbol=%(symbol)s' %{'symbol':symbol}
        return httpsGet(self.__url, self.__TICKER, params, self.__logger)

    def __API_userinfo(self):
        params ={}
        params['api_key'] = self.__apiKey
        params['sign'] = signMd5(params, self.__secretKey)
        return httpsPost(self.__url, self.__USERINFO, params, self.__logger)

    def __API_trade(self, symbol, tradeType, amount='', price=''):
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
        result = httpsPost(self.__url, self.__TRADE, params, self.__logger)
        if not result['result']:
            self.__logger.warning('Place order FAILED params %s, result %s'
                            % (params, result))
        return result
    
    def __API_orderinfo(self, symbol, orderId):
        params ={}
        params['api_key'] = self.__apiKey
        params['symbol'] = symbol
        params['order_id'] = orderId
        params['sign'] = signMd5(params, self.__secretKey)
        return httpsPost(self.__url, self.__ORDERINFO, params, self.__logger)

    def __API_cancelOrder(self, symbol, orderId):
        params ={}
        params['api_key'] = self.__apiKey
        params['symbol'] = symbol
        params['order_id'] = orderId
        params['sign'] = signMd5(params, self.__secretKey)
        return httpsPost(self.__url, self.__CNCLORDER, params, self.__logger)

    def getAccount(self):
        account = {}
        data = self.__API_userinfo()
        account['usd'] = 0.0
        for x in ['cny', 'btc', 'ltc']:
            account[x] = float(data['info']['funds']['free'][x]) \
                         + float(data['info']['funds']['freezed'][x])
        return account

    def getSpotQuote(self):
        quote = {}
        data = self.__API_ticker()
        quote['date'] = int(data['date'])
        for x in ['buy', 'sell', 'last', 'vol']:
            quote[x] = float(data['ticker'][x])
        return quote

    def tradeMarketPrice(self, symbol, amount, currPrice):
        if amount > 0:
            result = self.__API_trade(symbol, 'sell_market', amount)
            if result['result']:
                sqlLog().trade(int(time.time()), symbol,
                               'sell_market', '', amount)
        else:
            result = self.__API_trade(symbol, 'buy_market',
                                      price=abs(amount) * currPrice)
            if result['result']:
                sqlLog().trade(int(time.time()), symbol, 'buy_market',
                               abs(amount) * currPrice, '')
        self.__logger.debug('Trade %.2f with market price CNY %.2f, result %r'
                            % (amount, currPrice, result))
        return result['result']

    def tradeLimitPrice(self, symbol, direction, amount, price):
        result = self.__API_trade(symbol, direction, amount, price)
        self.__logger.info('Placed %s order %.2f with price CNY %.2f, result %r'
                           % (direction, amount, price, result['result']))
        return result

    def getOpenOrder(self, symbol, id):
        result = self.__API_orderinfo(symbol, id)
        if result['result']:
            return result['orders']
        else:
            return {}

    def cancelOrder(self, symbol, id):
        result = self.__API_cancelOrder(symbol, id)
        self.__logger.info('Cancel order ID: %d, result %r'
                           % (id, result['result']))
        return result['result']
