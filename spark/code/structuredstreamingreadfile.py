from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
import pyspark.sql.types as tp
# Create a Spark Session 

spark = SparkSession \
    .builder \
    .appName("StructuredStreamingRead") \
    .getOrCreate()


# Read all the csv files written atomically in a directory
userSchema = tp.StructType().add("name", "string").add("age", "integer")
csvDF = spark \
    .readStream \
    .option("sep", ",") \
    .schema(userSchema) \
    .csv("/tapvolume/")  # Equivalent to format("csv").load("/path/to/directory")


# Generate running age count
ageCount = csvDF.groupBy("age").count()

 # Start running the query that prints the running counts to the console
query = ageCount \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()