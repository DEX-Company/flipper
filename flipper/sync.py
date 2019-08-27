"""

    Sync Class

    Sync between a folder and Ocean assets

"""

import logging

from flipper.utils import (
    read_file_list,
    show_size_as_text,
    generate_listing_checksum,
    get_filename_from_metadata,
)

logger = logging.getLogger('flipper.sync')

class Sync():
    def __init__(self, ocean, squid_agent):
        """

        Initialise the Sync object for loading sync information

        :param ocean: Ocean objet that contains the information for the Ocean Network
        :param squid_agent: Squid agent to get the asset listings registered.
        """
        self._ocean = ocean
        self._squid_agent = squid_agent
        self._file_list = []
        self._listing_list = []
        self._sync_file_list = []
        self._download_list = []
        self._upload_list = []
        self._download_file_list = []
        self._upload_file_list = []
        self._stats = {}


    def analyse(self, drop_path, drop_secret,  asset_tag):
        """

        Analyse and compare what is already available on the local folder and
        what assets are registered.

        :param str drop_path: Path of the files currently saved in the drop folder.
        :param str drop_secret: Secret text that both uploader and downloader share,
        so that we can make sure that both users will upload and download the same assets.

        :param str asset_tag: tag used to search the correct assets

        :return stats: Return the stats dict
        """
        self._file_list = []
        total_size = 0
        self._file_list, total_size = read_file_list(drop_path, self._file_list, total_size)
        file_count = 0
        for file_item in self._file_list:
            if file_item['is_file']:
                file_count += 1

        total_size_text = show_size_as_text(total_size)
        logger.debug(f' found {len(self._file_list)} files with a total size of {total_size_text}')

        self._listing_list = self.get_valid_listings(asset_tag, drop_secret)
        self.sync_lists()
        self._stats = {
            'file_count': file_count,
            'total_size': total_size,
            'sync_count': len(self._sync_file_list),
            'download_count': len(self._download_list),
            'upload_count': len(self._upload_list)
        }
        logger.debug(', '.join(self.stats_to_text_list))
        return self._stats

    def sync_lists(self):
        """

        Create a list of sync items that need to be uploaded and downloaded.

        """
        self._sync_file_list = []
        self._download_list = []
        self._upload_list = []
        self._download_file_list = []
        self._upload_file_list = []

        # scan through the registered assets
        for listing in self._listing_list:
            is_found = False
            for file_item in self._file_list:
                if file_item['is_file'] and file_item['size'] > 0:
                    if self.is_listing_equal_to_file_item(listing, file_item['md5_hash']):
                        # if both file in the folder and registered asset is the same
                        # then add to the _sync_file_list
                        self._sync_file_list.append((listing, file_item))
                        is_found = True
                        break
            if not is_found:
                # if the file in the folder is not found in the listing of registered
                # assets then add to the list of assets that can be downloaded
                self._download_list.append(listing)
                remote_asset = listing.asset.get_asset_at_index(0)
                filename = get_filename_from_metadata(listing.ddo.metadata['base'])
                self._download_file_list.append(filename)

        # now scan through all fo the local files
        for file_item in self._file_list:
            if file_item['is_file'] and file_item['size'] > 0:
                is_found = False
                for listing in self._listing_list:
                    if self.is_listing_equal_to_file_item(listing, file_item['md5_hash']):
                        # found the file on disk and also as a registered asset
                        is_found = True
                        break
                # now add the file to the to upload list, if not found as a registered asset
                if not is_found:
                    self._upload_list.append(file_item)
                    self._upload_file_list.append(file_item['relative_filename'])


    def get_valid_listings(self, asset_tag, drop_secret):
        """

        Return a list of valid listings for registered assets.

        :param str asset_tag: Text tag to search for a valid listing.
        :param str drop_secret: Text secret to validate the listing with, so that
        we know this has been registered by a valid uploader.

        :return: a list of listing objects

        """
        result = []
        search_filter = {
            'tags': [asset_tag]
        }
        listing_items = self._squid_agent.search_listings(search_filter)
        for listing in listing_items:
            if self.is_listing_valid(listing, drop_secret):
                result.append(listing)
        return result

    def is_listing_valid(self, listing, drop_secret):
        """

        Return True if the listing is a valid listing and has the same checksum
        created by using the same drop_secret.

        :Param object listing: The listing to check to see if it's valid.
        :param str drop_secret: The shared secret to use in calculating the checksum.

        :return: True if the listing is valid and created by the opposite uploader.

        """
        data = listing.data
        if data and 'extra_data' in data:
            extra_data = data['extra_data']
            if extra_data and 'nonce' in extra_data and 'checksum' in extra_data:
                nonce = extra_data['nonce']
                checksum = generate_listing_checksum(nonce, drop_secret)
                return extra_data['checksum'] == checksum
        return False

    def is_listing_equal_to_file_item(self, listing, file_hash):
        """
        Check to see if the listing is the same as the saved file on disk.

        :param object listing: Listing object to check.
        :param str file_hash: Hash of the file that we currently have no disk.

        :return: True if the hash on disk is the same as the hash saved in the listing.

        """
        data = listing.data
        logger.debug(f'{data}')
        if data and 'extra_data' in data:
            extra_data = data['extra_data']
            if extra_data and 'file_hash' in extra_data:
                return extra_data['file_hash'] == file_hash
        return False


    @property
    def stats_to_text_list(self):
        """

        Return the stats as a text string

        :return: Text string describing the sync stats.
        """
        total_space_text = show_size_as_text(self._stats['total_size'])
        result = [
            f'Total files: {self._stats["file_count"]}',
            f'Total disk space used: {total_space_text}',
            f'Uploaded: {self._stats["sync_count"]}',
            f'Available to download:  {self._stats["download_count"]}',
            f'Available to upload: {self._stats["upload_count"]}',
        ]
        return result

    @property
    def file_list(self):
        return self._file_list

    @property
    def listing_list(self):
        return self._listing_list

    @property
    def sync_file_list(self):
        return _sync_file_list

    @property
    def download_list(self):
        return self._download_list

    @property
    def download_file_list(self):
        return self._download_file_list

    @property
    def upload_list(self):
        return self._upload_list

    @property
    def upload_file_list(self):
        return self._upload_file_list

    @property
    def stats(self):
        return self._stats
