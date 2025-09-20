#!/usr/bin/env python3
"""
🏢 CDC DWH Consumer - Consume eventos CDC y los almacena en Data Warehouse
PostgreSQL → CDC (Debezium) → Kafka → Este script → Data Warehouse
"""

import json
import time
import psycopg2
import logging
from kafka import KafkaConsumer
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import signal
import sys
import base64
import struct

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CDCDWHConsumer:
    def __init__(self):
        """Inicializa el consumer CDC a DWH"""
        self.dwh_conn = self._setup_dwh_connection()
        self.consumer = self._setup_kafka_consumer()
        self.running = True
        
        # Contadores
        self.stats = {
            'total_events_processed': 0,
            'transactions_processed': 0,
            'customers_processed': 0,
            'products_processed': 0,
            'errors': 0,
            'start_time': datetime.now(timezone.utc)
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Crear tabla si no existe
        self._ensure_dwh_table()
    
    def _decode_decimal_bytes(self, byte_string: str) -> float:
        """Decodifica un decimal de Debezium que viene como bytes"""
        try:
            # Debezium envía decimales como base64 o string bytes
            if isinstance(byte_string, str) and len(byte_string) == 4:
                # Para valores pequeños, parece ser un encoding específico
                # Convertir cada carácter a su valor ASCII y computar
                decoded = 0
                for i, char in enumerate(byte_string):
                    decoded += ord(char) * (256 ** (3 - i))
                return decoded / 100.0  # scale=2 según el schema
            else:
                # Fallback para otros casos
                return float(byte_string) if byte_string else 0.0
        except Exception:
            return 0.0
        
    def _setup_dwh_connection(self):
        """Configura conexión al Data Warehouse"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5436,
                dbname='dwh_db',
                user='dwh',
                password='dwh123'
            )
            conn.autocommit = True
            logger.info("✅ Conexión al DWH establecida")
            return conn
        except Exception as e:
            logger.error(f"❌ Error conectando al DWH: {e}")
            raise
    
    def _setup_kafka_consumer(self):
        """Configura consumer de Kafka para tópicos CDC"""
        try:
            consumer = KafkaConsumer(
                'transaction',
                'customer', 
                'product',
                'transactiondetail',
                'interaction',
                'stock',
                'carrier',
                'shipment',
                bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=f'cdc-dwh-consumer-{int(time.time())}',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                consumer_timeout_ms=1000,
                api_version=(2, 6, 0)
            )
            logger.info("✅ Consumer Kafka CDC configurado")
            logger.info(f"📋 Tópicos CDC suscritos: {list(consumer.subscription())}")
            return consumer
        except Exception as e:
            logger.error(f"❌ Error configurando consumer Kafka: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de interrupción"""
        logger.info(f"🛑 Señal {signum} recibida, cerrando gracefully...")
        self.running = False
    
    def _ensure_dwh_table(self):
        """Verificar que la tabla realtime_events existe"""
        try:
            cursor = self.dwh_conn.cursor()
            
            # Solo verificar que la tabla existe, no modificarla
            cursor.execute("SELECT COUNT(*) FROM realtime_events LIMIT 1;")
            cursor.close()
            logger.info("✅ Tabla realtime_events verificada en DWH")
            
        except Exception as e:
            logger.error(f"❌ Error verificando tabla DWH: {e}")
            raise
    
    def _process_cdc_event(self, topic: str, message: Dict[str, Any]) -> None:
        """Procesa evento CDC y lo inserta en DWH"""
        try:
            # Estructura CDC de Debezium
            payload = message.get('payload', {})
            operation = payload.get('op')  # c=create, u=update, d=delete, r=read
            after = payload.get('after', {})
            source = payload.get('source', {})
            ts_ms = payload.get('ts_ms', int(time.time() * 1000))
            
            table_name = source.get('table', topic)
            
            # Extraer IDs según la tabla y mapear a event_type compatible con dashboard
            record_id = None
            customer_id = None
            transaction_id = None
            product_id = None
            
            if table_name == 'transaction':
                record_id = after.get('transaction_id')
                transaction_id = record_id
                customer_id = after.get('customer_id') or after.get('buyer_id')
                event_type = 'transaction'  # Dashboard espera este tipo
                
            elif table_name == 'customer':
                record_id = after.get('customer_id')
                customer_id = record_id
                event_type = 'user_behavior'  # Dashboard espera este tipo para métricas generales
                
            elif table_name == 'product':
                record_id = after.get('product_id')
                product_id = record_id
                event_type = 'user_behavior'  # Mapear a user_behavior para que aparezca en gráficos
                
            elif table_name == 'transactiondetail':
                record_id = after.get('transactiondetailid') or after.get('id')
                transaction_id = after.get('transaction_id')
                product_id = after.get('product_id')
                event_type = 'transaction'  # Asociar con transacciones
                
            else:
                # Otros tipos (interaction, stock, carrier, shipment) - mapear a user_behavior
                record_id = after.get('id') or after.get(f'{table_name}id')
                customer_id = after.get('customer_id')  # Intentar extraer customer_id si existe
                event_type = 'user_behavior'  # Dashboard espera este tipo
            
            # Convertir timestamp CDC a datetime
            event_timestamp = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            
            # Insertar en DWH
            self._insert_to_dwh(
                event_type=event_type,
                table_name=table_name,
                operation=operation,
                record_id=record_id,
                customer_id=customer_id,
                transaction_id=transaction_id,
                product_id=product_id,
                event_data=after,
                timestamp=event_timestamp
            )
            
            # Actualizar contadores
            self.stats['total_events_processed'] += 1
            
            if event_type == 'transaction':
                self.stats['transactions_processed'] += 1
            elif event_type == 'customer':
                self.stats['customers_processed'] += 1
            elif event_type == 'product':
                self.stats['products_processed'] += 1
            
            logger.info(f"📥 {event_type.upper()} CDC: {operation} - ID:{record_id}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando evento CDC: {e}")
            self.stats['errors'] += 1
    
    def _insert_to_dwh(self, event_type: str, table_name: str, operation: str,
                       record_id: Optional[int], customer_id: Optional[int],
                       transaction_id: Optional[int], product_id: Optional[int],
                       event_data: Dict[str, Any], timestamp: datetime) -> None:
        """Insertar evento en la tabla realtime_events del DWH (esquema existente)"""
        try:
            cursor = self.dwh_conn.cursor()
            
            # Adaptar al esquema existente
            customer_name = event_data.get('name', '') if table_name == 'customer' else None
            product_name = event_data.get('name', '') if table_name == 'product' else None
            category = event_data.get('category', '') if table_name == 'product' else None
            amount = None
            
            if table_name == 'transaction':
                # Decodificar total_amount que viene como bytes
                total_amount_bytes = event_data.get('total_amount')
                if total_amount_bytes:
                    amount = self._decode_decimal_bytes(total_amount_bytes)
                    logger.info(f"💰 Decodificado amount: {total_amount_bytes} -> ${amount}")
                else:
                    amount = 0.0
            elif table_name == 'transactiondetail':
                # Para transaction details, usar price * quantity si está disponible
                price = event_data.get('price', 0)
                quantity = event_data.get('quantity', 1)
                if isinstance(price, str):
                    price = self._decode_decimal_bytes(price)
                amount = float(price) * float(quantity) if price else 0.0
            
            # Generar session_id simple basado en customer_id
            session_id = f"cdc_session_{customer_id}" if customer_id else None
            
            insert_query = """
            INSERT INTO realtime_events (
                event_type, timestamp, customer_id, customer_name,
                product_id, product_name, category, amount,
                session_id, raw_data, processed_at, source
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            cursor.execute(insert_query, (
                event_type,
                timestamp,
                customer_id,
                customer_name,
                product_id,
                product_name,
                category,
                amount,
                session_id,
                json.dumps(event_data),
                datetime.now(timezone.utc),
                'cdc_debezium'
            ))
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Error insertando en DWH: {e}")
            raise
    
    def _log_stats(self) -> None:
        """Log estadísticas del consumer"""
        runtime = datetime.now(timezone.utc) - self.stats['start_time']
        
        logger.info("📊 === ESTADÍSTICAS CDC DWH CONSUMER ===")
        logger.info(f"⏰ Tiempo ejecutándose: {runtime}")
        logger.info(f"📈 Total eventos procesados: {self.stats['total_events_processed']}")
        logger.info(f"💳 Transacciones: {self.stats['transactions_processed']}")
        logger.info(f"👥 Clientes: {self.stats['customers_processed']}")
        logger.info(f"📦 Productos: {self.stats['products_processed']}")
        logger.info(f"❌ Errores: {self.stats['errors']}")
        
        if runtime.total_seconds() > 0:
            rate = self.stats['total_events_processed'] / runtime.total_seconds()
            logger.info(f"⚡ Tasa: {rate:.2f} eventos/segundo")
        
        logger.info("=" * 50)
    
    def run(self) -> None:
        """Ejecuta el loop principal del consumer"""
        logger.info("🚀 CDC DWH Consumer iniciado")
        logger.info("🏢 Escribiendo eventos CDC al Data Warehouse...")
        
        last_stats_time = time.time()
        
        try:
            while self.running:
                try:
                    # Poll por mensajes CDC
                    message_pack = self.consumer.poll(timeout_ms=1000)
                    
                    if message_pack:
                        for topic_partition, messages in message_pack.items():
                            for message in messages:
                                if message.value:
                                    self._process_cdc_event(
                                        topic_partition.topic,
                                        message.value
                                    )
                    
                    # Log estadísticas cada 30 segundos
                    current_time = time.time()
                    if current_time - last_stats_time >= 30:
                        self._log_stats()
                        last_stats_time = current_time
                    
                    # Heartbeat cuando no hay mensajes
                    if not message_pack and int(time.time()) % 30 == 0:
                        logger.info(f"💓 CDC DWH Consumer activo - {self.stats['total_events_processed']} eventos procesados")
                        time.sleep(1)  # Evitar spam
                        
                except Exception as e:
                    logger.error(f"❌ Error en loop principal: {e}")
                    self.stats['errors'] += 1
                    time.sleep(5)  # Wait before retry
                    
        except KeyboardInterrupt:
            logger.info("🛑 Interrupción por teclado")
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Limpia recursos al cerrar"""
        try:
            logger.info("🧹 Limpiando recursos...")
            
            # Log estadísticas finales
            self._log_stats()
            
            # Cerrar consumer
            if hasattr(self, 'consumer'):
                self.consumer.close()
                
            # Cerrar conexión DWH
            if hasattr(self, 'dwh_conn'):
                self.dwh_conn.close()
                
            logger.info("✅ Cleanup completado")
            
        except Exception as e:
            logger.error(f"❌ Error en cleanup: {e}")

def main():
    """Función principal"""
    try:
        consumer = CDCDWHConsumer()
        consumer.run()
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
