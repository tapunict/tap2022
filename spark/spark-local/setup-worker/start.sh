#!/bin/bash 
start-worker.sh -p 7078 spark://10.0.100.27:7077
while true; do
  sleep 1000
done