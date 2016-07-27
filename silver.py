#!/usr/bin/env python3
#
# This is the entry of Silver Sprint project
# It crates a timer to start the trading thread
#
# Source code folders:
#     common.py   - Independent tools like http/https and checksum
#     strategy.py - trading strategies
#     okcoinCN.py - okcoin.cn APIs
#     config.example - an example of config file used by project

import os
import sys
import time
import logging
import configparser
import threading

from common import *
from strategy import *
from okcoinCN import *

TRADE_INTERVAL=30

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

class tradeThread (threading.Thread):
    def __init__(self, param, logger):
        threading.Thread.__init__(self)
        self.param = param
        self.logger = logger
    def run(self):
        self.logger.info('Trade started.')
        self.logger.info(self.param['desc'])

        # check stragety enabled flag
        if self.param['enable'].lower() != 'yes':
            self.logger.info('Strategy disabled by config file')
            rt = False
        else:
            rt = True

        while rt:
            exchange = eval(self.param['exchange'])(self.param, self.logger)
            rt = eval(self.param['strategy'])(exchange, self.param, self.logger)
            self.logger.debug('Sleep %d seconds...' % TRADE_INTERVAL)
            time.sleep(TRADE_INTERVAL)

        self.logger.info('Trade terminated.')

if __name__ == "__main__":
    conf = getConfig()
    globConf = conf.pop('GLOBAL')
    threads = []

    globCon = True if globConf['showlog'].lower() == 'true' else False
    logger = getLogger('SILV', globConf['loglevel'],
                       file = os.path.join(LOG_DIR, 'silver.log'),
                       console = globCon)
    logger.info('Logging initiated within %s level.' % globConf['loglevel'])

    # start trading instances
    for inst, param in conf.items():
        # setup stragety logs
        con = True if param['showlog'].lower() == 'true' else False
        tdLogger = getLogger('SILV.' + inst, param['loglevel'],
                           file = os.path.join(LOG_DIR, inst + '.log'),
                           console = not globCon and con)
        thread = tradeThread(param, tdLogger)
        thread.run()
        #thread.start()
        #threads.append(thread)

    # Wait for all threads to complete
    for t in threads:
        t.join()
    logger.info('ALL TRADING THREADS STOPPED!')
