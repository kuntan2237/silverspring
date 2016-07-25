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
    MIN_BTC = 0.01
    try:
        top = float(param['top'])
        btm = float(param['bottom'])
        prin = float(param['prin'])
        step = float(param['step'])
    except ValueError:
        logger.error('Incorrect parameters top/bottom/prin/step...')
        return False
    # get data
    info = subject.getAccount()
    price = subject.getSpotQuote()
    total = info['cny'] / price['last'] + info['btc']
    logger.info('Current CNY %.2f, BTC %.4f, total CNY %.2f'
                % (info['cny'], info['btc'], total * price['last']))
    # stop out of grid
    if price['last'] < btm or price['last'] > top:
        logger.warning('Stop trade at %.2f, out of grid %.2f ~ %.2f '
                       % (price['last'], btm, top))
        return True
    # initial trade, return if this is first check
    try:
        preStp = param['prevStep']
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
            result = subject.tradeMarketPrice('btc_cny', \
                                              info['btc'] - expBtc, \
                                              price['last'])
            logger.info('Trading completed, result %r', result)
        param['prevStep'] = curStp
        param['tdStp'] = round(prin * step / price['last'], 4)
        if param['tdStp'] < MIN_BTC:
            logger.critical('Unproper principle and steps, too concentrated.')
            return False
        else:
            return result
    # Check signal
    curStp = int((1 - (price['last'] - btm) / (top - btm)) / step)
    if curStp == preStp:
        return True
    logger.info('Trade grad %d -> %d' % (preStp, curStp))
    # Trade
    result = subject.tradeMarketPrice('btc_cny', (preStp - curStp) * tdBtc, \
                                      price['last'])
    logger.info('Trading completed, result %r', result)
    param['prevStep'] = curStp
    return result

# Get BTC price
def getPrice(subject, param, logger):
    conn = sqlLog()
    # get data
    info = subject.getAccount()
    price = subject.getSpotQuote()
    conn.price(price['date'], price['buy'], price['last'], price['sell'],
               price['vol'], info['cny'], info['btc'])
    logger.info('Current price saved.')
    return True
