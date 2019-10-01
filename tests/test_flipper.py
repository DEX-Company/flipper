"""
    I want to test flipper library

"""


import secrets
import logging

from flipper import Flipper

def check_stats(stats, check_stats):
    for name, value in check_stats.items():
        assert(name in stats)
        assert(stats[name] == value)

def test_status_upload(config, drop_folder):
    config.main.drop_path = drop_folder['upload']
    config.main.drop_secret = secrets.token_hex(32)
    flipper = Flipper(config)
    sync_result = flipper.get_sync
    assert(sync_result)
    print(sync_result.upload_file_list)
    stats = {
        'file_count': 3,
        'sync_count': 0,
        'download_count': 0,
        'upload_count': 3,
    }
    check_stats(sync_result.stats, stats)

def test_upload(config, drop_folder):
    config.main.drop_path = drop_folder['upload']
    flipper = Flipper(config)
    flipper.upload()
