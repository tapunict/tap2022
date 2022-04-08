FROM tap:kafka
ADD streams.examples/target/streams.examples-0.1.jar /opt/kafka/libs
WORKDIR /opt/kafka/
ENTRYPOINT [ "kafka-run-class.sh","tap.WordCount"]  