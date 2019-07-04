#!/usr/bin/env python3


import argparse
import logging
import sys

from ocean_drop.config_reader import ConfigReader
from ocean_drop import OceanDrop

DEFAULT_CONFIG_FILENAME = './ocean_drop.conf'
DEFAULT_MAX_COUNT = 0

COMMAND_LIST = {
    'publish': 'Publish a new files as assets onto the Ocean Network.',
    'consume': 'Consume and download any new asset from the Ocean Newtwork.',
    'status': 'Show the status and stats of the number of files that need to be synced.',
    'watch': 'Watch for new consumer payment requests, to complete the consumer payment transactions.',
}

def show_command_help():
    print('\nThe following commands can be used:\n')
    print('Command              Description')
    for name, line in COMMAND_LIST.items():
        print(f'{name:20} {line}\n')
        

def main():
    parser = argparse.ArgumentParser('Ocean Drop')
    command_list_text = '","'.join(COMMAND_LIST)
    parser.add_argument(
        'drop_command',
        type=str,
        help=f'The type of commands: "{command_list_text}"',
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
    
    parser.add_argument(
        '-m', '--max',
        type=int,
        help=f'Only consume/publish maximum number of assets. Default: {DEFAULT_MAX_COUNT} ( 0 = No limit )',
        default=DEFAULT_MAX_COUNT,
    )
    
    parser.add_argument(
        '--help-commands',
        action='store_true',
        help='show the help for the possible commands'
    )
    args = parser.parse_args()

    if args.help_commands:
        show_command_help()
        return
        
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
        command_text = args.drop_command.lower()[:3]
        if command_text == 'pub':
            ocean_drop.publish(args.max)
        elif command_text == 'con':
            ocean_drop.consume(args.max)
        elif command_text == 'sta':
            ocean_drop.status()
        elif command_text == 'wat':
            ocean_drop.process_payment_events()
        else:
            print(f'unknown command {args.drop_command}')
            show_command_help()


if __name__ == '__main__':
    main()
