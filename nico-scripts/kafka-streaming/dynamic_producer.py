#!/usr/bin/env python3
"""
🚀 Dynamic Kafka Producer - Lee datos frescos de PostgreSQL en tiempo real
Envía datos reales de transacciones y eventos a Kafka
"""

import json
import random
import time
import logging
from datetime import datetime, timedelta
from kafka import KafkaProducer
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

class DynamicInstaShopKafkaProducer:
    def __init__(self):
        # Conectar a Kafka
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Conectar a PostgreSQL
        self.db_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            dbname='instashop',
            user='insta',
            password='insta123'
        )
        
        logger.info("🚀 Dynamic Kafka Producer inicializado")
        
        # Verificar si hay datos en las tablas
        self.check_table_data()
    
    def check_table_data(self):
        """Verificar si hay datos en las tablas"""
        try:
            # Verificar transacciones
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Transaction")
            transaction_count = cursor.fetchone()[0]
            logger.info(f"📊 Total transacciones en DB: {transaction_count}")
            
            # Verificar transacciones recientes
            cursor.execute("SELECT COUNT(*) FROM Transaction WHERE transaction_date >= NOW() - INTERVAL '10 minutes'")
            recent_transactions = cursor.fetchone()[0]
            logger.info(f"📊 Transacciones recientes (10 min): {recent_transactions}")
            
            # Verificar eventos de comportamiento
            crm_conn = psycopg2.connect(
                host='localhost', port=5433, dbname='crm_db', 
                user='crm', password='crm123'
            )
            crm_cursor = crm_conn.cursor()
            crm_cursor.execute("SELECT COUNT(*) FROM Interaction")
            interaction_count = crm_cursor.fetchone()[0]
            logger.info(f"📊 Total interacciones en CRM: {interaction_count}")
            
            crm_cursor.execute("SELECT COUNT(*) FROM Interaction WHERE interaction_date >= NOW() - INTERVAL '10 minutes'")
            recent_interactions = crm_cursor.fetchone()[0]
            logger.info(f"📊 Interacciones recientes (10 min): {recent_interactions}")
            
            cursor.close()
            crm_cursor.close()
            crm_conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error verificando datos de tablas: {e}")
    
    def get_recent_transactions(self, limit=10):
        """Obtener transacciones recientes de PostgreSQL"""
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            # Consulta simple en UTC
            simple_query = """
                SELECT transaction_id, buyer_id, customer_id, transaction_date, 
                       total_amount, payment_method, status
                FROM Transaction 
                WHERE transaction_date >= NOW() - INTERVAL '10 minutes'
                ORDER BY transaction_date DESC
                LIMIT %s
            """
            
            cursor.execute(simple_query, (limit,))
            transactions = cursor.fetchall()
            
            # Enriquecer con datos del comprador y cliente
            enriched_transactions = []
            for t in transactions:
                # Obtener datos del comprador
                buyer_query = "SELECT name, email FROM Buyer WHERE buyer_id = %s"
                cursor.execute(buyer_query, (t['buyer_id'],))
                buyer_data = cursor.fetchone()
                
                # Obtener datos del cliente
                customer_query = "SELECT business_name, subscription_plan FROM Customer WHERE customer_id = %s"
                cursor.execute(customer_query, (t['customer_id'],))
                customer_data = cursor.fetchone()
                
                # Crear transacción enriquecida
                enriched_t = dict(t)
                if buyer_data:
                    enriched_t['buyer_name'] = buyer_data['name']
                    enriched_t['buyer_email'] = buyer_data['email']
                else:
                    enriched_t['buyer_name'] = f"Comprador {t['buyer_id']}"
                    enriched_t['buyer_email'] = f"buyer{t['buyer_id']}@example.com"
                
                if customer_data:
                    enriched_t['customer_name'] = customer_data['business_name']
                    enriched_t['subscription_plan'] = customer_data['subscription_plan']
                else:
                    enriched_t['customer_name'] = f"Cliente {t['customer_id']}"
                    enriched_t['subscription_plan'] = "Free"
                
                enriched_transactions.append(enriched_t)
            
            return enriched_transactions
        except Exception as e:
            logger.error(f"❌ Error obteniendo transacciones: {e}")
            return []
    
    def get_transaction_details(self, transaction_id):
        """Obtener detalles de una transacción específica"""
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT td.quantity, td.unit_price, p.name as product_name, 
                       p.category, p.price as product_price
                FROM TransactionDetail td
                JOIN Product p ON td.product_id = p.product_id
                WHERE td.transaction_id = %s
            """
            cursor.execute(query, (transaction_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ Error obteniendo detalles de transacción: {e}")
            return []
    
    def get_recent_behavior_events(self, limit=10):
        """Obtener eventos de comportamiento recientes del CRM"""
        try:
            # Conectar específicamente al CRM
            crm_conn = psycopg2.connect(
                host='localhost',
                port=5433,
                dbname='crm_db',
                user='crm',
                password='crm123'
            )
            cursor = crm_conn.cursor(cursor_factory=RealDictCursor)
            
            # También necesitamos datos del cliente desde instashop
            instashop_conn = psycopg2.connect(
                host='localhost',
                port=5432,
                dbname='instashop',
                user='insta',
                password='insta123'
            )
            instashop_cursor = instashop_conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT i.interaction_id, i.customer_id, i.interaction_type, 
                       i.channel, i.interaction_date, i.status
                FROM Interaction i
                WHERE i.interaction_date >= NOW() - INTERVAL '10 minutes'
                ORDER BY i.interaction_date DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            interactions = cursor.fetchall()
            
            # Enriquecer con datos del cliente
            enriched_interactions = []
            for interaction in interactions:
                customer_query = """
                    SELECT business_name FROM Customer WHERE customer_id = %s
                """
                instashop_cursor.execute(customer_query, (interaction['customer_id'],))
                customer_data = instashop_cursor.fetchone()
                
                if customer_data:
                    interaction['customer_name'] = customer_data['business_name']
                else:
                    interaction['customer_name'] = f"Cliente {interaction['customer_id']}"
                
                enriched_interactions.append(interaction)
            
            cursor.close()
            instashop_cursor.close()
            crm_conn.close()
            instashop_conn.close()
            
            return enriched_interactions
        except Exception as e:
            logger.error(f"❌ Error obteniendo eventos de comportamiento: {e}")
            return []
    
    def create_transaction_event(self, transaction):
        """Crear evento de transacción para Kafka"""
        details = self.get_transaction_details(transaction['transaction_id'])
        
        event = {
            'event_type': 'transaction',
            'timestamp': transaction['transaction_date'].isoformat(),
            'transaction_id': transaction['transaction_id'],
            'customer_id': transaction['customer_id'],
            'customer_name': transaction['customer_name'],
            'subscription_plan': transaction['subscription_plan'],
            'buyer_id': transaction['buyer_id'],
            'buyer_name': transaction['buyer_name'],
            'buyer_email': transaction['buyer_email'],
            'total_amount': float(transaction['total_amount']),
            'payment_method': transaction['payment_method'],
            'status': transaction['status'],
            'items': [
                {
                    'product_name': detail['product_name'],
                    'category': detail['category'],
                    'quantity': detail['quantity'],
                    'unit_price': float(detail['unit_price']),
                    'product_price': float(detail['product_price'])
                } for detail in details
            ],
            'source': 'postgresql_realtime'
        }
        return event
    
    def create_behavior_event(self, interaction):
        """Crear evento de comportamiento para Kafka"""
        event = {
            'event_type': 'user_behavior',
            'timestamp': interaction['interaction_date'].isoformat(),
            'customer_id': interaction['customer_id'],
            'customer_name': interaction['customer_name'],
            'interaction_type': interaction['interaction_type'],
            'channel': interaction['channel'],
            'status': interaction['status'],
            'source': 'postgresql_realtime'
        }
        return event
    
    def send_event(self, topic, event):
        """Enviar evento a Kafka"""
        try:
            logger.info(f"🔄 Enviando a {topic}: {event['event_type']} - Cliente {event['customer_id']}")
            self.producer.send(topic, value=event, key=str(event['customer_id']))
            self.producer.flush()  # Forzar envío inmediato
            logger.info(f"✅ Enviado exitosamente a {topic}: {event['event_type']} - Cliente {event['customer_id']}")
        except Exception as e:
            logger.error(f"❌ Error enviando a {topic}: {e}")
    
    def run_dynamic_producer(self, duration_minutes=5):
        """Ejecutar producer dinámico que lee datos frescos"""
        logger.info(f"🔄 Iniciando producer dinámico por {duration_minutes} minutos...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        processed_transactions = set()
        processed_interactions = set()
        
        while time.time() < end_time:
            try:
                # Obtener transacciones recientes
                recent_transactions = self.get_recent_transactions(5)
                # Log solo si hay transacciones
                if recent_transactions:
                    logger.info(f"📤 Enviando {len(recent_transactions)} transacciones a Kafka")
                
                for transaction in recent_transactions:
                    if transaction['transaction_id'] not in processed_transactions:
                        event = self.create_transaction_event(transaction)
                        self.send_event('transactions', event)
                        processed_transactions.add(transaction['transaction_id'])
                
                # Obtener eventos de comportamiento recientes
                recent_behaviors = self.get_recent_behavior_events(5)
                # Log solo si hay eventos
                if recent_behaviors:
                    logger.info(f"📤 Enviando {len(recent_behaviors)} eventos de comportamiento a Kafka")
                
                for interaction in recent_behaviors:
                    if interaction['interaction_id'] not in processed_interactions:
                        event = self.create_behavior_event(interaction)
                        self.send_event('user_behavior', event)
                        processed_interactions.add(interaction['interaction_id'])
                
                # Log de progreso cada 10 segundos
                total_processed = len(processed_transactions) + len(processed_interactions)
                if total_processed == 0:
                    # Solo log cada 30 segundos para no spamear
                    if int(time.time()) % 30 == 0:
                        logger.debug("⏳ Esperando datos nuevos...")
                elif total_processed % 10 == 0 and total_processed > 0:
                    logger.info(f"📈 Progreso: {total_processed} eventos procesados ({len(processed_transactions)} transacciones, {len(processed_interactions)} comportamientos)")
                
                # Esperar antes de la siguiente consulta
                time.sleep(2)  # Consultar cada 2 segundos
                
            except KeyboardInterrupt:
                logger.info("⏹️ Producer detenido por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en producer: {e}")
                time.sleep(5)  # Esperar antes de reintentar
        
        logger.info(f"✅ Producer finalizado. Total procesados: {len(processed_transactions)} transacciones, {len(processed_interactions)} comportamientos")
        self.producer.close()
        self.db_conn.close()

def main():
    producer = DynamicInstaShopKafkaProducer()
    producer.run_dynamic_producer(duration_minutes=5)

if __name__ == "__main__":
    main()
