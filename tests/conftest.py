from unittest.mock import Mock
import pytest
import secrets
import logging
import pathlib
import datetime

from ocean_drop_lib.config_reader import ConfigReader


from starfish import Ocean
from starfish.agent import (
    SurferAgent,
    SquidAgent,
)

from starfish.models.surfer_model import SurferModel

TESTS_PATH = pathlib.Path.cwd() / 'tests'
RESOURCES_PATH = TESTS_PATH / 'resources'
CONFIG_FILE = TESTS_PATH / 'ocean_drop.conf'
TEST_ASSET_FILE = RESOURCES_PATH / 'test_asset_file.txt'

TEST_LISTING_DATA = {
    'name': 'Test file asset',
    'description': 'Test asset for sale',
    'dateCreated': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'author': 'Test starfish',
    'license': 'Closed',
    'price': '1000000000000',
    'extra_data': 'Some extra data',
    'tags': ['asset', 'sale', 'test', 'starfish'],
}


@pytest.fixture(scope="module")
def ocean():
    config = ConfigReader()
    config.read(CONFIG_FILE)
    ocean = Ocean(
        keeper_url=config.ocean.keeper_url,
        contracts_path=config.ocean.contracts_path,
        gas_limit=config.ocean.gas_limit,
    )
    return ocean

@pytest.fixture(scope="module")
def config():
    config = ConfigReader()
    config.read(CONFIG_FILE)
    return config

@pytest.fixture(scope="module")
def surfer_agent(ocean):
    config = ConfigReader()
    config.read(CONFIG_FILE)

    ddo_options = None
    ddo = SurferAgent.generate_ddo(config.surfer_agent.url, ddo_options)
    options = {
        'url': config.surfer_agent.url,
        'username': config.surfer_agent.username,
        'password': config.surfer_agent.password,
    }
    surfer_agent = SurferAgent(ocean, did=ddo.did, ddo=ddo, options=options)

    return surfer_agent

@pytest.fixture(scope="module")
def squid_agent(ocean):
    config = ConfigReader()
    config.read(CONFIG_FILE)
    return SquidAgent(ocean, config.squid_agent.as_dict)

@pytest.fixture(scope="module")
def resources():
    data = Mock()
    data.asset_file = TEST_ASSET_FILE
    data.listing_data = TEST_LISTING_DATA
    return data
