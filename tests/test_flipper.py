"""
    I want to test flipper library

"""


import secrets
import logging
import os
import threading

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

def assert_pre_upload_stats(flipper, drop_folder):
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

def assert_post_upload_stats(flipper, drop_folder8):
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

def assert_pre_download_stats(flipper, drop_folder8):
    sync_result = flipper.get_sync
    assert(sync_result)
    print(sync_result.upload_file_list)

    stats = {
        'file_count': 0,
        'sync_count': 0,
        'download_count': 3,
        'upload_count': 0
    }
    assert_stats_equal(sync_result.stats, stats)


def assert_post_download_stats(flipper, drop_folder8):
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

def process_payments(flipper, timeout_seconds):
    flipper.process_payment_events(timeout_seconds)

def test_upload_download(config, drop_folder):
    config.main.drop_path = drop_folder['upload']
    config.main.drop_secret = secrets.token_hex(32)
    flipper = Flipper(config)
    assert_pre_upload_stats(flipper, drop_folder)
    flipper.upload()
    assert_post_upload_stats(flipper, drop_folder)

    thread = threading.Thread(target=process_payments, args=(flipper, 60 ))
    thread.start()

    config.main.drop_path = drop_folder['download']
    flipper = Flipper(config)
    assert_pre_download_stats(flipper, drop_folder)
    flipper.download()
    assert_post_download_stats(flipper, drop_folder)
