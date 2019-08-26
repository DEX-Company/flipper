# Flipper Drop

Python app to allow for publishing and conusming of files via a folder.
The publisher just copies the data files into a folder, and runs the
*Flipper Drop* script.

This script then publishes the new data files.

The data consumer can then run the *Flipper Drop* script and automatically
purchase and download any new data files into their own folder.

The cli script can be found in the `cli` folder.


```
usage: FLipper Drop [-h] [-c CONFIG] [-p PATH] [-d] [-m MAX] [--help-commands]
                  [--name NAME] [-n]
                  [drop_command [drop_command ...]]

positional arguments:
  drop_command          The type of commands:
                        "upload","download","status","watch","account"

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        sets the config file. Default: ./flipper_drop.conf
  -p PATH, --path PATH  sets the upload or download path to get or place the
                        data files
  -d, --debug           show debug log
  -m MAX, --max MAX     Only upload/download maximum number of assets.
                        Default: 0 ( 0 = No limit )
  --help-commands       show the help for the possible commands
  --name NAME           Upload or download a file matching with the name
                        provided
  -n, --dry-run         if enabled then process as a upload or download but do
                        not change any files
```

## Testing

To test with a local Ocean network, you need to do the following:

1. Setup the environment.
```
$ git clone https://github.com/DEX-Company/flipper-drop
$ cd flipper_drop
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements_dev.txt
```

2. In a seperate terminal download and run Dex barge from https://github.com/DEX-Company/barge using the local spree test network

```
# if you are already in flipper_drop folder..
$ cd ..

# or go to the parent folder to install barge
# cd $HOME/myprojecs

$ git clone https://github.com/DEX-Company/barge
$ cd barge
$ ./start_ocean.sh --no-brizo --no-pleuston --local-spree-node
```

3. Return back to the first terminal with flipper-drop and run the contract wait script, to get the new contracts created on your local network
```
$ ./scripts/wait_for_migration_and_extract_keeper_artifacts.sh
```

4. Run the tests
```
$ pytest tests
```
