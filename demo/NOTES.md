# Ocean Drop Demo Notes

## Intro

* using demo-magic and bash
* Not using powerpoint

## What does the script do?
* simple Python script
* Similiar solution to drop box
* Send files from one user to another
* Run the script using cron jobs
* run once a day or every hour
* Using Ocean Procool network to register and purchse assets

## Demo setup
* Running barge in a seperate tab
* Run as docker containers
* Barge is the complete Ocean Protocol stack
* This demo is using a local network
* Using Parity, Aquarius & Surfer as services

## Show app command line
* Highlight --path
* --config

## Show Config file
* Explain secret
* Explain Ocean, Squid & Surfer
* Explain Auto topup and asset

## Folders
* Explain test folder
* Explain folder split between uploader and downloaded
* Show folders

## Uploader Status
* Show list of files for upload

## Do Upload
* Show DID & asset ids
* Maybe show barge and aquarius saving data

## Uploader status done
* Show completed file count

## Agreement Event Processor
* Explain that the publisher needs to have a process listerning for new customers
* Switch to over tab, and run watch
* Publisher needs to be available to start the agreement smart contracts.
* Highlight the whitelisting could be here

## Show downlaod folder
* It is empty

## Show Download status
* show available files to downlaod

## Do Download
* Show agreements being completed.
* Show escrow account completion

## Show Download done
* Show list of files

## Show Donwload files
* Show same files

## More Information
* Ocean-drop new app that works with `starfish` and `squid` for OceanProtocol
* Have a look and try it out





This is a simple python script that uses `starfish` python library to allow
one user to upload files and another user to download files. Similar to drop-box.
The main difference is that this demo uses OceanProtocol network to register and buy
'assets' or files.
When this is done the registration and purchase is recorded on the block chain showing the
time and who registered and accessed the data file.


### What is barge
The first thing I have done on a seperate tab is install and startup Barge. This
is a set of docker containers that run a local Parity block chain, and web services.
Simply it's a complete stack of the OceanProtocol. So any interaction I can test and
recrceate using Barge.

### Params on the ocean_barge, especially --path
Now we can have a look at the ocean_drop app. The main option we are going to use
is the --path option. Since we want to test the same uploader and downloader on one
computer we can split up the paths. So that the downloader has a path and the uploader has
another path.

### The main configuration file
The main configuration file, defines the block chain and web services that Ocean Protocol
needs to access to enable the services this app uses.

Such as the URL's and passwords for the Surfer service ( storage ), and the price to
sell each asset, what secret code we are going to use to make sure that the asset
has been identified correctly on the network.

### The test folder and the upload folder
The folders are in the following format for uploading

### Do the upload of files to the network
You can see the registered asset id's and DID. We have registered 3 assets or
3 files.

### Check upload status

### Startup watch process on another tab
The way OceanProtocol works, is that we need another process to be watching the
block chain using the publishers account. Once a purchase `request` has been made the
publish can start the purchase process on the block chain by creating the correct
Service Level Agreement.

### Show empty download folder

### Show download status

### Do the download and buy assets
Maybe talk about the transfer of funds between the consumer - escrow - publisher

### Check the download status

### Look at the download files

### Finish
show the github repo of ocean-drop, starfish, squid

Here are the links for the app and libraries used in this demo.
The ocean-drop is the app I'm demmoing at the moment
Starfish is the library that brings it all together
Squid-py is the low level  oceanprotocol library that does the asset registering and purchasing
