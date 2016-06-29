# This file includes standalone utilities
# - HTTP/HTTPS
# - MD5 signature
# - Get logger handler

import http.client
import urllib
import json
import hashlib
import logging

HTTP_TIMEOUT=10

def httpsGet(url, resource, params=''):
    conn = http.client.HTTPSConnection(url, timeout=HTTP_TIMEOUT)
    conn.request("GET", resource + '?' + params)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    return json.loads(data)

def httpsPost(url, resource, params):
     headers = {
            "Content-type" : "application/x-www-form-urlencoded",
     }
     conn = http.client.HTTPSConnection(url, timeout=HTTP_TIMEOUT)
     temp_params = urllib.parse.urlencode(params)
     conn.request("POST", resource, temp_params, headers)
     response = conn.getresponse()
     data = response.read().decode('utf-8')
     params.clear()
     conn.close()
     return json.loads(data)

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
