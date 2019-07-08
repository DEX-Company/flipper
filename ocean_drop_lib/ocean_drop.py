"""

    Ocean Drop Class

"""

import os
import logging
import secrets
import json
import time
import base64
import re

from starfish import Ocean
from starfish.agent import (
    SurferAgent,
    SquidAgent,
)
from starfish.asset import (
    FileAsset,
    RemoteAsset,
)

from starfish.exceptions import StarfishAssetNotFound

from ocean_drop_lib.sync import Sync
from ocean_drop_lib.utils import (
    generate_listing_checksum,
    get_filename_from_metadata
)

logger = logging.getLogger('ocean_drop')

class OceanDrop:
    def __init__(self, config):
        self._config = config
        self._ocean = None
        self._squid_agent = None
        self._surfer_agent = None


    def publish(self, max_count=0, filter_name=None, dry_run=None):
        if self.connect():
            sync = Sync(self._ocean, self._squid_agent)
            sync.analyse(self._config.main.drop_path, self._config.main.drop_secret, self._config.main.search_tag)
            if sync.publish_list:
                counter = 0
                for file_item in sync.publish_list:
                    if filter_name is None or re.match(filter_name, file_item['filename']):
                        if dry_run:
                            logger.info(f'will publish file {file_item["filename"]}')
                        else:
                            logger.info(f'publishing file {file_item["filename"]}')
                            self.publish_file(file_item['filename'], file_item['md5_hash'], file_item['relative_filename'])
                        counter += 1
                        if counter >= max_count and max_count > 0:
                            break


    def consume(self, max_count=0, filter_name=None, dry_run=None):
        if self.connect():
            sync = Sync(self._ocean, self._squid_agent)
            sync.analyse(self._config.main.drop_path, self._config.main.drop_secret, self._config.main.search_tag)
            if sync.consume_list:
                counter = 0
                for listing in sync.consume_list:
                    filename = get_filename_from_metadata(listing.asset.metadata['base'])
                    if filter_name is None or re.match(filter_name, filename):
                        is_consume = False
                        if dry_run:
                            logger.info(f'will consume {filename}')
                            is_consume = True
                        else:
                            if self.consume_asset(listing, self._config.main.drop_path):
                                is_consume = True
                        if is_consume:
                            counter += 1
                            if counter >= max_count and max_count > 0:
                                break

    def process_payment_events(self):
        if self.connect():
            publish_account = self._ocean.get_account(self._config.publish.account_address, self._config.publish.account_password)
            self._squid_agent.watch_provider_events(publish_account)
            logger.info('wait for transaction to be started')
            while True:
                time.sleep(1)

    def topup(self):
        if self.connect():
            self.auto_topup_account

    def connect(self):
        self._ocean = Ocean(
            keeper_url=self._config.ocean.keeper_url,
            contracts_path=self._config.ocean.contracts_path,
            gas_limit=self._config.ocean.gas_limit,
            log_level=logging.DEBUG
        )

        self._squid_agent = SquidAgent(self._ocean, self._config.squid_agent.as_dict)

        ddo_options = None
        ddo = SurferAgent.generate_ddo(self._config.surfer_agent.url, ddo_options)
        options = {
            'url': self._config.surfer_agent.url,
            'username': self._config.surfer_agent.username,
            'password': self._config.surfer_agent.password,
        }
        self._surfer_agent = SurferAgent(self._ocean, did=ddo.did, ddo=ddo, options=options)

        return self._ocean, self._squid_agent, self._surfer_agent

    def publish_file(self, filename, file_hash, relative_filename):

        listing_data = self.generate_listing_data(file_hash, self._config.main.drop_secret)

        # save the asset file to surfer
        asset_store = FileAsset(filename=filename)
        listing_store = self._surfer_agent.register_asset(asset_store, listing_data)

        # now upload to the storage
        self._surfer_agent.upload_asset(asset_store)

        publish_account = self._ocean.get_account(self._config.publish.account_address, self._config.publish.account_password)
        download_link = asset_store.did

        resourceId = base64.b64encode(relative_filename.encode()).decode('utf-8')
        asset_sale = RemoteAsset(metadata={'resourceId': resourceId}, url=download_link)
        listing = self._squid_agent.register_asset(asset_sale, listing_data, publish_account)
        return listing

    def consume_asset(self, listing, drop_path):
        consume_account = self._ocean.get_account(self._config.consume.account_address, self._config.consume.account_password)
        self.auto_topup_account(consume_account)
        logger.info(f'purchasing asset {listing.listing_id}')
        try:
            purchase = listing.purchase(consume_account)
            if not purchase.is_completed:
                purchase.wait_for_completion()
        except StarfishAssetNotFound:
            logger.warn(f'Unable to find asset {listing.listing_id} on the network')
            return False

        if purchase.is_purchase_valid:
            purchase_asset = purchase.consume_asset
            surfer_did, asset_id = self._surfer_agent.decode_asset_did(purchase_asset.url)
            download_url = self._surfer_agent.get_asset_store_url(asset_id)
            asset_store = self._surfer_agent.download_asset(asset_id, download_url)
            filename = os.path.join(os.path.abspath(drop_path), asset_store.metadata['filename'])
            if 'resourceId' in purchase_asset.metadata:
                relative_filename = base64.b64decode(purchase_asset.metadata['resourceId']).decode('utf-8')
                filename = os.path.join(os.path.abspath(drop_path), relative_filename)
                folder = os.path.dirname(filename)
                if not os.path.exists(folder):
                    logger.info(f'creating folder {folder}')
                    os.makedirs(folder)
            logger.info(f'saving file to {filename}')

            # save the data
            # asset_store.save(filename)
            with open(filename, 'wb') as fp:
                fp.write(asset_store.data)

            return True
        return False

    def auto_topup_account(self, account):
        min_ocean_balance = int(self._config.auto_topup.min_ocean_balance)
        topup_ocean_balance = int(self._config.auto_topup.topup_ocean_balance)
        min_ether_balance = int(self._config.auto_topup.min_ether_balance)
        topup_ether_balasnce = int(self._config.auto_topup.topup_ether_balance)
        faucet_url = self._config.auto_topup.ether_faucet_url

        if account.ocean_balance < min_ocean_balance:
            logger.info(f'account {account.address} current balance is {account.ocean_balance} \
below the minimum allowed, so auto top up of account with ocean tokens')
            account.unlock()
            account.request_tokens(topup_ocean_balance)

    def generate_listing_data(self, file_hash, drop_secret):
        nonce = secrets.token_hex(32)
        checksum = generate_listing_checksum(nonce, drop_secret)
        data = {
            'name': self._config.asset.name,
            'description': self._config.asset.description,
            'author': self._config.asset.author,
            'license': self._config.asset.license,
            'price': self._config.asset.price,
            'extra_data': {
                'nonce': nonce,
                'checksum': checksum,
                'file_hash': file_hash,
            },
            'tags': [self._config.main.search_tag],
        }
        return data

    @property
    def get_sync(self):
        if self.connect():
            sync = Sync(self._ocean, self._squid_agent)
            sync.analyse(self._config.main.drop_path, self._config.main.drop_secret, self._config.main.search_tag)
            return sync
        return None
