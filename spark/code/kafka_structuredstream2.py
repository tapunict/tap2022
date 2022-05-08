from __future__ import print_function

import sys

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.dataframe import DataFrame

def elaborate(batch_df: DataFrame, batch_id: int):
  batch_df.show(truncate=False)

sc = SparkContext(appName="PythonStructuredStreamsKafka")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

kafkaServer="kafkaServer:9092"
topic = "tap"

# Streaming Query

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafkaServer) \
  .option("subscribe", topic) \
  .load()

df.selectExpr("CAST(timestamp AS STRING)","CAST(value AS STRING)") \
  .writeStream \
  .format("console") \
  .start() \
  .awaitTermination()

#df.writeStream \
#  .format("console") \
#  .start() \
#  .awaitTermination()
