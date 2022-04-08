# https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad
import os
from time import sleep
from json import dumps
from kafka import KafkaProducer

topic = os.getenv("KAFKA_TOPIC", "tap")
producer = KafkaProducer(bootstrap_servers=['kafkaServer:9092'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

for e in range(1000):
    data = {'number' : e}
    producer.send(topic, value=data)
    sleep(5)
