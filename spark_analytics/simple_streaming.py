"""
Simplified Spark Streaming - Alternative approach
Reads data from DWH database instead of directly from Kafka
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, avg, window, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import time

class SimpleInstaShopSparkStreaming:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("SimpleInstaShopStreaming") \
            .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        print("Simple Spark Streaming initialized")
    
    def read_from_dwh(self):
        """Read data from DWH database"""
        try:
            # Read from DWH database
            df = self.spark.read \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://localhost:5436/dwh_db") \
                .option("dbtable", "realtime_events") \
                .option("user", "dwh") \
                .option("password", "dwh123") \
                .option("driver", "org.postgresql.Driver") \
                .load()
            
            return df
        except Exception as e:
            print(f"Error reading from DWH: {e}")
            return None
    
    def analyze_data(self):
        """Perform real-time analysis on the data"""
        print("Starting data analysis...")
        
        # Read data from DWH
        df = self.read_from_dwh()
        if df is None:
            print("Could not read data from DWH")
            return
        
        print(f"Total events in DWH: {df.count()}")
        
        # Show recent events
        print("\n=== RECENT EVENTS ===")
        recent_events = df.orderBy(col("timestamp").desc()).limit(5)
        recent_events.select("event_type", "timestamp", "customer_id", "product_name", "amount").show()
        
        # Analyze by event type
        print("\n=== EVENTS BY TYPE ===")
        event_counts = df.groupBy("event_type").count().orderBy(col("count").desc())
        event_counts.show()
        
        # Analyze transactions
        print("\n=== TRANSACTION ANALYSIS ===")
        transactions = df.filter(col("event_type") == "transaction")
        if transactions.count() > 0:
            transaction_stats = transactions.agg(
                count("*").alias("total_transactions"),
                sum("amount").alias("total_revenue"),
                avg("amount").alias("avg_transaction_value")
            )
            transaction_stats.show()
            
            # Top customers by transaction count
            print("\n=== TOP CUSTOMERS ===")
            top_customers = transactions.groupBy("customer_id", "customer_name") \
                .agg(count("*").alias("transaction_count"), sum("amount").alias("total_spent")) \
                .orderBy(col("transaction_count").desc()) \
                .limit(5)
            top_customers.show()
        
        # Analyze by category
        print("\n=== ANALYSIS BY CATEGORY ===")
        category_stats = df.filter(col("category").isNotNull()) \
            .groupBy("category") \
            .agg(count("*").alias("event_count"), sum("amount").alias("total_amount")) \
            .orderBy(col("event_count").desc())
        category_stats.show()
        
        print("\n=== ANALYSIS COMPLETED ===")
    
    def run_analysis(self, duration_minutes=2):
        """Run analysis for specified duration"""
        print(f"Running analysis for {duration_minutes} minutes...")
        start_time = time.time()
        
        while (time.time() - start_time) < (duration_minutes * 60):
            self.analyze_data()
            print(f"Waiting 30 seconds before next analysis...")
            time.sleep(30)
        
        print("Analysis completed!")

if __name__ == "__main__":
    streaming = SimpleInstaShopSparkStreaming()
    streaming.run_analysis(duration_minutes=2)
