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
        top = float(param['top'])
        btm = float(param['bottom'])
        asset = float(param['asset'])
        step = float(param['step'])
        stop = float(param['stop'])
        assetStep = (top - btm) * step
    except ValueError:
        logger.error('Incorrect parameters ...')
        return False
    # get accout information
    info = subject.getAccount()
    price = subject.getSpotQuote()
    total = info['cny'] / price['last'] + info['btc']
    logger.info('Current CNY %.2f, BTC %.4f, total CNY %.2f'
                % (info['cny'], info['btc'], total * price['last']))
    openOrders = subject.getOpenOrder('btc_cny', '-1')
    # !!! STOP LOSS !!!
    if price['last'] <= stop:
        logger.critical('STOP LOSS AT PRICE %.2f !!!' % price['last'])
        return False
    # ! PAUSE OUT OF GRID !
    if price['last'] < btm or price['last'] > top:
        logger.warning('PAUSE TRADE AT %.2f, OUT OF GRID %.2f ~ %.2f'
                       % (price['last'], btm, top))
        return True
    # initial trade
    try:
        gridOrders = param['grid']
    except KeyError: # First loop
        # Setup position
        gap = info['btc'] - (top - price['last']) / (top - btm) * total
        subject.tradeMarketPrice('btc_cny', gap, price['last'])
        logger.info('Try to make up gap BTC %.4f' % gap)
        # Clear exist orders
#        for order in openOrders:
#            result = subject.cancelOrder('btc_cny', order['order_id'])
#            logger.info('Cancel order ID: %d, result %r'
#                        % (order['order_id'], result))
        # Generate grid orders
        gridOrders = {}
        for idx in range(int(1 / step / 2), int(-1 / step / 2), -1):
            gridOrders[idx] = {}
            gridOrders[idx]['price'] = (top + btm) / 2 + assetStep * idx
            gridOrders[idx]['orderId'] = 0
            gridOrders[idx]['status'] = -1
        return True
    # Check and place grid orders
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
