#!/usr/bin/env python3
#
# This is the entry of Silver Sprint project
# It crates a timer to start the trading thread
#
# Source code folders:
#     common.py   - Independent tools like http/https and checksum
#     strategy.py - trading strategies
#     okcoinCN.py - okcoin.cn APIs

import os
import sys
import time
import logging
import configparser

from common import *
from strategy import *
from okcoinCN import *

BASE_DIR = os.path.dirname(__file__)
CONF_FILE = os.path.join(BASE_DIR, 'config')
LOG_DIR = os.path.join(BASE_DIR, 'log')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def getConfig():
    dict = {}
    conf = configparser.ConfigParser()
    conf.read(CONF_FILE)

    for section in conf.sections():
        dict[section] = {}
        for option in conf.options(section):
            try:
                dict[section][option] = conf.get(section, option)
            except:
                print("Exception on %s %s" % (section, option))
                sys.exit(-1)
    return dict

if __name__ == "__main__":
    conf = getConfig()
    globConf = conf.pop('GLOBAL')

    globCon = True if globConf['showlog'].lower() == 'true' else False
    logger = getLogger('SILV', globConf['loglevel'],
                       file = os.path.join(LOG_DIR, 'silver.log'),
                       console = globCon)
    logger.info('Logging initiated within %s level.' % globConf['loglevel'])

    # start trading instances
    for inst, param in conf.items():
        loop = True
        con = True if param['showlog'].lower() == 'true' else False
        logger = getLogger('SILV.' + inst, param['loglevel'],
                           file = os.path.join(LOG_DIR, inst + '.log'),
                           console = not globCon and con)
        logger.info('Starting trade: ' + inst)
        logger.info('Trade description: ' + param['desc'])
        while loop:
            exchange = eval(param['exchange'])(param, logger)
            loop = eval(param['strategy'])(exchange, logger)
            logger.debug('Sleep 10 seconds...')
            time.sleep(10)
