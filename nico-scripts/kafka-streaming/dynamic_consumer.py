#!/usr/bin/env python3
"""
🚀 Dynamic Kafka Consumer - Lee de Kafka y procesa hacia DWH
Procesa eventos en tiempo real y los almacena en Data Warehouse
"""

import json
import time
import logging
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
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
            group_id='instashop-dynamic-group-new',
            auto_offset_reset='latest',  # Solo mensajes nuevos
            enable_auto_commit=True,
            auto_commit_interval_ms=1000
        )
        
        # Conectar a Kafka Producer para enviar eventos procesados
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
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
            
            # Agregar columna source si no existe (para tablas existentes)
            try:
                alter_table_sql = "ALTER TABLE realtime_events ADD COLUMN IF NOT EXISTS source VARCHAR(50) DEFAULT 'kafka_consumer';"
                cursor.execute(alter_table_sql)
                logger.info("✅ Columna 'source' verificada/agregada")
            except Exception as alter_error:
                logger.warning(f"⚠️ Advertencia al verificar columna source: {alter_error}")
            
            self.dwh_conn.commit()
            cursor.close()
            
            logger.info("✅ Tabla realtime_events creada/actualizada en DWH")
        except Exception as e:
            logger.error(f"❌ Error creando tabla: {e}")
    
    def process_transaction_event(self, event):
        """Procesar evento de transacción"""
        try:
            cursor = self.dwh_conn.cursor()
            
            # Insertar evento principal de transacción
            insert_sql = """
            INSERT INTO realtime_events 
            (event_type, timestamp, customer_id, customer_name, product_id, product_name, 
             category, amount, raw_data, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Extraer datos del evento
            customer_id = event.get('customer_id')
            customer_name = event.get('customer_name')
            amount = event.get('total_amount')
            
            cursor.execute(insert_sql, (
                event['event_type'],
                datetime.fromisoformat(event['timestamp']),
                customer_id,
                customer_name,
                None,  # product_id para transacción principal
                None,  # product_name para transacción principal
                None,  # category para transacción principal
                amount,
                json.dumps(event),
                'kafka_consumer'
            ))
            
            # Insertar eventos individuales para cada item
            items = event.get('items', [])
            for item in items:
                item_insert_sql = """
                INSERT INTO realtime_events 
                (event_type, timestamp, customer_id, customer_name, product_id, product_name, 
                 category, amount, raw_data, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(item_insert_sql, (
                    'transaction_item',
                    datetime.fromisoformat(event['timestamp']),
                    customer_id,
                    customer_name,
                    item.get('product_id'),
                    item.get('product_name'),
                    item.get('category'),
                    item.get('product_price', 0),
                    json.dumps(item),
                    'kafka_consumer'
                ))
                
                # Enviar evento transaction_item enriquecido a Kafka para Spark
                transaction_item_event = {
                    'event_type': 'transaction_item',
                    'timestamp': event['timestamp'],
                    'transaction_id': event['transaction_id'],
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'customer_subscription': event.get('subscription_plan'),
                    'buyer_id': event.get('buyer_id'),
                    'buyer_name': event.get('buyer_name'),
                    'buyer_email': event.get('buyer_email'),
                    'product_id': item.get('product_id'),
                    'product_name': item.get('product_name'),
                    'category': item.get('category'),
                    'amount': item.get('product_price', 0),
                    'quantity': item.get('quantity', 1),
                    'unit_price': item.get('unit_price', 0),
                    'total_transaction_amount': event.get('total_amount', 0),
                    'payment_method': event.get('payment_method'),
                    'transaction_status': event.get('status'),
                    'source': 'kafka_consumer'
                }
                
                self.producer.send('transaction_items', value=transaction_item_event)
                logger.info(f"📤 Enviado transaction_item a Kafka: {item.get('product_name')} ({item.get('category')})")
            
            self.dwh_conn.commit()
            cursor.close()
            
            logger.info(f"✅ Transacción procesada: {customer_name} - ${amount} ({len(items)} items)")
            
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
        
        logger.info(f"🔄 Procesando evento: {event_type} desde topic {topic}")
        
        try:
            if event_type == 'transaction':
                logger.debug("💰 Procesando transacción...")
                self.process_transaction_event(event)
            elif event_type == 'user_behavior':
                logger.debug("👤 Procesando comportamiento de usuario...")
                self.process_behavior_event(event)
            elif event_type == 'search':
                logger.debug("🔍 Procesando búsqueda...")
                self.process_search_event(event)
            elif event_type == 'cart_abandonment':
                logger.debug("🛒 Procesando evento de carrito...")
                self.process_cart_event(event)
            else:
                logger.warning(f"⚠️ Tipo de evento desconocido: {event_type} en topic {topic}")
                
        except Exception as e:
            logger.error(f"❌ Error procesando evento: {e}")
            logger.error(f"❌ Evento que falló: {event}")
    
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
            logger.info("🔍 Esperando mensajes de Kafka...")
            logger.info("📋 Topics suscritos: transactions, user_behavior, searches, cart_events")
            logger.info("⏰ Consumer ejecutándose hasta que se reciban datos o se presione Ctrl+C")
            
            # Log de heartbeat cada 10 segundos
            heartbeat_time = time.time()
            
            while time.time() < end_time:
                # Heartbeat cada 10 segundos
                if time.time() - heartbeat_time >= 10:
                    logger.info("💓 Consumer activo - esperando mensajes...")
                    heartbeat_time = time.time()
                
                # Intentar obtener mensaje con timeout
                try:
                    message = self.consumer.poll(timeout_ms=5000)  # 5 segundos timeout
                    if message is None:
                        continue
                    
                    for topic_partition, messages in message.items():
                        for msg in messages:
                            logger.info(f"📨 Mensaje recibido de topic: {msg.topic}, offset: {msg.offset}")
                            logger.debug(f"📄 Contenido del mensaje: {msg.value}")
                            
                            self.process_event(msg)
                            event_count += 1
                            
                            logger.info(f"✅ Evento #{event_count} procesado exitosamente")
                            
                except Exception as e:
                    logger.error(f"❌ Error en poll: {e}")
                    time.sleep(1)
                
                # Mostrar estadísticas cada 30 segundos
                if time.time() - last_stats_time >= 30:
                    stats = self.get_processing_stats()
                    if stats:
                        logger.info("📊 Estadísticas de procesamiento:")
                        for event_type, count in stats:
                            logger.info(f"   {event_type}: {count} eventos")
                    else:
                        logger.info("📊 No hay eventos procesados aún")
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
