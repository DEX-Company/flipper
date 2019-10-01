"""
    I want to test flipper library

"""


import secrets
import logging
import os

from flipper import Flipper

def assert_stats_equal(stats, check_stats):
    for name, value in check_stats.items():
        assert(name in stats)
        assert(stats[name] == value)

def get_file_list(folder):
    file_list = []
    for path, folders, files in os.walk(folder):
        offset_path = path[len(str(folder)) + 1:]
        for file in files:
            file_list.append(os.path.join(offset_path, file))
    return file_list

def assert_list_equal(list_a, list_b):
    for value in list_a:
        assert(value in list_b)

    for value in list_b:
        assert(value in list_a)

def test_status_upload(config, drop_folder):
    config.main.drop_path = drop_folder['upload']
    config.main.drop_secret = secrets.token_hex(32)
    flipper = Flipper(config)
    sync_result = flipper.get_sync
    assert(sync_result)

#    print(sync_result.upload_file_list)
    actual_upload_file_list = get_file_list(drop_folder['upload'])
    assert_list_equal(sync_result.upload_file_list, actual_upload_file_list)
    stats = {
        'file_count': 3,
        'sync_count': 0,
        'download_count': 0,
        'upload_count': 3
    }
    assert_stats_equal(sync_result.stats, stats)

def test_upload(config, drop_folder):
    config.main.drop_path = drop_folder['upload']
    config.main.drop_secret = secrets.token_hex(32)
    flipper = Flipper(config)
    sync_result = flipper.get_sync
    assert(sync_result)

    stats = {
        'file_count': 3,
        'sync_count': 0,
        'download_count': 0,
        'upload_count': 3
    }
    assert_stats_equal(sync_result.stats, stats)

    flipper.upload()
    sync_result = flipper.get_sync
    assert(sync_result)
    print(sync_result.upload_file_list)

    stats = {
        'file_count': 3,
        'sync_count': 3,
        'download_count': 0,
        'upload_count': 0
    }
    assert_stats_equal(sync_result.stats, stats)
