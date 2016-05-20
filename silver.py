#!/usr/bin/python
#
# This is the entry of Silver Sprint project
# It crates a timer to start the trading thread
#
# Source code folders:
#     common.py   - Independent tools like http/https and checksum
#     strategy.py - trading strategies
#     okcoinCN.py - okcoin.cn APIs

import sys
import time
import configparser

from common import *
from strategy import *
from okcoinCN import *

def usage():
    pass

def getConfig():
    dict = {}

    conf = configparser.ConfigParser()
    conf.read('./config')

    for section in conf.sections():
        dict[section] = {}
        for option in conf.options(section):
            try:
                dict[section][option] = conf.get(section, option)
            except:
                print("Exception on %s %s" % (section, option))
                sys.exit(-1)
    return dict

def initTrade(config):
    print("Initialize trades...")
    # init here

if __name__ == "__main__":
    conf = getConfig()
    initTrade(conf.pop('global'))

    # start trading instances
    for inst, param in conf.items():
        loop = True
        print("Trade Instance: " + inst)
        print("Description: " + param['desc'])
        while loop:
            exchange = eval(param['exchange'])(param)
            loop = eval(param['strategy'])(exchange)
            time.sleep(5)
