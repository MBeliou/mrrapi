#!/usr/bin/env python3


'''
                The mrr_api module
================================================

    Python wrapper for the mining rig rental API

    .. todo :: Add remaining rigs methods
               Add remaining account methods
               Add remaining docstrings
               Write tests for connection
'''

import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests


RIG_METHODS = [
    'list',
]

ALGOS = [
    'scrypt',
    'sha256',
    'x11',
    'lbry',
    'hashimotos',
    'groestl',
    'equihash',
    'lyra2re',
    'qubit',
    'cryptonote',
    # myriad-groestl,
    # yescript,
    'nscrypt',
    'neoscrypt',
    'nist5',
    'pluck',
    'quark',
    'timetravel10',
    'scryptjane',
    'sha3',
    'whirlpoolx',
    'm7m',
    'x13',
    'x14',
    'x15',
    'blake2s',
    'blake256',
    'lyra2rev2',
    'lyra2z',
    'sia',
    'x17',
    'c11',
    'skunk',
    'hashimotog',
    'hmq1725'
]

class MrrApi(object):
    def __init__(self, api_key, api_secret):
        '''
            :param api_key: API key from the miningrigrental.com website
            :param api_secret: API secret from the miningrigrental.com website
        '''
        self._api_key = api_key
        self._api_secret = api_secret
        self.uri = "https://www.miningrigrentals.com/api/v1/{}"

    @property
    def _nonce(self):
        '''
            :return: Returns a value of time in ms
        '''
        return '{:.10f}'.format(int(time.time()*1000))

    def _signature(self, post_data):
        '''
            :param post_data: string data to be encoded
            :return: hmac sha1 encoded hexdigest of the post_data using the api_secret as key
        '''
        sign = hmac.new(self._api_secret.encode(), post_data.encode(), digestmod=hashlib.sha1).hexdigest()
        return sign

    def define_url(self, method):
        '''
            Defines the url to be used
            :param method: rig or account method
            :return: Element to append to the uri

            .. raises :: Raises an error if the method is not yet implemented or does not exist
        '''
        if method in RIG_METHODS:
            return "rig?method="+method
        else:
            raise EnvironmentError('Not implemented')

    def _post(self, **kwargs):
        param = kwargs
        param.update({'nonce' : self._nonce})

        params = urlencode(param)
        sign = self._signature(params)
        url = self.uri.format(self.define_url(param['method']))

        headers = {'x-api-key': self._api_key,
                   'x-api-sign': sign}
        req = requests.post(url, param, headers=headers)
        return req.json()

    # -- CALLS --------------------------

    def rig_list(self, algo='scrypt', **kwargs):
        # out ['name', 'rpi', 'maxhrs', 'price_hr', 'price', 'id', 'hashrate_nice', 'rating', 'minhrs', 'hashrate', 'status'])
        return self._post(method='list', type=algo, **kwargs)

    def rig_scrypt(self):
        return self._post(method='list', type='scrypt')

    # -- CUSTOM CALLS -----------------------------------
    def cheapest_rig_list(self, algo='scrypt', quantity=10, **kwargs):
        ''' ISSUES with ordering ? '''
        out = []
        rep = self.rig_list(algo, **kwargs)
        data = rep['data']['records']

        for i in range(quantity):
            out.append(data[i])
        return out

    def cheapest_rig(self, algo='scrypt'):
        rep = self.rig_list(algo)
        data = rep['data']['records']

        return data[0]
