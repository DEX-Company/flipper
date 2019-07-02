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
        self.contracts_path = config.get('ocean', 'contracts_path')
        self.gas_limit = config.get('ocean', 'gas_limit')


        self.asset = {}
        self.asset['tag'] = config.get('asset', 'tag', 'health1b_asset_share')
        self.asset['author'] = config.get('asset', 'author', 'Ocean Drop Asset')
        self.asset['license'] = config.get('asset', 'lisence', 'closed')
        self.asset['description'] = config.get('asset', 'description', 'Not for public sale')
        self.asset['price'] = config.get('asset', 'price', '1')

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
            self.squid_config[item[0]] = item[1]

        items = config.items('surfer agent')
        self.surfer_agent = {}
        for item in items:
            self.surfer_config[item[0]] = item[1]
        
