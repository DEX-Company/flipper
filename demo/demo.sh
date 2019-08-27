#!/bin/bash

FLIPPER_FOLDER="../"
DROP_FOLDER="test_drop"

BLACK="\033[0;30m"
BLUE="\033[0;34m"
GREEN="\033[0;32m"
GREY="\033[0;90m"
CYAN="\033[0;36m"
RED="\033[0;31m"
PURPLE="\033[0;35m"
BROWN="\033[0;33m"
WHITE="\033[1;37m"
COLOR_RESET="\033[0m"

if [ ! -d demo-magic ]; then
    git clone git@github.com:paxtonhare/demo-magic.git
fi

if [ ! -d venv ]; then
virtualenv venv
fi
source venv/bin/activate


rm -f squid_py.db
rm -rf artifacts

rm -rf $DROP_FOLDER
mkdir $DROP_FOLDER
mkdir $DROP_FOLDER/upload
mkdir $DROP_FOLDER/download

cp -r resources/data_files $DROP_FOLDER/upload
cp $FLIPPER_FOLDER/README.md $DROP_FOLDER/upload

$FLIPPER_FOLDER/scripts/wait_for_migration_and_extract_keeper_artifacts.sh

pushd $FLIPPER_FOLDER
pip install -r requirements_dev.txt
pip install pyfiglet
popd

rm ./flipper
ln -s $FLIPPER_FOLDER/cli/flipper .

rm ./flipper.conf
NEW_UUID=`openssl rand -hex 16`
cp $FLIPPER_FOLDER/cli/flipper_local.conf flipper.conf
sed -i "s/^drop_secret = .*/drop_secret = $NEW_UUID/g" flipper.conf
sed -i "s/^# network_url.*//g" flipper.conf

# kill any watch process
WATCH_PID=`ps -ef | grep './flipper watch' | grep python | awk '{print $2}'`
if [ ! -z $WATCH_PID ]; then
    echo "Stopping watch process"
    kill -9 $WATCH_PID
fi

. demo-magic/demo-magic.sh -n

clear
pyfiglet 'Flipper'
echo
wait
echo
echo 'What is the Flipper?'
echo 'Python Dropbox application to provide uploading and downloading of files between users using the Ocean Network'
wait
echo
echo 'How does the demo work, what do I need to setup?'
echo 'For this demo I am running `Barge` the OceanProtocol Network `stack` locally on another tab ..'
wait
echo
echo 'Lets look at the app help text and see what options are available ..'
pe "./flipper --help"
wait
echo
echo 'The configuration file that is used for the flipper demo..'
wait
pe "more ./flipper.conf"
echo
echo 'The test folder which is split up for `upload` and `download` to test two seperate users an uploader and a downloader'
pe "ls -1 ./$DROP_FOLDER"
wait
echo
echo 'The test `upload` files availble for the app to start working'
pe "ls -1R ./$DROP_FOLDER/upload"
wait
echo
echo 'Now lets run the app and check the status for the `upload` files as an `uploader`'
pe "./flipper --path=$DROP_FOLDER/upload status"
wait
echo
echo 'Lets run the app to`upload` and register the files with the Ocean Network'
pe "./flipper --path=$DROP_FOLDER/upload upload"
echo 'upload done'
wait
echo
echo 'Now check again on the `upload` status, we should have seen the files have been registered and uploaded'
pe "./flipper --path=$DROP_FOLDER/upload status"
wait
echo
echo 'Now we need to start up the watch event process to provide payment agreements on another tab....'
wait
# pe "./flipper watch > /tmp/watch.log &"
echo
echo 'Just check the `download folder` to make sure that we do not have any files'
pe "ls -1R ./$DROP_FOLDER/download"
wait
echo
echo 'What is the `download` status with flipper as a `downloader` user'
pe "./flipper --path=$DROP_FOLDER/download status"
wait
echo
echo 'Now let us do the download and buy the assets'
pe "./flipper --path=$DROP_FOLDER/download download"
echo 'download done'
wait
echo
echo 'Check the `download` status again'
pe "./flipper --path=$DROP_FOLDER/download status"
wait
echo
echo 'Finanly check that we actually have files in the `download` folder'
pe "ls -1R ./$DROP_FOLDER/download"
wait
clear
pyfiglet 'Find out more  ...'
echo 'github repo for `flipper` is at https://github.com/DEX-Company/flipper'
echo 'github repo for `starfish` library is at https://github.com/DEX-Company/starfish-py'
echo 'github repo for `squid-py` library is at https://github.com/oceanprotocol/squid-py'
wait
