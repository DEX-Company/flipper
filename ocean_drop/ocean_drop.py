"""

    Ocean Drop Class

"""

import os
import hashlib
import logging
import math
import secrets
import json

from web3 import Web3

from starfish import Ocean
from starfish.agent import (
    SurferAgent,
    SquidAgent,
)
from starfish.asset import (
    FileAsset,
    RemoteAsset,
)

logger = logging.getLogger(__name__)

BYTES_PER_KB = 1000


class OceanDrop:
    def __init__(self, config):
        self._config = config
        self._ocean = None
        self._squid_agent = None
        self._surfer_agent = None


    def publish(self, drop_path):
        if self.connect():
            found_file_list, new_listing_list, new_file_list = self.sync(drop_path)
            if new_file_list:
                for file_item in new_file_list:
                    logger.info(f'publishing file {file_item["filename"]}')
                    self.publish_file(file_item['filename'], file_item['md5_hash'])


    def consume(self, drop_path):
        if self.connect():
            found_file_list, new_listing_list, new_file_list = self.sync(drop_path)
            if new_listing_list:
                for listing in new_listing_list:
                    self.consume_asset(listing, drop_path)

    def connect(self):
        self._ocean = Ocean(
            keeper_url=self._config.keeper_url,
            contracts_path=self._config.contracts_path,
            gas_limit=self._config.gas_limit,
            log_level=logging.WARNING
        )
        self._squid_agent = SquidAgent(self._ocean, self._config.squid_agent)

        ddo_options = None
        ddo = SurferAgent.generate_ddo(self._config.surfer_agent['url'], ddo_options)
        options = {
            'url': self._config.surfer_agent['url'],
            'username': self._config.surfer_agent['username'],
            'password': self._config.surfer_agent['password'],
        }
        self._surfer_agent = SurferAgent(self._ocean, did=ddo.did, ddo=ddo, options=options)

        return self._ocean, self._squid_agent, self._surfer_agent

    def sync(self, drop_path):
        file_list = []
        total_size = 0
        file_list, total_size = OceanDrop.get_file_list(drop_path, file_list, total_size)
        total_size_text = OceanDrop.show_size_as_text(total_size)
        logger.info(f' found {len(file_list)} files with a total size of {total_size_text}')

        listing_list = self.get_valid_listings()
        found_file_list, new_listing_list, new_file_list = self.sync_list(listing_list, file_list)
        logger.debug(f' found {len(found_file_list)} new to consume {len(new_listing_list)} new to publish {len(new_file_list)}')
        return found_file_list, new_listing_list, new_file_list

    def publish_file(self, filename, file_hash):

        listing_data = self.generate_listing_data(file_hash)

        # save the asset file to surfer
        asset_store = FileAsset(filename=filename)
        listing_store = self._surfer_agent.register_asset(asset_store, listing_data)

        # now upload to the storage
        self._surfer_agent.upload_asset(asset_store)

        publisher_account = self._ocean.get_account(self._config.publisher_account)
        download_link = asset_store.did
        asset_sale = RemoteAsset(url=download_link)
        listing = self._squid_agent.register_asset(asset_sale, listing_data, publisher_account)
        return listing

    def auto_topup_account(self, account, min_ocean_balance, topup_ocean_balance, min_ether_balance, topup_ether_balance, faucet_url):
        if account.ocean_balance < min_ocean_balance:
            logger.info(f'current balance is {account.ocean_balance}, so auto topup of ocean balance')
            account.unlock()
            account.request_tokens(topup_ocean_balance)

    def consume_asset(self, listing):
        consumer_account = self._ocean.get_account(self._config.consumer_account)
        self.auto_topup_account(consumer_account, 
            int(self.config.account_topup['minimum_ocean_balance']),
            int(self.config.account_topup['topup_ocean_balance']),
            int(self.config.account_topup['minimum_ether_balance']),
            int(self.config.account_topup['topup_ether_balance']),
            self.config.account_topup['faucet_url']),            
        )
        purchase = listing.purchase(consumer_account)
        if not purchase.is_completed:
            purchase.wait_for_completion()

        if purchase.is_purchase_valid:
            purchase_asset = purchase.consume_asset
            surfer_did, asset_id = self._surfer_agent.decode_asset_did(purchase_asset.url)
            download_url = self._surfer_agent.get_asset_store_url(asset_id)
            new_asset_store = self._surfer_agent.download_asset(asset_id, download_url)

    def get_valid_listings(self):
        result = []
        search_filter = {
            'tags': [self._config.asset['tag']]
        }
        listing_items = self._squid_agent.search_listings(search_filter)
        for listing in listing_items:
            if self.is_listing_valid(listing):
                result.append(listing)
        return result

    def sync_list(self, listing_list, file_list):
        found_file_list = []
        new_listing_list = []
        new_file_list = []

        for listing in listing_list:
            is_found = False
            for file_item in file_list:
                if file_item['is_file']:
                    if self.is_listing_equal_to_file_item(listing, file_item['md5_hash']):
                        found_file_list.append((listing, file_item))
                        is_found = True
                        break
            if not is_found:
                new_listing_list.append(listing)

        for file_item in file_list:
            if file_item['is_file']:
                is_found = False
                for listing in listing_list:
                    if self.is_listing_equal_to_file_item(listing, file_item['md5_hash']):
                        is_found = True
                        break
                if not is_found:
                    new_file_list.append(file_item)
        return found_file_list, new_listing_list, new_file_list

    def is_listing_valid(self, listing):
        data = listing.data
        if data and 'extra_data' in data and 'nonce' in data['extra_data'] and 'valid_check' in data['extra_data']:
            nonce = data['extra_data']['nonce']
            checksum = self.generate_listing_checksum(nonce)
            return data['extra_data']['checksum'] == checksum
        return False

    def is_listing_equal_to_file_item(listing, file_hash):
        data = listing.data
        if data and 'extra_data' in data and 'file_hash' in data['extra_data']:
            return data['extra_data']['file_hash'] == file_hash
        return False

    def generate_listing_checksum(self, nonce):
        drop_secret = self._config.drop_secret
        return Web3.toHex(Web3.sha3(text=f'{nonce}{drop_secret}'))

    def generate_listing_data(self, file_hash):
        nonce = secrets.token_hex(32)
        checksum = self.generate_listing_checksum(nonce)
        data = {
            'name': self._config.asset['name'],
            'description': self._config.asset['description'],
            'author': self._config.asset['author'],
            'license': self._config.asset['license'],
            'price': self._config.asset['price'],
            'extra_data': json.dumps({
                'nonce': nonce,
                'checksum': checksum,
                'file_hash': file_hash,
            }),
            'tags': [self._config.asset['tag']],
        }
        return data

    @staticmethod
    def get_file_list(folder, file_list, total_size):
        logger.info(f'Scanning folder {folder}')
        for root, dirs, files in os.walk(folder):
            if len(files) == 0 and len(dirs) == 0:
                stat = os.lstat(root)
                file_list.append({'mtime': stat.st_mtime, 'folder':root, 'size': 0, 'is_file': False} )
            for file in files:
                filename = os.path.join(root, file)
                stat = os.lstat(filename)
                md5_hash = OceanDrop.hash_file(filename)
                total_size = total_size + stat.st_size
                file_list.append({'mtime': stat.st_mtime, 'filename': filename, 'folder':root, 'size': stat.st_size, 'is_file': True, 'md5_hash': md5_hash} )

        file_list = sorted(file_list, key = lambda k:k['mtime'])
        return (file_list, total_size)

    @staticmethod
    def hash_file(filename):
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def show_size_as_text(size):
        result = f'{size} Bytes'
        items = [
            (BYTES_PER_KB, 'KB'),
            (math.pow(BYTES_PER_KB, 2), 'MB'),
            (math.pow(BYTES_PER_KB, 3), 'GB'),
            (math.pow(BYTES_PER_KB, 4), 'TB'),
        ]

        for item in items:
            if size < item[0]:
                break
            format_size = size / item[0]
            result = f'{format_size:.2f} {item[1]}'

        return result
