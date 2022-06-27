from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.conf import SparkConf
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark import SparkContext
from pyspark.sql import SparkSession
from elasticsearch import Elasticsearch

elastic_host="http://elasticsearch:9200"
elastic_index="taptweet"
kafkaServer="kafkaServer:9092"
topic = "tap"


## is there a field in the mapping that should be used to specify the ES document ID
# "es.mapping.id": "id"
# Credit for mapping https://medium.com/@CMpoi/elasticsearch-defining-the-mapping-of-twitter-data-dafad0f50695 Timestamp

es_mapping = {
    "mappings": {
        "properties": 
            {
                "created_at": {"type": "date","format": "EEE MMM dd HH:mm:ss Z yyyy"},
                "text": {"type": "text","fielddata": True}
            }
    }
}

es = Elasticsearch(hosts=elastic_host) 
# make an API call to the Elasticsearch cluster
# and have it return a response:
response = es.indices.create(
    index=elastic_index,
    body=es_mapping,
    ignore=400 # ignore 400 already exists code
)

if 'acknowledged' in response:
    if response['acknowledged'] == True:
        print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])


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

sparkConf = SparkConf().set("es.nodes", "elasticsearch") \
                        .set("es.port", "9200")

sc = SparkContext(appName="TapSentiment", conf=sparkConf)
spark = SparkSession(sc)
sc.setLogLevel("WARN")

# read the dataset  
training_set = spark.read.csv('../tap/spark/dataset/training_set_sentipolc16.csv',
                         schema=schema,
                         header=True,
                         sep=',')

tokenizer = Tokenizer(inputCol="text", outputCol="words")
hashtf = HashingTF(numFeatures=2**16, inputCol="words", outputCol='tf')
idf = IDF(inputCol='tf', outputCol="features", minDocFreq=5) #minDocFreq: remove sparse terms
model = LogisticRegression(featuresCol= 'features', labelCol= 'positive',maxIter=100)
pipeline = Pipeline(stages=[tokenizer, hashtf, idf, model])

# fit the pipeline model with the training data
pipelineFit = pipeline.fit(training_set)

modelSummary=pipelineFit.stages[-1].summary
print ("Model Accuracy:")
print(modelSummary.accuracy)
# Streaming Query

# Read the stream from kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .load()


# Cast the message received from kafka with the provided schema
df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", tweetKafka).alias("data")) \
    .select("data.*")

# Apply the machine learning model and select only the interesting columns
df = pipelineFit.transform(df) \
    .select("id_str", "created_at", "text", "prediction")

# Write the stream to elasticsearch
df.writeStream \
    .option("checkpointLocation", "/save/location") \
    .format("es") \
    .start(elastic_index) \
    .awaitTermination()
 
df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start() \
    .awaitTermination()