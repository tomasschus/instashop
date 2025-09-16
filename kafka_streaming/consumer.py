"""
Kafka Consumer - Reads data from Kafka and processes it
Consumes real-time events from InstaShop
"""

import json
import time
from datetime import datetime
from kafka import KafkaConsumer
import psycopg2

class InstaShopKafkaConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'transactions',
            'user_behavior', 
            'searches',
            'cart_events',
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda m: m.decode('utf-8') if m else None,
            group_id='instashop-analytics-group',
            auto_offset_reset='earliest'
        )
        
        self.db_conn = psycopg2.connect(
            host='localhost',
            port=5436,
            dbname='dwh_db',
            user='dwh',
            password='dwh123'
        )
        
        self.create_realtime_events_table()
        print("Consumer initialized and connected to Kafka")
    
    def create_realtime_events_table(self):
        cursor = self.db_conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS realtime_events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50),
            timestamp TIMESTAMP,
            customer_id INTEGER,
            customer_name VARCHAR(255),
            product_id INTEGER,
            product_name VARCHAR(255),
            category VARCHAR(100),
            amount DECIMAL(10,2),
            session_id VARCHAR(255),
            raw_data JSONB,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_sql)
        self.db_conn.commit()
        cursor.close()
        
        print("Table realtime_events created in DWH")
    
    def process_transaction_event(self, event):
        cursor = self.db_conn.cursor()
        
        insert_sql = """
        INSERT INTO realtime_events 
        (event_type, timestamp, customer_id, customer_name, product_id, product_name, 
         category, amount, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            event['event_type'],
            datetime.fromisoformat(event['timestamp']),
            event['customer_id'],
            event['customer_name'],
            event['product_id'],
            event['product_name'],
            event['category'],
            event['total_amount'],
            json.dumps(event)
        ))
        
        self.db_conn.commit()
        cursor.close()
        
        print(f"Transaction processed: {event['customer_name']} - ${event['total_amount']}")
    
    def process_click_event(self, event):
        cursor = self.db_conn.cursor()
        
        insert_sql = """
        INSERT INTO realtime_events 
        (event_type, timestamp, customer_id, customer_name, product_id, product_name, 
         category, session_id, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            event['event_type'],
            datetime.fromisoformat(event['timestamp']),
            event['customer_id'],
            event['customer_name'],
            event['product_id'],
            event['product_name'],
            event['category'],
            event['session_id'],
            json.dumps(event)
        ))
        
        self.db_conn.commit()
        cursor.close()
        
        print(f"Click processed: {event['customer_name']} on {event['product_name']}")
    
    def process_search_event(self, event):
        cursor = self.db_conn.cursor()
        
        insert_sql = """
        INSERT INTO realtime_events 
        (event_type, timestamp, customer_id, customer_name, session_id, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            event['event_type'],
            datetime.fromisoformat(event['timestamp']),
            event['customer_id'],
            event['customer_name'],
            event['session_id'],
            json.dumps(event)
        ))
        
        self.db_conn.commit()
        cursor.close()
        
        print(f"Search processed: {event['customer_name']} - '{event['search_query']}'")
    
    def process_cart_abandonment_event(self, event):
        cursor = self.db_conn.cursor()
        
        insert_sql = """
        INSERT INTO realtime_events 
        (event_type, timestamp, customer_id, customer_name, amount, session_id, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            event['event_type'],
            datetime.fromisoformat(event['timestamp']),
            event['customer_id'],
            event['customer_name'],
            event['cart_total'],
            event['session_id'],
            json.dumps(event)
        ))
        
        self.db_conn.commit()
        cursor.close()
        
        print(f"Cart abandonment processed: {event['customer_name']} - ${event['cart_total']}")
    
    def process_event(self, message):
        event = message.value
        event_type = event['event_type']
        
        try:
            if event_type == 'transaction':
                self.process_transaction_event(event)
            elif event_type == 'click':
                self.process_click_event(event)
            elif event_type == 'search':
                self.process_search_event(event)
            elif event_type == 'cart_abandonment':
                self.process_cart_abandonment_event(event)
            else:
                print(f"Unknown event type: {event_type}")
        except Exception as e:
            print(f"Error processing event: {e}")
    
    def run_consumer(self, duration_minutes=5):
        print(f"Starting consumer for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        event_count = 0
        
        try:
            for message in self.consumer:
                if time.time() > end_time:
                    break
                
                print(f"\nMessage received from topic: {message.topic}")
                self.process_event(message)
                event_count += 1
                
        except KeyboardInterrupt:
            print("\nConsumer stopped by user")
        except Exception as e:
            print(f"Error in consumer: {e}")
        finally:
            self.consumer.close()
            self.db_conn.close()
            print(f"Consumer finished. Processed {event_count} events")

def main():
    consumer = InstaShopKafkaConsumer()
    consumer.run_consumer(duration_minutes=3)

if __name__ == "__main__":
    main()