#!/bin/sh

echo '## Encoding'
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

echo '## For install Python3.7 add-apt-repository ppa:deadsnakes/ppa'
sudo add-apt-repository -y ppa:deadsnakes/ppa

echo '## apt update and upgrade'
sudo apt -y update
sudo apt -y upgrade

echo '## Install Python3.7'
sudo apt install -y python3.7 python3.7-dev

echo '## Install pip'
# NOTE: After them can use both pip and pip3 commands. But they are symbolic links of the same file.
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.7 get-pip.py
rm get-pip.py

echo '## Create pipenv environment'
# NOTE: Paramiko and Dulwich are included in Pipfile
cd /project-dir
sudo pip install pipenv
# I don't know why, but an error occurs without setting LC_ALL and LANG environ only on Mac.
pipenv install

echo '## Install zip and unzip'
sudo apt install -y zip unzip

echo '## Create zip file'
cd /project-dir
rm project.zip
# py files
zip project.zip lambda_function.py
# pip libraries
VENV_PATH=`pipenv --venv`
cd "$VENV_PATH/lib/python3.7/site-packages"
zip /project-dir/project.zip ./* -r

# environ
# TODO: Implement
export TARGET_URL=''
