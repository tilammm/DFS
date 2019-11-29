#!/bin/bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

site=$(curl -s https://api.ipify.org/?format=text); \
sudo docker swarm join --advertise-addr $site \
--token SWMTKN-1-24805usnjb961jxajd6xcr6nu0psvbhiyt4lxx7rnrudd414x4-1fxyp5ewhusljkffll94clid1 172.31.91.253:2377


