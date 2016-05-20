# This file includes standalone utilities
# - HTTP/HTTPS
# - MD5 signature

import http.client
import urllib
import json
import hashlib


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
            
