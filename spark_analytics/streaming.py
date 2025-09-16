"""
Spark Streaming - Processes Kafka data in real-time
Advanced analytics with Apache Spark
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

class InstaShopSparkStreaming:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("InstaShopStreaming") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        print("Spark Streaming initialized")
    
    def create_kafka_stream(self, topic):
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092,localhost:9093,localhost:9094") \
            .option("subscribe", topic) \
            .option("startingOffsets", "earliest") \
            .load()
        
        return df
    
    def parse_json_schema(self):
        return StructType([
            StructField("event_type", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("customer_id", IntegerType(), True),
            StructField("customer_name", StringType(), True),
            StructField("subscription_plan", StringType(), True),
            StructField("buyer_id", IntegerType(), True),
            StructField("buyer_name", StringType(), True),
            StructField("product_id", IntegerType(), True),
            StructField("product_name", StringType(), True),
            StructField("category", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("quantity", IntegerType(), True),
            StructField("total_amount", DoubleType(), True),
            StructField("payment_method", StringType(), True),
            StructField("status", StringType(), True),
            StructField("page", StringType(), True),
            StructField("session_id", StringType(), True),
            StructField("search_query", StringType(), True),
            StructField("results_count", IntegerType(), True),
            StructField("cart_items", ArrayType(StringType()), True),
            StructField("cart_total", DoubleType(), True)
        ])
    
    def process_transactions_stream(self):
        print("Processing transactions stream...")
        
        kafka_df = self.create_kafka_stream("transactions")
        
        json_schema = self.parse_json_schema()
        
        parsed_df = kafka_df \
            .select(from_json(col("value").cast("string"), json_schema).alias("data")) \
            .select("data.*") \
            .filter(col("event_type") == "transaction")
        
        realtime_metrics = parsed_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(window(col("timestamp"), "1 minute")) \
            .agg(
                count("*").alias("transaction_count"),
                sum("total_amount").alias("total_revenue"),
                avg("total_amount").alias("avg_order_value"),
                countDistinct("customer_id").alias("unique_customers")
            ) \
            .select(
                col("window.start").alias("time_window"),
                col("transaction_count"),
                col("total_revenue"),
                col("avg_order_value"),
                col("unique_customers")
            )
        
        return realtime_metrics
    
    def process_user_behavior_stream(self):
        print("Processing user behavior stream...")
        
        kafka_df = self.create_kafka_stream("user_behavior")
        
        json_schema = self.parse_json_schema()
        
        parsed_df = kafka_df \
            .select(from_json(col("value").cast("string"), json_schema).alias("data")) \
            .select("data.*") \
            .filter(col("event_type") == "click")
        
        behavior_metrics = parsed_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(window(col("timestamp"), "1 minute"), "category") \
            .agg(
                count("*").alias("click_count"),
                countDistinct("customer_id").alias("unique_users")
            ) \
            .select(
                col("window.start").alias("time_window"),
                col("category"),
                col("click_count"),
                col("unique_users")
            )
        
        return behavior_metrics
    
    def process_cart_abandonment_stream(self):
        print("Processing cart abandonment stream...")
        
        kafka_df = self.create_kafka_stream("cart_events")
        
        json_schema = self.parse_json_schema()
        
        parsed_df = kafka_df \
            .select(from_json(col("value").cast("string"), json_schema).alias("data")) \
            .select("data.*") \
            .filter(col("event_type") == "cart_abandonment")
        
        abandonment_metrics = parsed_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(window(col("timestamp"), "1 minute")) \
            .agg(
                count("*").alias("abandoned_carts"),
                sum("cart_total").alias("lost_revenue"),
                avg("cart_total").alias("avg_cart_value")
            ) \
            .select(
                col("window.start").alias("time_window"),
                col("abandoned_carts"),
                col("lost_revenue"),
                col("avg_cart_value")
            )
        
        return abandonment_metrics
    
    def start_streaming_analysis(self):
        print("Starting streaming analysis...")
        
        try:
            transaction_stream = self.process_transactions_stream()
            behavior_stream = self.process_user_behavior_stream()
            abandonment_stream = self.process_cart_abandonment_stream()
            
            transaction_query = transaction_stream \
                .writeStream \
                .outputMode("update") \
                .format("console") \
                .option("truncate", False) \
                .start()
            
            behavior_query = behavior_stream \
                .writeStream \
                .outputMode("update") \
                .format("console") \
                .option("truncate", False) \
                .start()
            
            abandonment_query = abandonment_stream \
                .writeStream \
                .outputMode("update") \
                .format("console") \
                .option("truncate", False) \
                .start()
            
            print("Streams started. Press Ctrl+C to stop...")
            
            transaction_query.awaitTermination()
            behavior_query.awaitTermination()
            abandonment_query.awaitTermination()
            
        except KeyboardInterrupt:
            print("\nStreaming stopped by user")
        except Exception as e:
            print(f"Error in streaming: {e}")
        finally:
            self.spark.stop()
            print("Spark Streaming finished")

def main():
    streaming = InstaShopSparkStreaming()
    streaming.start_streaming_analysis()

if __name__ == "__main__":
    main()