#!/usr/bin/env python3


import argparse
import logging
import sys

from ocean_drop.config_reader import ConfigReader
from ocean_drop import OceanDrop

DEFAULT_CONFIG_FILENAME = './ocean_drop.conf'

def main():
    parser = argparse.ArgumentParser('Ocean Drop')
    parser.add_argument(
        'drop_command',
        type=str,
        help='The type of user, "publish", "consume", "status"',
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

    logger = logging.getLogger('ocean_drop')
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    if args.path:
        config.main.drop_path = args.path

    logger.info(f'drop folder is {config.main.drop_path}')
    ocean_drop = OceanDrop(config)
    if args.drop_command:
        command_char = args.drop_command.lower()[0]
        if command_char == 'p':
            ocean_drop.publish()
        elif command_char == 'c':
            ocean_drop.consume()
        elif command_char == 's':
            ocean_drop.status()
        else:
            print(f'unknown command {args.drop_command}')


if __name__ == '__main__':
    main()
