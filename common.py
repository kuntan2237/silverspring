# This file includes standalone utilities
# - HTTP/HTTPS
# - MD5 signature
# - Get logger handler
# - Sqlite3 interface

import os
import http.client
import urllib
import json
import hashlib
import logging
import time
import datetime
import sqlite3

HTTP_TIMEOUT=10

def httpsGet(url, resource, params, logger):
    while True:
        try:
            conn = http.client.HTTPSConnection(url, timeout=HTTP_TIMEOUT)
            conn.request("GET", resource + '?' + params)
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            return json.loads(data)
        except:
            logger.error('Oops! HTTPS GET failed, retry after 30 seconds...')
            time.sleep(30)

def httpsPost(url, resource, params, logger):
    while True:
        try:
            headers = {
                "Content-type" : "application/x-www-form-urlencoded",
            }
            conn = http.client.HTTPSConnection(url, timeout=HTTP_TIMEOUT)
            temp_params = urllib.parse.urlencode(params)
            conn.request("POST", resource, temp_params, headers)
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            conn.close()
            return json.loads(data)
        except:
            logger.error('Oops! HTTPS POST, retry after 30 seconds...')
            time.sleep(30)

def signMd5(params, secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) + '&'
    data = sign + 'secret_key=' + secretKey
    return hashlib.md5(data.encode("utf8")).hexdigest().upper()
            
def getLogger(name, level, file='', console=False):
    logger = logging.getLogger(name)
    logLevel = eval('logging.' + level)
    logger.setLevel(logLevel)
    fmtr = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - ' +
                             '%(message)s', datefmt = '%Y-%m-%d %H:%M:%S')
    conFmtr = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - ' +
                                '%(message)s', datefmt = '%H:%M:%S')
    def handlerNotExists(handlers, type):
        if len(handlers) == 0: return True
        elif isinstance(handlers, type): return False
        else: return True

    if file and handlerNotExists(logger.handlers, logging.FileHandler):
        fh = logging.FileHandler(file)
        #fh.setLevel(logLevel)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmtr)
        logger.addHandler(fh)
    if console and handlerNotExists(logger.handlers, logging.StreamHandler):
        ch = logging.StreamHandler()
        ch.setLevel(logLevel)
        ch.setFormatter(conFmtr)
        logger.addHandler(ch)
    return logger

class sqlLog:
    def __init__(self):
        pass
    def __getDbFile(self):
        base_dir = os.path.dirname(__file__)
        date = datetime.date.today()
        return os.path.join(base_dir, 'data_' + date.strftime('%Y') + '.sqlite')
    def price(self, date, buy, last, sell, vol, my_cny, my_btc):
        conn = sqlite3.connect(self.__getDbFile())
        c = conn.cursor()
        # "alter table price add column my_cny real;"
        c.execute('CREATE TABLE IF NOT EXISTS price'
                  '(date integer, buy real, last real, sell real, vol real, '
                  'my_cny real, my_btc real)')
        c.execute('INSERT INTO price VALUES (?,?,?,?,?,?,?)',
                  (date, buy, last, sell, vol, my_cny, my_btc))
        conn.commit()
        conn.close()
    def trade(self, date, symbol, type, price, amount):
        conn = sqlite3.connect(self.__getDbFile())
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS trade '
                  '(date integer, symbol text, type text, '
                  'price real, amount real)')
        c.execute('INSERT INTO trade VALUES (?,?,?,?,?)',
                  (date, symbol, type, price, amount))
        conn.commit()
        conn.close()
