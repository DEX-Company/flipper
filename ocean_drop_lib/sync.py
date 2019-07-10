"""

    Sync Class

    Sync between a folder and Ocean assets

"""

import logging

from ocean_drop_lib.utils import (
    read_file_list,
    show_size_as_text,
    generate_listing_checksum,
    get_filename_from_metadata,
)

logger = logging.getLogger('ocean_drop.sync')

class Sync():
    def __init__(self, ocean, squid_agent):
        self._ocean = ocean
        self._squid_agent = squid_agent
        self._file_list = []
        self._listing_list = []
        self._sync_file_list = []
        self._consume_list = []
        self._publish_list = []
        self._consume_file_list = []
        self._publish_file_list = []
        self._stats = {}


    def analyse(self, drop_path, drop_secret,  asset_tag):
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
            'consume_count': len(self._consume_list),
            'publish_count': len(self._publish_list)
        }
        logger.debug(', '.join(self.stats_to_text_list))
        return self._stats

    def sync_lists(self):
        self._sync_file_list = []
        self._consume_list = []
        self._publish_list = []
        self._consume_file_list = []
        self._publish_file_list = []

        for listing in self._listing_list:
            is_found = False
            for file_item in self._file_list:
                if file_item['is_file'] and file_item['size'] > 0:
                    if self.is_listing_equal_to_file_item(listing, file_item['md5_hash']):
                        self._sync_file_list.append((listing, file_item))
                        is_found = True
                        break
            if not is_found:
                self._consume_list.append(listing)
                remote_asset = listing.asset.get_asset_at_index(0)
                filename = get_filename_from_metadata(listing.ddo.metadata['base'])
                self._consume_file_list.append(filename)

        for file_item in self._file_list:
            if file_item['is_file'] and file_item['size'] > 0:
                is_found = False
                for listing in self._listing_list:
                    if self.is_listing_equal_to_file_item(listing, file_item['md5_hash']):
                        is_found = True
                        break
                if not is_found:
                    self._publish_list.append(file_item)
                    self._publish_file_list.append(file_item['relative_filename'])


    def get_valid_listings(self, asset_tag, drop_secret):
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
        data = listing.data
        if data and 'extra_data' in data:
            extra_data = data['extra_data']
            if extra_data and 'nonce' in extra_data and 'checksum' in extra_data:
                nonce = extra_data['nonce']
                checksum = generate_listing_checksum(nonce, drop_secret)
                return extra_data['checksum'] == checksum
        return False

    def is_listing_equal_to_file_item(self, listing, file_hash):
        data = listing.data
        logger.debug(f'{data}')
        if data and 'extra_data' in data:
            extra_data = data['extra_data']
            if extra_data and 'file_hash' in extra_data:
                return extra_data['file_hash'] == file_hash
        return False


    @property
    def stats_to_text_list(self):
        total_space_text = show_size_as_text(self._stats['total_size'])
        result = [
            f'Total files: {self._stats["file_count"]}',
            f'Total disk space used: {total_space_text}',
            f'Published: {self._stats["sync_count"]}',
            f'Available to consume:  {self._stats["consume_count"]}',
            f'Available to publish: {self._stats["publish_count"]}',
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
    def consume_list(self):
        return self._consume_list

    @property
    def consume_file_list(self):
        return self._consume_file_list

    @property
    def publish_list(self):
        return self._publish_list

    @property
    def publish_file_list(self):
        return self._publish_file_list

    @property
    def stats(self):
        return self._stats
