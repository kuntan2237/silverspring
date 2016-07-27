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
def gradTrading(subject, param, logger):
    # collect parameters
    try:
        delta = float(param['delta'])
        cnyUnit = float(param['netunit'])
        depth = int(param['netdepth'])
        losser = float(param['stoploss'])
    except ValueError as e:
        logger.error('Incorrect parameters ... ' + e)
        return False
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
        btm = base - delta * depth
        top = base + delta * depth
        # ! PAUSE OUT OF GRID !
        if price['last'] < btm or price['last'] > top:
            logger.warning('Unilateral quotation happened ...')
            param.pop('grid')
        gridOrders = param['grid']
    except KeyError: # First loop
        # Setup position to 50/50
        gap = info['btc'] - total / 2
        subject.tradeMarketPrice('btc_cny', gap, price['last'])
        logger.info('Try to make up gap BTC %.4f' % gap)
        # Clear exist orders
        openOrders = subject.getOpenOrder('btc_cny', '-1')
        for order in openOrders:
            result = subject.cancelOrder('btc_cny', order['order_id'])
            logger.info('Cancel order ID: %d, result %r'
                        % (order['order_id'], result))
        # Generate grid orders
        gridOrders = {}
        for idx in range(-depth, depth + 1):
            gridOrders[idx] = {}
            gridOrders[idx]['price'] = base + delta * idx
            gridOrders[idx]['orderId'] = 0
            gridOrders[idx]['status'] = -1
        param['orders'] = gridOrders
        param['latest_index'] = 0
        return True
    # update order status if exist
    latest = param['latest_index']
    for (idx, order) in gridOrders:
        if order['orderId'] != 0:
            result = subject.getOpenOrder('btc_cny', order['orderId'])
            order['status'] = result['status']
            # Get the latest trade, or the nearest grid to current price ?
            if order['status'] == 2 \
               and abs(order['price'] - price['latest'] < \
                       abs(gridOrders[latest]['price'] - price['latest'])):
                latest = idx
    # renew old orders or create if ID == 0
    for (idx, order) in gridOrders:
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

'''
    # stop out of grid
    # initial trade, return if this is first check
    try:
        preStp = param['prevStep']
        prePrc = param['prevPrice']
        tdBtc = param['tdStp']
    except KeyError:
        logger.info('Initial position with top %.2f, bottem %.2f, '
                    'principle %.2f, step %.2f'
                    % (top, btm, prin, step))
        curStp = int((1 - (price['last'] - btm) / (top - btm)) / step)
        expBtc = (curStp * step) * prin / price['last']
        if info['btc'] < expBtc:
            logger.debug('Need buy %.4f BTC, threashold %.2f'
                         % (abs(info['btc'] - expBtc), MIN_BTC))
        else:
            logger.debug('Need sell %.4f BTC, threashold %.2f'
                         % (info['btc'] - expBtc, MIN_BTC))
        if abs(info['btc'] - expBtc) < MIN_BTC:
            result = True
            logger.debug('Does not reach threashold, do nothing')
        else: # send out trade
        param['prevStep'] = curStp
        param['prevPrice'] = top - curStp * stpPrc
        param['tdStp'] = round(prin * step / price['last'], 3)
        if param['tdStp'] < MIN_BTC:
            logger.critical('Unproper principle and steps, too concentrated.')
            return False
        else:
            return result
    # Check signal
    curStp = int((1 - (price['last'] - btm) / (top - btm)) / step)
    if curStp == preStp or abs(prePrc - price['last']) < stpPrc:
        return True
    # Trade
    logger.info('Trade grad %d -> %d price %.2f -> %.2f'
                % (preStp, curStp, prePrc, price['last']))
    result = subject.tradeMarketPrice('btc_cny', (preStp - curStp) * tdBtc, \
                                      price['last'])
    logger.info('Trading completed, result %r', result)
    if result:
        param['prevStep'] = curStp
        param['prevPrice'] = price['last']
    return result
'''
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
