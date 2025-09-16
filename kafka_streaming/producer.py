"""
Kafka Producer - Sends data from PostgreSQL to Kafka
Simulates real-time events for InstaShop
"""

import json
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
import psycopg2
from faker import Faker

fake = Faker()

class InstaShopKafkaProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        self.db_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            dbname='instashop',
            user='insta',
            password='insta123'
        )
        
        self.customers = self.get_customers()
        self.products = self.get_products()
        self.buyers = self.get_buyers()
        
        print(f"Producer initialized: {len(self.customers)} customers, {len(self.products)} products, {len(self.buyers)} buyers")
    
    def get_customers(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT customer_id, business_name, subscription_plan FROM customer LIMIT 50")
        return cursor.fetchall()
    
    def get_products(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT product_id, name, category, price FROM product LIMIT 100")
        return cursor.fetchall()
    
    def get_buyers(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT buyer_id, name, email FROM buyer LIMIT 200")
        return cursor.fetchall()
    
    def generate_transaction_event(self):
        customer = random.choice(self.customers)
        buyer = random.choice(self.buyers)
        product = random.choice(self.products)
        
        event = {
            'event_type': 'transaction',
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer[0],
            'customer_name': customer[1],
            'subscription_plan': customer[2],
            'buyer_id': buyer[0],
            'buyer_name': buyer[1],
            'product_id': product[0],
            'product_name': product[1],
            'category': product[2],
            'price': float(product[3]),
            'quantity': random.randint(1, 5),
            'total_amount': round(float(product[3]) * random.randint(1, 5), 2),
            'payment_method': random.choice(['Credit Card', 'PayPal', 'Wire Transfer']),
            'status': random.choice(['completed', 'pending', 'failed'])
        }
        return event
    
    def generate_click_event(self):
        customer = random.choice(self.customers)
        product = random.choice(self.products)
        
        event = {
            'event_type': 'click',
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer[0],
            'customer_name': customer[1],
            'product_id': product[0],
            'product_name': product[1],
            'category': product[2],
            'page': random.choice(['homepage', 'product_page', 'category_page', 'search_results']),
            'session_id': fake.uuid4(),
            'user_agent': fake.user_agent()
        }
        return event
    
    def generate_search_event(self):
        customer = random.choice(self.customers)
        
        event = {
            'event_type': 'search',
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer[0],
            'customer_name': customer[1],
            'search_query': random.choice(['laptop', 'phone', 'book', 'clothing', 'electronics']),
            'results_count': random.randint(0, 50),
            'session_id': fake.uuid4()
        }
        return event
    
    def generate_cart_abandonment_event(self):
        customer = random.choice(self.customers)
        products = random.sample(self.products, random.randint(1, 3))
        
        event = {
            'event_type': 'cart_abandonment',
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer[0],
            'customer_name': customer[1],
            'cart_items': [
                {
                    'product_id': p[0],
                    'product_name': p[1],
                    'price': float(p[3]),
                    'quantity': random.randint(1, 3)
                } for p in products
            ],
            'cart_total': sum(float(p[3]) * random.randint(1, 3) for p in products),
            'session_id': fake.uuid4()
        }
        return event
    
    def send_event(self, topic, event):
        try:
            self.producer.send(topic, value=event, key=str(event['customer_id']))
            print(f"Sent to {topic}: {event['event_type']} - Customer {event['customer_id']}")
        except Exception as e:
            print(f"Error sending to {topic}: {e}")
    
    def run_producer(self, duration_minutes=2):
        print(f"Starting producer for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        event_types = ['transaction', 'click', 'search', 'cart_abandonment']
        topics = ['transactions', 'user_behavior', 'searches', 'cart_events']
        
        while time.time() < end_time:
            event_type = random.choice(event_types)
            topic = topics[event_types.index(event_type)]
            
            if event_type == 'transaction':
                event = self.generate_transaction_event()
            elif event_type == 'click':
                event = self.generate_click_event()
            elif event_type == 'search':
                event = self.generate_search_event()
            elif event_type == 'cart_abandonment':
                event = self.generate_cart_abandonment_event()
            
            self.send_event(topic, event)
            time.sleep(random.uniform(0.5, 2.0))
        
        print("Producer finished")
        self.producer.close()
        self.db_conn.close()

def main():
    producer = InstaShopKafkaProducer()
    producer.run_producer(duration_minutes=2)

if __name__ == "__main__":
    main()