#!/usr/bin/env python3
"""
🚀 Dynamic Kafka Consumer - Lee de Kafka y procesa hacia DWH
Procesa eventos en tiempo real y los almacena en Data Warehouse
"""

import json
import time
import logging
from datetime import datetime
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import RealDictCursor

# Desactivar logs de debug de Faker
logging.getLogger('faker').setLevel(logging.WARNING)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DynamicInstaShopKafkaConsumer:
    def __init__(self):
        # Conectar a Kafka
        self.consumer = KafkaConsumer(
            'transactions',
            'user_behavior', 
            'searches',
            'cart_events',
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda m: m.decode('utf-8') if m else None,
            group_id='instashop-dynamic-group',
            auto_offset_reset='latest',  # Solo mensajes nuevos
            enable_auto_commit=True,
            auto_commit_interval_ms=1000
        )
        
        # Conectar a DWH
        self.dwh_conn = psycopg2.connect(
            host='localhost',
            port=5436,
            dbname='dwh_db',
            user='dwh',
            password='dwh123'
        )
        
        self.create_realtime_events_table()
        logger.info("🚀 Dynamic Kafka Consumer inicializado")
    
    def create_realtime_events_table(self):
        """Crear tabla de eventos en tiempo real en DWH"""
        try:
            cursor = self.dwh_conn.cursor()
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS realtime_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                customer_id INTEGER,
                customer_name VARCHAR(255),
                product_id INTEGER,
                product_name VARCHAR(255),
                category VARCHAR(100),
                amount DECIMAL(12,2),
                session_id VARCHAR(255),
                raw_data JSONB,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source VARCHAR(50) DEFAULT 'kafka_consumer'
            )
            """
            
            cursor.execute(create_table_sql)
            self.dwh_conn.commit()
            cursor.close()
            
            logger.info("✅ Tabla realtime_events creada en DWH")
        except Exception as e:
            logger.error(f"❌ Error creando tabla: {e}")
    
    def process_transaction_event(self, event):
        """Procesar evento de transacción"""
        try:
            cursor = self.dwh_conn.cursor()
            
            insert_sql = """
            INSERT INTO realtime_events 
            (event_type, timestamp, customer_id, customer_name, product_id, product_name, 
             category, amount, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Extraer datos del evento
            customer_id = event.get('customer_id')
            customer_name = event.get('customer_name')
            product_id = event.get('product_id')
            product_name = event.get('product_name')
            category = event.get('category')
            amount = event.get('total_amount')
            
            cursor.execute(insert_sql, (
                event['event_type'],
                datetime.fromisoformat(event['timestamp']),
                customer_id,
                customer_name,
                product_id,
                product_name,
                category,
                amount,
                json.dumps(event)
            ))
            
            self.dwh_conn.commit()
            cursor.close()
            
            logger.info(f"✅ Transacción procesada: {customer_name} - ${amount}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando transacción: {e}")
            self.dwh_conn.rollback()
    
    def process_behavior_event(self, event):
        """Procesar evento de comportamiento"""
        try:
            cursor = self.dwh_conn.cursor()
            
            insert_sql = """
            INSERT INTO realtime_events 
            (event_type, timestamp, customer_id, customer_name, product_id, product_name, 
             category, session_id, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Extraer datos del evento
            customer_id = event.get('customer_id')
            customer_name = event.get('customer_name')
            product_id = event.get('product_id')
            product_name = event.get('product_name')
            category = event.get('category')
            session_id = event.get('session_id')
            
            cursor.execute(insert_sql, (
                event['event_type'],
                datetime.fromisoformat(event['timestamp']),
                customer_id,
                customer_name,
                product_id,
                product_name,
                category,
                session_id,
                json.dumps(event)
            ))
            
            self.dwh_conn.commit()
            cursor.close()
            
            logger.info(f"✅ Comportamiento procesado: {customer_name} - {event.get('interaction_type', 'event')}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando comportamiento: {e}")
            self.dwh_conn.rollback()
    
    def process_search_event(self, event):
        """Procesar evento de búsqueda"""
        try:
            cursor = self.dwh_conn.cursor()
            
            insert_sql = """
            INSERT INTO realtime_events 
            (event_type, timestamp, customer_id, customer_name, session_id, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_sql, (
                event['event_type'],
                datetime.fromisoformat(event['timestamp']),
                event.get('customer_id'),
                event.get('customer_name'),
                event.get('session_id'),
                json.dumps(event)
            ))
            
            self.dwh_conn.commit()
            cursor.close()
            
            logger.info(f"✅ Búsqueda procesada: {event.get('customer_name')} - '{event.get('search_query')}'")
            
        except Exception as e:
            logger.error(f"❌ Error procesando búsqueda: {e}")
            self.dwh_conn.rollback()
    
    def process_cart_event(self, event):
        """Procesar evento de carrito"""
        try:
            cursor = self.dwh_conn.cursor()
            
            insert_sql = """
            INSERT INTO realtime_events 
            (event_type, timestamp, customer_id, customer_name, amount, session_id, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_sql, (
                event['event_type'],
                datetime.fromisoformat(event['timestamp']),
                event.get('customer_id'),
                event.get('customer_name'),
                event.get('cart_total'),
                event.get('session_id'),
                json.dumps(event)
            ))
            
            self.dwh_conn.commit()
            cursor.close()
            
            logger.info(f"✅ Carrito procesado: {event.get('customer_name')} - ${event.get('cart_total')}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando carrito: {e}")
            self.dwh_conn.rollback()
    
    def process_event(self, message):
        """Procesar evento según su tipo"""
        event = message.value
        event_type = event.get('event_type')
        topic = message.topic
        
        try:
            if event_type == 'transaction':
                self.process_transaction_event(event)
            elif event_type == 'user_behavior':
                self.process_behavior_event(event)
            elif event_type == 'search':
                self.process_search_event(event)
            elif event_type == 'cart_abandonment':
                self.process_cart_event(event)
            else:
                logger.warning(f"⚠️ Tipo de evento desconocido: {event_type} en topic {topic}")
                
        except Exception as e:
            logger.error(f"❌ Error procesando evento: {e}")
    
    def get_processing_stats(self):
        """Obtener estadísticas de procesamiento"""
        try:
            cursor = self.dwh_conn.cursor()
            
            # Contar eventos por tipo
            query = """
            SELECT event_type, COUNT(*) as count 
            FROM realtime_events 
            WHERE processed_at >= NOW() - INTERVAL '1 hour'
            GROUP BY event_type
            """
            
            cursor.execute(query)
            stats = cursor.fetchall()
            cursor.close()
            
            return stats
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return []
    
    def run_consumer(self, duration_minutes=10):
        """Ejecutar consumer dinámico"""
        logger.info(f"🔄 Iniciando consumer dinámico por {duration_minutes} minutos...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        event_count = 0
        last_stats_time = start_time
        
        try:
            for message in self.consumer:
                if time.time() > end_time:
                    break
                
                logger.info(f"📨 Mensaje recibido de topic: {message.topic}")
                self.process_event(message)
                event_count += 1
                
                # Mostrar estadísticas cada 30 segundos
                if time.time() - last_stats_time >= 30:
                    stats = self.get_processing_stats()
                    if stats:
                        logger.info("📊 Estadísticas de procesamiento:")
                        for event_type, count in stats:
                            logger.info(f"   {event_type}: {count} eventos")
                    last_stats_time = time.time()
                
        except KeyboardInterrupt:
            logger.info("⏹️ Consumer detenido por usuario")
        except Exception as e:
            logger.error(f"❌ Error en consumer: {e}")
        finally:
            self.consumer.close()
            self.dwh_conn.close()
            logger.info(f"✅ Consumer finalizado. Total procesados: {event_count} eventos")

def main():
    consumer = DynamicInstaShopKafkaConsumer()
    consumer.run_consumer(duration_minutes=10)

if __name__ == "__main__":
    main()
