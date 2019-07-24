#!/bin/bash

# code highlighting

PYGMENTIZE="pygmentize -O full,style=native"
SRC_PATH=../
clear

#connect
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '138, 170 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Connect to the ocean network via starfish"; clear

# upload
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '44, 76 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Upload and register assets"; clear

# upload
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '170, 203 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Upload and register an asset"; clear

# create listing data
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '320, 346 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Create listing data for each asset"; clear

# generate_listing_checksum
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/utils.py |  sed -n '119, 122 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Create a unique listing checksum"; clear

# search valid listings
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/sync.py |  sed -n '123, 145 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Search for a valid listing"; clear

# is listing valid
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/sync.py |  sed -n '145, 166 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "is listing valid"; clear


# download assets
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '77, 112 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Download assets"; clear

# download asset Part 1
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '204, 231 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Download an asset Part 1"; clear


# download asset Part 2
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '204, 204 p'
echo " ... "
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '231, 270 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Download an asset Part 2"; clear

# auto topup
echo "-------------------------------------------------------------------------"
echo ""
$PYGMENTIZE $SRC_PATH/ocean_drop/ocean_drop.py |  sed -n '298, 320 p'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Auto topup"; clear
echo "-------------------------------------------------------------------------"
echo ""
echo ""
echo 'github repo for `ocean-drop` is at https://github.com/DEX-Company/ocean-drop'
echo 'github repo for `starfish` library is at https://github.com/DEX-Company/starfish-py'
echo 'github repo for `squid-py` library is at https://github.com/oceanprotocol/squid-py'
echo ""
echo ""
echo "-------------------------------------------------------------------------"
read -p "Find out more"; clear
