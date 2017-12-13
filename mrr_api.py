#!/usr/bin/env python3


'''
                The mrr_api module
================================================

    Python wrapper for the mining rig rental API
    https://www.miningrigrentals.com/apidoc

    .. todo :: Add remaining docstrings
               Write tests for connection
'''

import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests


RIG_METHODS = [
    'list',
    'detail',
    'update',
    'rent',
]

RENTAL_METHODS = [
    'detail'
]

ACCOUNT_METHODS = [
    'myrigs',
    'myrentals',
    'balance',
    'pools',
    'profiles'
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
            :return: Returns a value of time in ms - meeting the always increasing int pre-requisite
        '''
        return '{:.10f}'.format(int(time.time()*1000))

    def _signature(self, post_data):
        '''

            :param post_data: string data to be encoded
            :return: hmac sha1 encoded hexdigest of the post_data using the api_secret as key
        '''
        sign = hmac.new(self._api_secret.encode(), post_data.encode(), digestmod=hashlib.sha1).hexdigest()
        return sign

    def define_url(self, method, is_rental=False):
        '''
            Defines the url to be used

            :param method: rig or account method
            :return: Element to append to the uri

            :Example:

            define_url('myrentals', is_rental=True)

            .. note :: Method uses a is_rental Boolean to differenciate rig & rental 'detail' method
            .. raises :: Raises an error if the method is not yet implemented or does not exist
        '''
        if method in RIG_METHODS:
            return "rig?method="+method
        else:
            raise NotImplementedError('Method {} is not implemented'.format(method))

    def _post(self, **kwargs):
        """
            Turns the key word arguments into a dictionnary to be used to create the url for the call
            as well as the payload and headers

            :param **kwargs: requires at least method='name of method'
            :return: response to the request in a json format 

            :Example:

            _post(method='list', algo='scrypt')

        """
        param = kwargs
        param.update({'nonce' : self._nonce})
        try:
            rental = param.pop('is_rental')
        except:
            rental = False
        params = urlencode(param)
        
        sign = self._signature(params)

        url = self.uri.format(self.define_url(param['method'], rental))

        headers = {'x-api-key': self._api_key,
                   'x-api-sign': sign}

        req = requests.post(url, param, headers=headers)
        return req.json()

    # -- PUBLIC CALLS --------------------------

    def rig_list(self, algo='scrypt', **kwargs):
        return self._post(method='list', type=algo, **kwargs)

    def rig_detail(self, id):
        return self._post(method='detail', id=id)

    def rig_scrypt(self):
        return self._post(method='list', type='scrypt')

    # -- RENTAL RELATED CALLS ---------------------------
    def my_rigs(self):
        return self._post(method='myrigs')

    def my_rentals(self):
        return self._post(method='myrentals')

    def rental_details(self, id):
        return self._post(method='detail', id=id, is_rental=True)

    def update_rig(self, id, name=None, status=None, hashrate=None, hash_type=None, price=None, min_hours=None, max_hours=None):
        kwargs = locals()

        kwargs.pop('self')
        kwargs = {k:v for k,v in kwargs.items() if v is not None}
        if len(kwargs) == 1:
            raise ValueError("This method requires id and at least 1 more argument to be used")
        else:
            return self._post(method='update',**kwargs)

    # -- ACCOUNT RELATED CALLS --------------------------
    def get_balance(self):
        return self._post(method='balance')

    def favorite_pools(self):
        return self._post(method='pools')

    def profiles(self):
        return self._post(method='profiles')

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
