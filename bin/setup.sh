#!/bin/bash

sudo docker run -d --name registry-tmp --restart=always -p 5000:5000 registry

sudo nydusify convert --source centos --target localhost:5000/centos-nydus:latest
sudo nydusify convert --source openjdk --target localhost:5000/openjdk-nydus:latest
sudo nydusify convert --source node --target localhost:5000/node-nydus:latest
sudo nydusify convert --source tensorflow/tensorflow --target localhost:5000/tensorflow-nydus:latest

sudo /usr/bin/containerd-nydus-grpc \
	--nydusd-config /etc/nydus/nydusd-config.fusedev.json \
	--log-to-stdout
