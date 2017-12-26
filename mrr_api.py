 #!/usr/bin/env python3


'''
                The mrr_api module
================================================

    Python wrapper for the mining rig rental website API
    https://www.miningrigrentals.com/apidoc

     .. warning :: The miningrigrental API only returns errors for connection /
     signature errors. All other failures seem to result in false positive with
     Null values.

     .. note :: ALGOS is only given as information, methods don't check if a
     given algo is actually listed.
                    
'''

import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests


RIG_METHODS = ['list', 'detail', 'update', 'rent']

RENTAL_METHODS = ['detail']

ACCOUNT_METHODS = ['myrigs', 'myrentals', 'balance', 'pools', 'profiles']

ALGOS = [ 'scrypt', 'sha256', 'x11', 'lbry', 'hashimotos', 'groestl',
 'equihash', 'lyra2re', 'qubit', 'cryptonote', # myriad-groestl, # yescript,
 'nscrypt', 'neoscrypt', 'nist5', 'pluck', 'quark', 'timetravel10',
 'scryptjane', 'sha3', 'whirlpoolx', 'm7m', 'x13', 'x14', 'x15', 'blake2s',
 'blake256', 'lyra2rev2', 'lyra2z', 'sia', 'x17', 'c11', 'skunk', 'hashimotog',
 'hmq1725' ]

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

        elif method in RENTAL_METHODS:
            return "rental?method="+method

        elif method in ACCOUNT_METHODS:
            return "account?method="+method

        else:
            raise NotImplementedError('Method {} is not implemented'.format(method))

    def _post(self, **kwargs):
        """
            Creates the url for the call as well as the payload and headers

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

    def rig_list(self, algo, **kwargs):
        '''
            Gets the list of rigs
            :param algo: algorithm of interest

            :optional min_hash: minimum hashrate in MH
            :optional max_hash: maximum hashrate in MH
            :optional min_cost: minimum price per MH
            :optional max_cost: maximum price per MH
            :optional showoff: yes/no - show offline rigs - by default = no
            :optional order: orders response by price/hashrate/minhrs/maxhrs/rating/name
            :optional orderdir: requires order - orders by asc/desc
            :optional page: 1-# - results of a given page
        '''
        return self._post(method='list', type=algo, **kwargs)

    def rig_detail(self, id):
        '''
            Returns the details of a rig

            :param: id - rig id
        '''
        return self._post(method='detail', id=id)

    # -- RENTAL RELATED CALLS ---------------------------

    def my_rigs(self):
        '''
            Returns your rigs
        '''
        return self._post(method='myrigs')

    def my_rentals(self):
        '''
            Returns your rentals
        '''
        return self._post(method='myrentals')

    def rental_details(self, id):
        '''
            Returns the details of a given rental
            :param id: id of the rig
        '''
        return self._post(method='detail', id=id, is_rental=True)

    def update_rig(self, id, name=None, status=None, hashrate=None,
                    hash_type=None, price=None, min_hours=None, max_hours=None):
        '''
            Updates the details of one of your rigs - Requires the ID and at least one more argument
            :param id: id of the rig

            :optional name: new name of the rig
            :optional status: available/disabled
            :optional hashrate: defaults to MHash (eg: 10 = 10 MHash)
            :optional hash_type: used with 'hashrate' - Replaces the hashrate factor (kh, mh, gh, th)
            :optional price: price in BTC per mhash per day
            :optional min_hours: minimum rental length
            :optional max_hours: maximum rental length
        '''
        kwargs = locals()

        kwargs.pop('self')
        kwargs = {k:v for k, v in kwargs.items() if v is not None}
        if len(kwargs) == 1:
            raise ValueError("This method requires id and at least 1 more argument to be used")
        else:
            return self._post(method='update', **kwargs)

        def rent(self, id, length, profileid):
            '''
                Rents a rig
                :param id: id of the rig
                :param length: length in hours of the rental
                :param profileid: profile id - # pulled from the account profiles method
            '''
            return self._post(method='rent', length=length, profileid=profileid)

    # -- ACCOUNT RELATED CALLS --------------------------
    def get_balance(self):
        '''
            Returns the confirmed / unconfirmed BTC balance of the account

            .. note :: apidocs don't mention LTC or ETH
        '''
        return self._post(method='balance')

    def favorite_pools(self):
        ''' 
            Returns the account listed favorite pools

        :Example:
        >>> from mrr_api import MrrApi
        >>> app  = MrrApi(apikey, apisecret)
        >>> app.favorite_pools()
         {'success': True, 'data': [{'workername':
         'MjiJVx588Phk3hzrzyiiCRShSXAEtxKP6i', 'port': '3003',
         'host':'magnetpool.io', 'name': 'magnet500', 'id': 95497, 'password':
         ''}, 'version': '1'} 
         
         .. note: Also returns further informations about the pool, see example
        '''
        return self._post(method='pools')

    def profiles(self):
        '''
            Returns the account saved profiles

            :rtype: list of profiles
        '''
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
