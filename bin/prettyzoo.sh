#!/usr/bin/env bash
docker stop prettyzoo

docker container rm prettyzoo

docker build ../prettyzoo/ --tag tap:prettyzoo
docker run --network tap --ip 10.0.100.22  -p 9092:9092 --name prettyzoo -i --tag tap:prettyzoo
