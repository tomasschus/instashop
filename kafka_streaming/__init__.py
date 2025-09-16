"""
Kafka Streaming Module
Maneja la comunicación con Apache Kafka
"""

from .producer import InstaShopKafkaProducer
from .consumer import InstaShopKafkaConsumer

__all__ = ['InstaShopKafkaProducer', 'InstaShopKafkaConsumer']
