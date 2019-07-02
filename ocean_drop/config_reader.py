"""

    Config Reader
"""
  

import os

from configparser import (
    ConfigParser,
    ExtendedInterpolation,
)

class ConfigReader():
    def read(self, filename):
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(filename)        
        self.network_url = config.get('main', 'network_url')
        self.drop_secret = config.get('main', 'drop_secret')
        
        
        self.drop_path = config.get('main', 'drop_path')
        self.keeper_url = config.get('ocean', 'keeper_url')
        self.contracts_path = config.get('ocean', 'contracts_path')
        self.gas_limit = config.get('ocean', 'gas_limit')


        self.asset = {}
        self.asset['tag'] = config.get('asset', 'tag', fallback='ocean_drop_share')
        self.asset['name'] = config.get('asset', 'name', fallback='Ocean Drop Asset')
        self.asset['author'] = config.get('asset', 'author', fallback='Ocean Drop Asset')
        self.asset['license'] = config.get('asset', 'lisence', fallback='closed')
        self.asset['description'] = config.get('asset', 'description', fallback='Not for public sale')
        self.asset['price'] = config.get('asset', 'price', fallback='1')

        self.publisher_account = {
            'address': config.get('publisher account', 'address'),
            'password': config.get('publisher account', 'password')
        }
        self.consumer_account = {
            'address': config.get('consumer account', 'address'),
            'password': config.get('consumer account', 'password')
        }

        items = config.items('squid agent')
        self.squid_agent = {}
        for item in items:
            self.squid_agent[item[0]] = item[1]

        items = config.items('surfer agent')
        self.surfer_agent = {}
        for item in items:
            self.surfer_agent[item[0]] = item[1]
        

        items = config.items('account topup')
        self.account_topup = {}
        for item in items:
            self.account_topup[item[0]] = item[1]
        
