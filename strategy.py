# This file impliments various trading strategies
# - 50-50 dynamic re-balanced
# - Grid trading
# - Get BTC price

from common import *

# https://xueqiu.com/3483147395/62338841
def halfBalanced(subject, param, logger):
    result = {}
    MIN_BTC = 0.01
    
    # get data
    info = subject.getAccount()
    price = subject.getSpotQuote()

    # check signal
    total = info['cny'] / price['last'] + info['btc']
    if info['btc'] < total / 2:
        logger.info('Need buy %.4f BTC, threashold %.2f'
                    % (abs(info['btc'] - total / 2), MIN_BTC))
    else:
        logger.info('Need sell %.4f BTC, threashold %.2f'
                    % (info['btc'] - total / 2, MIN_BTC))

    if abs(info['btc'] - total / 2) < MIN_BTC: # do nothing
        result['result'] = True
        logger.debug('Does not reach threashold, do nothing')
    else: # send out trade
        result = subject.tradeMarketPrice('btc_cny', \
                                          info['btc'] - total / 2, \
                                          price['last'])
        logger.info('Trading completed, result %r', result)
    return result

# Grid trading
# delta * depth * 2 <= (movement in last x days)
# unit * depth * 2 <= (total usable assets in RMB)
def gridTrading(subject, param, logger):
    # collect parameters
    delta = float(param['delta'])
    cnyUnit = float(param['netunit'])
    depth = int(param['netdepth'])
    losser = float(param['stoploss'])
    # get accout information
    info = subject.getAccount()
    price = subject.getSpotQuote()
    total = info['cny'] / price['last'] + info['btc']
    logger.info('Account info: CNY %.2f, BTC %.4f, TOTAL CNY %.2f'
                % (info['cny'], info['btc'], total * price['last']))
    # !!! STOP LOSS !!!
    if total * price['last'] <= losser:
        logger.critical('STOP LOSS AT total asset %.2f !!!'
                        % (total * price['last']))
        return False
    # initial trade
    try:
        base = param['base']
        # ! RESET GRID OF GRID !
        if abs(price['last'] - base) / delta > depth:
            logger.warning('Unilateral quotation happened ...')
            param['delta'] = str(delta + 1)
            logger.warning('Reset GRID with delta %s' % param['delta'])
            param.pop('orders')
        gridOrders = param['orders']
        logger.info('Order info: price drop in idx %d'% param['latest_index'])
        logger.debug('Order info: price drop in order %r'
                    % gridOrders[param['latest_index']])
    except KeyError: # First loop
        # Clear exist orders
        openOrders = subject.getOpenOrder('btc_cny', '-1')
        for order in openOrders:
            result = subject.cancelOrder('btc_cny', order['order_id'])
        # Setup position to 50/50
        gap = info['btc'] - total / 2
        base = price['last']
        subject.tradeMarketPrice('btc_cny', gap, price['last'])
        logger.info('Try to make up gap BTC %.4f' % gap)
        # Generate grid orders
        gridOrders = {}
        for idx in range(-depth, depth + 1):
            gridOrders[idx] = {}
            gridOrders[idx]['price'] = base + delta * idx
            gridOrders[idx]['orderId'] = 0
            gridOrders[idx]['status'] = -1
        param['orders'] = gridOrders
        param['base'] = base
        param['latest_index'] = 0
    # update order status if exist
    latest = param['latest_index']
    for idx, order in gridOrders.items():
        if order['orderId'] != 0:
            result = subject.getOpenOrder('btc_cny', order['orderId'])
            order['status'] = result[0]['status']
            # Get the latest trade, or the nearest grid to current price ?
            if order['status'] == 2 \
               and abs(order['price'] - price['last']) < \
                       abs(gridOrders[latest]['price'] - price['last']):
                logger.info('Index %d Closed, prev index %d' % (idx, latest))
                logger.debug('Prev idx %d , %r' % (latest, gridOrders[latest]))
                logger.debug('Curr idx %d , %r' % (idx, gridOrders[idx]))
                sqlLog().trade(int(time.time()),
                               result[0]['symbol'],
                               result[0]['type'],
                               result[0]['price'],
                               result[0]['deal_amount'])
                latest = idx
    # renew old orders or create if ID == 0
    for (idx, order) in gridOrders.items():
        if idx == latest:
            continue
        if order['orderId'] == 0 or order['status'] == 2:
            if price['last'] > order['price']:
                direction = 'buy'
            else:
                direction = 'sell'
            result = subject.tradeLimitPrice('btc_cny', direction,
                                             cnyUnit / price['last'],
                                             order['price'])
            if result['result']:
                order['orderId'] = result['order_id']
    param['latest_index'] = latest
    return True

# Get BTC price
def getPrice(subject, param, logger):
    conn = sqlLog()
    # get data
    info = subject.getAccount()
    price = subject.getSpotQuote()
    conn.price(price['date'], price['buy'], price['last'], price['sell'],
               price['vol'], info['cny'], info['btc'])
    logger.info('Price saved at %s'
                % datetime.datetime.fromtimestamp(price['date']).strftime('%c'))
    return True
