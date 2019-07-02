#!/usr/bin/env python3


import argparse
import logging

from ocean_drop.config_reader import ConfigReader
from ocean_drop import OceanDrop

DEFAULT_CONFIG_FILENAME = './ocean_drop.conf'


def main():
    parser = argparse.ArgumentParser('Ocean Drop')
    parser.add_argument(
        'drop_type',
        type=str,
        help='The type of user, "publish" or "consume"',
    )
    parser.add_argument(
        '-c', '--config',
        help=f'sets the config file. Default: {DEFAULT_CONFIG_FILENAME}',
        default=DEFAULT_CONFIG_FILENAME,
    )
    
    parser.add_argument(
        '-p', '--path',
        help=f'sets the drop or consume path to get or place the data files',
    )
    parser.add_argument(
        '-d', '--debug', 
        action='store_true',
        help='show debug log',
    )
    args = parser.parse_args()

    config = ConfigReader()
    config.read(args.config)
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    if args.path:
        config.drop_path = args.path
    
    ocean_drop = OceanDrop(config)
    if args.drop_type.lower()[0] == 'p':
        ocean_drop.publish(config.drop_path)

if __name__ == '__main__':
    main()
