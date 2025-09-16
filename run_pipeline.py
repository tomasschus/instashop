"""
Main script to run the complete pipeline
InstaShop Big Data Pipeline
"""

import sys
import time
import threading
from datetime import datetime

from kafka_streaming import InstaShopKafkaProducer, InstaShopKafkaConsumer
from spark_analytics import InstaShopSparkStreaming

def run_producer(duration_minutes=2):
    producer = InstaShopKafkaProducer()
    producer.run_producer(duration_minutes=duration_minutes)

def run_consumer(duration_minutes=3):
    consumer = InstaShopKafkaConsumer()
    consumer.run_consumer(duration_minutes=duration_minutes)

def run_spark_streaming():
    streaming = InstaShopSparkStreaming()
    streaming.start_streaming_analysis()

def main():
    print("INSTASHOP BIG DATA PIPELINE")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nOptions:")
    print("1. Complete pipeline (Producer + Consumer + Spark)")
    print("2. Producer only")
    print("3. Consumer only") 
    print("4. Spark Streaming only")
    print("5. Producer + Consumer (no Spark)")
    
    try:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            print("\nRunning complete pipeline...")
            
            producer_thread = threading.Thread(target=run_producer, args=(2,))
            consumer_thread = threading.Thread(target=run_consumer, args=(3,))
            
            producer_thread.start()
            time.sleep(2)
            consumer_thread.start()
            
            producer_thread.join()
            consumer_thread.join()
            
            print("\nBasic pipeline completed!")
            print("For Spark Streaming run: python run_pipeline.py and select option 4")
            
        elif choice == "2":
            print("\nRunning Producer only...")
            run_producer()
            
        elif choice == "3":
            print("\nRunning Consumer only...")
            run_consumer()
            
        elif choice == "4":
            print("\nRunning Spark Streaming only...")
            run_spark_streaming()
            
        elif choice == "5":
            print("\nRunning Producer + Consumer...")
            
            producer_thread = threading.Thread(target=run_producer, args=(2,))
            consumer_thread = threading.Thread(target=run_consumer, args=(3,))
            
            producer_thread.start()
            time.sleep(2)
            consumer_thread.start()
            
            producer_thread.join()
            consumer_thread.join()
            
        else:
            print("Invalid option")
            return
            
        print("\nProcess completed!")
        
    except KeyboardInterrupt:
        print("\nProcess stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()