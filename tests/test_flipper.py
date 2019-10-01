"""
    I want to test flipper library

"""


import secrets
import logging

from flipper import Flipper

def test_status_upload(config, drop_folder):
    config.main.drop_path = drop_folder['upload']
    flipper = Flipper(config)
    print(sync_result.upload_file_list)
    stats {
        'file_count': 3,
        'sync_count': 0,
        'download_count': 0,
        'upload_count': 3
    }
    assert(sync_result)
    check_stats(sync_result.stats, stats)

def test_upload(config, drop_folder):
    config.main.drop_path = drop_folder['upload']
    flipper = Flipper(config)
    flipper.upload()
