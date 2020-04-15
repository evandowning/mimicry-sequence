#!/bin/bash

uid=`id -u`

# Check user permissions
if [[ $uid -ne 0 ]]; then
    echo 'must be root'
    exit 2
fi

# Stop on any error
set -e

# Update
apt update

# Install neo4j - https://debian.neo4j.org/
apt install -y wget apt-transport-https ca-certificates
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.org/repo stable/' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
apt update
apt install -y neo4j=1:3.5.2

# Install python3
apt install -y python3.5
apt install -y python3-pip
pip3 install -r requirements.txt
