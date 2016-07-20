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

    # check status
    return True if result['result'] else False

# Grid trading
def gradTrading(subject, param, logger):
    result = {}
    MIN_BTC = 0.01
    try:
        top = float(param['top'])
        btm = float(param['bottom'])
        stop = float(param['stop'])
    except ValueError:
        logger.error('Incorrect top and bottom price, stop trade...')
        return False

    # get data
    info = subject.getAccount()
    price = subject.getSpotQuote()
    total = info['cny'] / price['last'] + info['btc']
    logger.info('Current CNY %.2f, BTC %.4f, total CNY %.2f'
                % (info['cny'], info['btc'], total * price['last']))

    # stop loss
    if total * price['last'] <= stop:
        logger.critical('STOP LOSS at %d !!!' % (total * price['last']))
        return True

    # check signal
    currPos = info['btc'] / total * 100
    expPos = (1 - (price['last'] - btm) / (top - btm)) * 100
    logger.debug('Current position %d%%, expect %d%%' % (currPos, expPos))
    expBtc = total * expPos / 100
    if info['btc'] < expBtc:
        logger.debug('Need buy %.4f BTC, threashold %.2f'
                    % (abs(info['btc'] - expBtc), MIN_BTC))
    else:
        logger.debug('Need sell %.4f BTC, threashold %.2f'
                    % (info['btc'] - expBtc, MIN_BTC))

    # trade
    if abs(info['btc'] - expBtc) < MIN_BTC:
        result['result'] = True
        logger.debug('Does not reach threashold, do nothing')
    else: # send out trade
        result = subject.tradeMarketPrice('btc_cny', \
                                          info['btc'] - expBtc, \
                                          price['last'])
        logger.info('Trading completed, result %r', result)

    # check status
    return True if result['result'] else False

# Get BTC price
def getPrice(subject, param, logger):
    conn = sqlLog()
    # get data
    price = subject.getSpotQuote()
    conn.price(price['date'], price['buy'], price['last'], price['sell'],
               price['vol'])
    logger.info('Current price saved.')
    return True
