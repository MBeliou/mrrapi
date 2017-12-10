#!/usr/bin/env python3
# Code for the mining rig rental API
# The idea is to serve through a flask python-anywhere for consumption in google sheets

import json
import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests


RIG_METHODS = [
    'list'
]

class api(object):
    def __init__(self):
        self._api_key = "2ffa0754242ab89607a986672e3f532ebd41c14c29cd6d1785c59b205ca97c13"
        self._api_secret = "feed83a2629f09418a53433705701f68a1bce13363896d8ef24d11c91200f9b0"
        self.uri = "https://www.miningrigrentals.com/api/v1/{}"

    @property
    def _nonce(self):
        return '{:.10f}'.format(int(time.time()*1000))

    def _signature(self, post_data):
        sign = hmac.new(self._api_secret.encode(), post_data.encode(), digestmod=hashlib.sha1).hexdigest()
        return sign

    def define_url(self, method):
        if method in RIG_METHODS:
            return "rig?method="+method
        else:
            raise EnvironmentError('Not implemented')

    def _post(self, param = {}):
        param.update({'nonce' : self._nonce})

        params = urlencode(param)
        sign = self._signature(params)
        url = self.uri.format(self.define_url(param['method']))

        
        headers = {'x-api-key': self._api_key,
                    'x-api-sign': sign}
        req = requests.post(url, param, headers = headers)
        return req.json()

    # -- CALLS --------------------------

    def rig_list(self, algo='scrypt'):
        # out ['name', 'rpi', 'maxhrs', 'price_hr', 'price', 'id', 'hashrate_nice', 'rating', 'minhrs', 'hashrate', 'status'])
        return self._post(param ={'method' : 'list', 'type' : algo})

    def rig_scrypt(self):
        return self._post(param={'method':'list', 'type' : 'scrypt'})
# hashimotog|neoscrypt|blake14s|hashimotos|x11evo|lyra2rev2|lbry|qubit|sia|lyra2re|yescrypt|m7m|scrypt|quark|nist5|blake256|x15|x13|x11|sha256|nscrypt

    # -- CUSTOM CALLS -----------------------------------
    def cheapest_rig_list(self, algo='scrypt', quantity=10):
        out = []
        rep = self.rig_list(algo)
        data = rep['data']['records']

        for i in range(quantity):
            out.append(data[i])
        return out

    def cheapest_rig(self, algo='scrypt', quantity=10):
        out = []
        rep = self.rig_list(algo)
        data = rep['data']['records']

        return data[0]