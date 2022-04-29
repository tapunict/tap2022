from __future__ import print_function

import sys
import json
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.streaming import StreamingContext
import pyspark
from pyspark.conf import SparkConf
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import from_json, struct, to_json
from pyspark.streaming import StreamingContext
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark.sql import Row
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from elasticsearch import Elasticsearch
import os
import sys


es = Elasticsearch(hosts="10.0.100.51") 

## is there a field in the mapping that should be used to specify the ES document ID
# "es.mapping.id": "id"

# Define Training Set Structure
tweetKafka = tp.StructType([
    tp.StructField(name= 'id_str', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'created_at', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'text',       dataType= tp.StringType(),  nullable= True)
])

# Training Set Schema
schema = tp.StructType([
    tp.StructField(name= 'id', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'subjective',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'positive',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'negative',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'ironic',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'lpositive',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'lnegative',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'top',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'text',       dataType= tp.StringType(),   nullable= True)
])


sc = SparkContext(appName="TapSentiment")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

conf = SparkConf(loadDefaults=False)
# read the dataset  
training_set = spark.read.csv('../tap/spark/dataset/training_set_sentipolc16.csv',
                         schema=schema,
                         header=True,
                         sep=',')

# define stage 1: tokenize the tweet text    
stage_1 = RegexTokenizer(inputCol= 'text' , outputCol= 'tokens', pattern= '\\W')
# define stage 2: remove the stop words
stage_2 = StopWordsRemover(inputCol= 'tokens', outputCol= 'filtered_words')
# define stage 3: create a word vector of the size 100
stage_3 = Word2Vec(inputCol= 'filtered_words', outputCol= 'vector', vectorSize= 100)
# define stage 4: Logistic Regression Model
model = LogisticRegression(featuresCol= 'vector', labelCol= 'positive')
# setup the pipeline
pipeline = Pipeline(stages= [stage_1, stage_2, stage_3, model])

# fit the pipeline model with the training data
pipelineFit = pipeline.fit(training_set)

modelSummary=pipelineFit.stages[-1].summary
modelSummary.accuracy


def elaborate(batch_df: DataFrame, batch_id: int):
    batch_df.show(truncate=False)
    if not batch_df.rdd.isEmpty():
        print("********************")
        data2=pipelineFit.transform(batch_df)
        data2.show()
        ##  [id, created_at, filtered_words, prediction, probability, rawPrediction, text, tokens, vector];
        data2.foreach(sendToEs)

# Method 1: Very inefficient 
def sendToEs(tweet):
    es = Elasticsearch(hosts="10.0.100.51") 
    print("Sending to ES")
    print(tweet.id_str)
    jsonTweet={"doc": {"created_at": tweet.created_at,"tweet":tweet.text,"prediction":tweet.prediction}}
    print(jsonTweet)
    es.create(index="tweets", id=tweet.id_str, body=jsonTweet)


kafkaServer="kafkaServer:9092"
topic = "tap"

# Streaming Query

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafkaServer) \
  .option("subscribe", topic) \
  .load()

df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", tweetKafka).alias("data")) \
    .select("data.*") \
    .writeStream \
    .foreachBatch(elaborate) \
    .start() \
    .awaitTermination()
 
 ##   .option("es.resource","testindex/testdoc") \
 ##   

## ##.foreachBatch(elaborate) \