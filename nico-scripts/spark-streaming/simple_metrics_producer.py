#!/usr/bin/env python3
"""
🚀 Simple Metrics Producer - Sin Spark
Lee de Kafka y envía métricas a Redis directamente
"""

import json
import redis
import logging
from datetime import datetime, timezone
from kafka import KafkaConsumer
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleMetricsProducer:
    def __init__(self):
        # Conectar a Redis
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Conectar a Kafka
        self.consumer = KafkaConsumer(
            'transactions',
            'user_behavior',
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='simple-metrics-group'
        )
        
        # Contadores de métricas
        self.metrics = {
            'transaction_count': 0,
            'total_revenue': 0.0,
            'behavior_events': 0,
            'last_update': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("🚀 Simple Metrics Producer inicializado")
    
    def update_metrics(self, event):
        """Actualizar métricas basado en el evento"""
        event_type = event.get('event_type')
        
        if event_type == 'transaction':
            self.metrics['transaction_count'] += 1
            self.metrics['total_revenue'] += event.get('total_amount', 0)
        elif event_type in ['page_view', 'product_view', 'search', 'add_to_cart']:
            self.metrics['behavior_events'] += 1
        
        self.metrics['last_update'] = datetime.now(timezone.utc).isoformat()
    
    def save_to_redis(self):
        """Guardar métricas en Redis"""
        try:
            self.redis_client.setex(
                "metrics:simple", 
                3600, 
                json.dumps(self.metrics)
            )
            logger.info(f"📊 Métricas actualizadas: {self.metrics}")
        except Exception as e:
            logger.error(f"❌ Error guardando en Redis: {e}")
    
    def run(self, duration_minutes=10):
        """Ejecutar producer simple"""
        logger.info(f"🔄 Iniciando producer simple por {duration_minutes} minutos...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        last_save_time = start_time
        
        try:
            for message in self.consumer:
                if time.time() > end_time:
                    break
                
                logger.info(f"📨 Mensaje recibido de topic: {message.topic}")
                self.update_metrics(message.value)
                
                # Guardar en Redis cada 30 segundos
                if time.time() - last_save_time >= 30:
                    self.save_to_redis()
                    last_save_time = time.time()
                
        except KeyboardInterrupt:
            logger.info("⏹️ Producer detenido por usuario")
        except Exception as e:
            logger.error(f"❌ Error en producer: {e}")
        finally:
            self.consumer.close()
            logger.info(f"✅ Producer finalizado. Métricas finales: {self.metrics}")

def main():
    producer = SimpleMetricsProducer()
    producer.run(duration_minutes=10)

if __name__ == "__main__":
    main()
