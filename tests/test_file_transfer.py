"""
    test_pd_case_file_transfer

    As a developer
    I want save an asset file on surfer, and sale the asset via squid,
    As a consumer
    I want to purchase an asset vi Ocean and download the asset from Sufer.

"""

import secrets
import logging
import json
import base64
import time

from starfish.asset import (
    DataAsset,
    RemoteDataAsset,
    BundleAsset
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def is_purchase_valid(did, agreement_id, publisher_account, consumer_account):
    logger.debug(f'is purchase allowed {did}, {agreement_id}, {publisher_account}, {consumer_account}')
    return True

def test_file_transfer(ocean, config, resources, surfer_agent, squid_agent):

    # take copy of the stored data to compare later
    with open(resources.asset_file, 'rb') as fp:
        store_data = fp.read()

    # save the asset file to surfer
    asset_store = DataAsset.create_from_file('FileAsset', resources.asset_file)
    listing_store = surfer_agent.register_asset(asset_store, resources.listing_data)
    assert(listing_store)

    # now upload to the storage
    surfer_agent.upload_asset(asset_store)

    # now register the asset link to surfer in squid
    download_account = ocean.get_account(config.download.account_address, config.download.account_password)

    # check to see if this account is hosted on the block chain node
    assert(download_account.is_hosted)

    download_link = asset_store.did
    resourceId = base64.b64encode(bytes(resources.asset_file)).decode('utf-8')

    asset_sale = RemoteDataAsset.create_with_url('LinkAsset', download_link, metadata={'resourceId': resourceId})
    # print('metadata ',squid_agent._convert_listing_asset_to_metadata(asset_sale, resources.listing_data))
    listing = squid_agent.register_asset(asset_sale, resources.listing_data, account=download_account)
    assert(listing)

    # now re-read the listing to make sure that we get the same result and listing data
    listing = squid_agent.get_listing(listing.listing_id)

    # now start the purchase part
    # setup the download account
    download_account = ocean.get_account(config.download.account_address, config.download.account_password)
    logging.info(f'download_account {download_account.ocean_balance}')
    download_account.unlock()
    # request the tokens to buy the asset
    download_account.request_tokens(10)

    # watch for purchasing events by the downloader below, and accept them
    squid_agent.start_agreement_events_monitor(download_account)

    # purchase the linked remote asset
    purchase = listing.purchase(download_account)
    assert(purchase)

    assert(not purchase.is_completed)

    # wait for completion of purchase
    purchase.wait_for_completion()

    # check to see if purchased
    assert(purchase.is_completed)
    assert(purchase.is_purchased)
    assert(purchase.is_purchase_valid)

    # get the purchased asset from squid
    purchase_asset = purchase.consume_asset
    assert(purchase_asset)
    # this is a bundle asset with a collection of remote assets
    assert(isinstance(purchase_asset, BundleAsset))

    # we are only using the first asset, so get it from the bundle
    remote_asset = purchase_asset.get_asset_at_index(0)
    assert(isinstance(remote_asset, DataAsset))


    #get the surfer_did and asset_id from the 'url'
    assert(remote_asset.metadata['url'])
    surfer_did, asset_id = surfer_agent.decode_asset_did(remote_asset.metadata['url'])
    assert(surfer_did)
    assert(asset_id)

    # get the actual URL of the surfer, and asset storage component
    download_url = surfer_agent.get_asset_store_url(asset_id)
    assert(download_url)

    # download the asset from storage
    new_asset_store = surfer_agent.download_asset(asset_id, download_url)
    assert(new_asset_store)
    assert(new_asset_store.is_asset_type('dataset'))

    # final check stored asset data is == to original data put up for sale
    assert(new_asset_store.data == store_data)

    # check the resource id in the purchased asset
    assert('resourceId' in remote_asset.metadata)
    asset_file_path = base64.b64decode(remote_asset.metadata['resourceId']).decode('utf-8')
    assert(str(resources.asset_file) == asset_file_path)
