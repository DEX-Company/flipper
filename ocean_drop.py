#!/usr/bin/env python3


import argparse


DEFAULT_CONFIG_FILENAME = './ocean_drop.conf'


def main():
    parser = argparse.ArgumentParser('Ocean Drop')
    parser.add_argument(
        '-c', '--config',
        help=f'sets the config file. Default: {DEFAULT_CONFIG_FILENAME}')
                        
    parser.add_argument(
        '-d', '--debug', 
        action='store_true',
        help='show debug log'
    )
    args = parser.parse_args()


if __name__ == '__main__':
    main()
