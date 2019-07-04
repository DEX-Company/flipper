"""

    Config Reader
"""

import re
import os

from configparser import (
    ConfigParser,
    ExtendedInterpolation,
)

class ConfigSection():
    @property
    def as_dict(self):
        return self.__dict__

class ConfigReader():

    CONFIG_DEFINE = {
        'main': {
            'network_url': None,
            'drop_secret': None,
            'drop_path': None,
            'search_tag': 'ocean_drop_share',
        },
        'ocean': {
            'keeper_url': None,
            'contracts_path': 'articles',
            'gas_limit': 100000,
        },
        'asset': {
            'name':  'Ocean Drop Asset',
            'author': 'Ocean Drop Asset',
            'license': 'closed',
            'description': 'Not for public sale',
            'price': 1,
        },
        'publish': {
            'account_address': None,
            'account_password': None,
        },
        'consume': {
            'account_address': None,
            'account_password': None,
        },
        'squid agent': {
            'aquarius_url': '${main:network_url}:5000',
            'brizo_url': '${main:network_url}:8030',
            'secret_store_url': '${main:network_url}:12001',
            'parity_url': '${main:network_url}:8545',
            'storage_path': 'squid_py.db',
            'download_path': 'consume_downloads',
        },
        'surfer agent': {
            'url': '${main:network_url}:8080',
            'username': None,
            'password': None,
        },
        'auto topup': {
            'min_ocean_balance': 10,
            'min_ether_balance': 3,
            'topup_ocean_balance':  10,
            'topup_ether_balance': 3,
            'ether_faucet_url': 'https://faucet.${main:network_url}',
        },
    }



    def read(self, filename):
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(filename)


        for section_name, values in ConfigReader.CONFIG_DEFINE.items():
            object_name = re.sub(r'\s', '_', section_name)
            config_section = ConfigSection()
            setattr(self, object_name, config_section)
            for name, default_value in values.items():
                setattr(config_section, name, config.get(section_name, name, fallback=default_value))

