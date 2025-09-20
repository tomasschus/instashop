"""
Centralized configuration for InstaShop
"""

KAFKA_CONFIG = {
    'bootstrap_servers': ['localhost:9092', 'localhost:9093', 'localhost:9094'],
    'topics': {
        'transactions': 'transactions',
        'user_behavior': 'user_behavior',
        'searches': 'searches',
        'cart_events': 'cart_events'
    }
}

DATABASE_CONFIG = {
    'instashop': {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'instashop',
        'user': 'insta',
        'password': 'insta123'
    },
    'crm': {
        'host': 'localhost',
        'port': 5433,
        'dbname': 'crm_db',
        'user': 'crm',
        'password': 'crm123'
    },
    'erp': {
        'host': 'localhost',
        'port': 5434,
        'dbname': 'erp_db',
        'user': 'erp',
        'password': 'erp123'
    },
    'ecommerce': {
        'host': 'localhost',
        'port': 5435,
        'dbname': 'ecommerce_db',
        'user': 'ecommerce',
        'password': 'ecommerce123'
    },
    'dwh': {
        'host': 'localhost',
        'port': 5436,
        'dbname': 'dwh_db',
        'user': 'dwh',
        'password': 'dwh123'
    }
}

SPARK_CONFIG = {
    'app_name': 'InstaShopStreaming',
    'kafka_package': 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0',
    'log_level': 'WARN'
}

EVENT_CONFIG = {
    'event_types': ['transaction', 'click', 'search', 'cart_abandonment'],
    'categories': ['Clothing', 'Electronics', 'Books', 'Home', 'Toys'],
    'payment_methods': ['Credit Card', 'PayPal', 'Wire Transfer'],
    'subscription_plans': ['Free', 'Pro', 'Enterprise']
}