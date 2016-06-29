# This file impliments various trading strategies
# - 50-50 dynamic re-balanced

# https://xueqiu.com/3483147395/62338841
def halfBalanced(subject, logger):
    result = {}
    MIN_BTC = 0.01
    
    # get data
    info = subject.getAccount()
    price = subject.getSpotQuote()

    # check signal
    total = info['cny'] / price['last'] + info['btc']
    if abs(info['btc'] - total / 2) < MIN_BTC: # do nothing
        logger.info('Balanced, need %.4f BTC, threashold %.2f'
                    % (info['btc'] - total / 2, MIN_BTC))
        result['result'] = True
    else: # send out trade
        logger.info('Trading, need %.4f BTC, threashold %.2f'
                    % (info['btc'] - total / 2, MIN_BTC))
        result = subject.tradeMarketPrice('btc_cny', \
                                          info['btc'] - total / 2, \
                                          price['last'])
        logger.info('Trading completed, result %r', result)

    # check status
    return True if result['result'] else False
