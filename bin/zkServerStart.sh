#!/usr/bin/env bash
# Stop
docker stop kafkaZookeeperWebUI

# Remove previuos container 
docker container rm kafkaZookeeperWebUI

docker build ../zookeeper/ --tag tap:kafka
docker run --network tap --ip 10.0.100.22 -d -p 9092:9092 --name kafkaZookeeperWebUI -t --tag tap:kafka