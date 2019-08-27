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
    DataAsset,
    RemoteDataAsset
)

from starfish.exceptions import StarfishAssetNotFound

from flipper.sync import Sync
from flipper.utils import (
    generate_listing_checksum,
    get_filename_from_metadata
)

from eth_account import Account

logger = logging.getLogger('flipper')

class Flipper:
    def __init__(self, config):
        self._config = config
        self._ocean = None
        self._squid_agent = None
        self._surfer_agent = None


    def upload(self, max_count=0, filter_name=None, dry_run=None):
        """

        Upload any new files that have not been registered on the Ocean Network.

        :param int max_count: Optional number of maximum record count to process for uploading. Default is set to 0 - no limit
        :param str filter_name: Optional name of the filter to use for the filename to upload.
        If specified then only search using the reg expression provided in the filter_name.

        :param bool dry_run: Optional flag to set if you wish to just run without adding any files or registering any assets.

        """
        if self.connect():
            # load in the sync data
            sync = Sync(self._ocean, self._squid_agent)
            # analyse the sync data for differences
            sync.analyse(self._config.main.drop_path, self._config.main.drop_secret, self._config.main.search_tag)
            if sync.upload_list:
                counter = 0
                # loop through each file in the upload list
                for file_item in sync.upload_list:
                    if filter_name is None or re.match(filter_name, file_item['filename']):
                        if dry_run:
                            logger.info(f'will upload file {file_item["filename"]}')
                        else:
                            logger.info(f'uploading file {file_item["filename"]}')
                            # do the actual upload for a file
                            self.upload_file(file_item['filename'], file_item['md5_hash'], file_item['relative_filename'])
                        counter += 1
                        if counter >= max_count and max_count > 0:
                            break


    def download(self, max_count=0, filter_name=None, dry_run=None):
        """

        Download any files that have been registered on the Ocean Network, but have not been
        purchased or downloaded.

        :param int max_count: Optional number of download assets to proces. Default is 0. No limit.
        :param str filter_name: Optional regular expression to filte on the filename. If set only file names matching
        filter_name will be downloaded. Default None - all files

        :param bool dry_run: Optional flag if True will only go through and process each download file, but will
        not buy or download the asset. Default None/False - No dry run.

        """
        if self.connect():
            sync = Sync(self._ocean, self._squid_agent)
            sync.analyse(self._config.main.drop_path, self._config.main.drop_secret, self._config.main.search_tag)
            if sync.download_list:
                counter = 0
                for listing in sync.download_list:
                    filename = "test"
                    # filename = get_filename_from_metadata(listing.asset.metadata['base'])
                    if filter_name is None or re.match(filter_name, filename):
                        is_download = False
                        if dry_run:
                            logger.info(f'will download {filename}')
                            is_download = True
                        else:
                            if self.download_asset(listing, self._config.main.drop_path):
                                is_download = True
                        if is_download:
                            counter += 1
                            if counter >= max_count and max_count > 0:
                                break

    def process_payment_events(self):
        """

        Process the payment events off the block chain. When a publisher/uploaded wants a consumer/downloader to
        purchase any assets. The publisher must have this process running and monitoring the block chain for purchase
        events.

        """
        if self.connect():
            upload_account = self._ocean.get_account(self._config.upload.account_address, self._config.upload.account_password)
            self._squid_agent.start_agreement_events_monitor(upload_account)
            logger.info('wait for transaction to be started')
            while True:
                time.sleep(1)

    def topup(self):
        """

        Run the auto topup process. This will only work for Test or Development Ocean Protocol Networks.
        Such as Nile or Spree

        """
        if self.connect():
            self.auto_topup_account

    def connect(self):
        """

        Connect to the Ocean Protocol Network.

        """

        # connect to the block chain node
        self._ocean = Ocean(
            keeper_url=self._config.ocean.keeper_url,
            contracts_path=self._config.ocean.contracts_path,
            gas_limit=self._config.ocean.gas_limit,
        )

        # connect to the squid agent
        self._squid_agent = SquidAgent(self._ocean, self._config.squid_agent.as_dict)

        # setup a dummy DDO, for normal live use, we can use the DID of Surfer which
        # will be registered on the block chain network.
        # If the DDO is registered we can then obtain the services provided by Surfer.
        ddo_options = None
        ddo = SurferAgent.generate_ddo(self._config.surfer_agent.url, ddo_options)
        options = {
            'url': self._config.surfer_agent.url,
            'username': self._config.surfer_agent.username,
            'password': self._config.surfer_agent.password,
        }

        # connect to surfer agent
        self._surfer_agent = SurferAgent(self._ocean, did=ddo.did, ddo=ddo, options=options)

        return self._ocean, self._squid_agent, self._surfer_agent

    def upload_file(self, filename, file_hash, relative_filename):
        """

        Upload a file to Surfer as the storage server, and register a new asset id using squid.

        :param string filename: Full path and name of the file to upload and register.
        :param string file_hash: Hash of the file contents.
        :param string relative_filename: Relative path and filename to the base folder.

        """

        # generate the listing to use for registration and upload
        listing_data = self.generate_listing_data(file_hash, self._config.main.drop_secret)

        # save the asset file to surfer
        asset_store = DataAsset.create_from_file('FileAsset', filename)
        listing_store = self._surfer_agent.register_asset(asset_store, listing_data)

        # now upload to the storage
        self._surfer_agent.upload_asset(asset_store)

        # get the account needed for registration.
        upload_account = self._ocean.get_account(self._config.upload.account_address, self._config.upload.account_password)
        download_link = asset_store.did

        # build the 'resourceId', which will be the relative path and filename
        resourceId = base64.b64encode(relative_filename.encode()).decode('utf-8')
        # create a remoet asset for registration
        asset_sale = RemoteDataAsset.create_with_url('LinkAsset', download_link, metadata={'resourceId': resourceId})
        # register the asset with squid agent
        listing = self._squid_agent.register_asset(asset_sale, listing_data, upload_account)
        return listing

    def download_asset(self, listing, drop_path):
        """

        Download an asset and save it to a sepcified path.

        :param listing: Listing object that contains the information needed to download and buy the asset.
        :param str drop_path: Base path of the destination to write the file too.

        :return bool: True if successfull in buying and saving an asset.

        """

        # get the download account to use.
        download_account = self._ocean.get_account(self._config.download.account_address, self._config.download.account_password)

        # check the account balance and maybe to an autotopup
        self.auto_topup_account(download_account)
        logger.info(f'purchasing asset {listing.listing_id}')
        try:
            # now try to purchase the asset
            purchase = listing.purchase(download_account)
            if not purchase.is_completed:
                # wait for the purchase process to complete
                purchase.wait_for_completion()
        except StarfishAssetNotFound:
            logger.warn(f'Unable to find asset {listing.listing_id} on the network')
            return False

        # if the purchase is complete, then we now need to download and save the file
        if purchase.is_purchase_valid:
            # mark the asset a 'consumed', so that the final payment is sent to the publisher, and
            # the asset details are decrypted.
            purchase_asset = purchase.consume_asset
            # get the first remote asset ( there will only be 1 )
            remote_asset = purchase_asset.get_asset_at_index(0)
            # get the 'url', in our case it's the full DID of the Surfer server and asset_id
            surfer_did, asset_id = self._surfer_agent.decode_asset_did(remote_asset.metadata['url'])

            # TODO: Resolve the `surfer_did` to the actual URL, at the moment we assume the URL is the same
            # as the local demo surfer URL. But later we will need to connect to  a new SurferAgent based on
            # it's DID

            # get the actual URL of the asset download from this surfer agent.
            download_url = self._surfer_agent.get_asset_store_url(asset_id)
            # now actually download the asset data from Surfer
            asset_store = self._surfer_agent.download_asset(asset_id, download_url)
            # calc the basic filename, writtern to the metadata
            filename = os.path.join(os.path.abspath(drop_path), get_filename_from_metadata(listing.ddo.metadata['base']))
            # if the resourceId is set, then we can get the correct filename and relative path
            if 'resourceId' in remote_asset.metadata:
                relative_filename = base64.b64decode(remote_asset.metadata['resourceId']).decode('utf-8')
                filename = os.path.join(os.path.abspath(drop_path), relative_filename)
                folder = os.path.dirname(filename)
                if not os.path.exists(folder):
                    logger.info(f'creating folder {folder}')
                    os.makedirs(folder)
            logger.info(f'saving file to {filename}')


            # save the data
            asset_store.save_to_file(filename)

            return True
        return False

    def account_add(self, password):
        """

        Create a new account

        TODO: Move this over to wallet-manager

        """
        if self.connect():
            account = self._ocean._web3.eth.account.create(password)
            key_file = Account.encrypt(account.privateKey, password)
            address = account.address
            # address = self._ocean.create_account(password)
            return key_file
        return None

    def account_list(self):
        """

        List the accounts on this node.

        TODO: Move this over to the wallet-manager

        """
        if self.connect():
            return self._ocean.accounts
        return None

    def auto_topup_account(self, account):
        """

        Auto topup an account. This is only available for test and development networks.

        :param account: Account that needs to check for topup. If below the specified amount
        defined in the config files, then topup by the config amount.

        """
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
            logger.info(f'account {account.address} current balance is now {account.ocean_balance}')

    def generate_listing_data(self, file_hash, drop_secret):
        """

        Generate the listing data for uploading and registering an asset.

        This is create metadata for the asset with a checksum that can be validated
        by the consumer/downloader process.

        """
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
        """

        Return the sync details for the current sync folder.

        :return sync: Sync object that has the sync details and lists of files to upload and download
        """
        if self.connect():
            sync = Sync(self._ocean, self._squid_agent)
            sync.analyse(self._config.main.drop_path, self._config.main.drop_secret, self._config.main.search_tag)
            return sync
        return None
