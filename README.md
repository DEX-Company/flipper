# Ocean Drop

Python app to allow for publishing and conusming of files via a folder.
The publisher just copies the data files into a folder, and runs the
*Ocean Drop* script.

This script then publishes the new data files.

The data consumer can then run the *Ocean Drop* script and automatically
purchase and download any new data files into their own folder.


```
usage: Ocean Drop [-h] [-c CONFIG] [-p PATH] [-d] [-m MAX] [--help-commands]
                  [--name NAME] [-n]
                  [drop_command [drop_command ...]]

positional arguments:
  drop_command          The type of commands:
                        "upload","download","status","watch","account"

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        sets the config file. Default: ./ocean_drop.conf
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
