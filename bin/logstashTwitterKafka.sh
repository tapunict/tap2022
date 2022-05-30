#!/usr/bin/env bash
#REM Stop
docker stop taplogstashkafka

#REM Remove previuos container 
docker container rm taplogstashkafka

#REM Build
docker build ../logstash_to_kafka/ --tag tap:taplogstashkafka

docker stop taplogstashkafka
#REM Run
docker run --network tap --ip 10.0.100.10  -it --name taplogstashkafka tap:taplogstashkafka