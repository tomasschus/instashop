#!/usr/bin/env python3
"""
🔧 PostgreSQL CDC Initialization Script
Configura PostgreSQL para Change Data Capture (CDC) con Debezium
"""

import psycopg2
import logging
import time
from dataclasses import dataclass
from typing import List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    name: str
    host: str
    port: int
    user: str
    password: str
    dbname: str
    tables: List[str]
    slot_name: str
    publication_name: str

class PostgresCDCInitializer:
    def __init__(self):
        self.databases = [
            DatabaseConfig(
                name="InstashopDB",
                host="localhost",
                port=5432,
                user="insta",
                password="insta123",
                dbname="instashop",
                tables=["transaction", "transactiondetail", "customer", "product"],
                slot_name="instashop_slot",
                publication_name="instashop_publication"
            ),
            DatabaseConfig(
                name="CRM DB",
                host="localhost",
                port=5433,
                user="crm",
                password="crm123",
                dbname="crm_db",
                tables=["interaction", "segment", "customersegment"],
                slot_name="crm_slot",
                publication_name="crm_publication"
            ),
            DatabaseConfig(
                name="ERP DB",
                host="localhost",
                port=5434,
                user="erp",
                password="erp123",
                dbname="erp_db",
                tables=["stock", "inventorymovement"],
                slot_name="erp_slot",
                publication_name="erp_publication"
            ),
            DatabaseConfig(
                name="E-commerce DB",
                host="localhost",
                port=5435,
                user="ecommerce",
                password="ecommerce123",
                dbname="ecommerce_db",
                tables=["carrier", "shipment"],
                slot_name="ecommerce_slot",
                publication_name="ecommerce_publication"
            )
        ]

    def wait_for_database(self, config: DatabaseConfig, max_retries=30):
        """Espera a que la base de datos esté disponible"""
        logger.info(f"⏳ Esperando conexión a {config.name}...")
        
        for attempt in range(max_retries):
            try:
                conn = psycopg2.connect(
                    host=config.host,
                    port=config.port,
                    user=config.user,
                    password=config.password,
                    dbname=config.dbname,
                    connect_timeout=5
                )
                conn.close()
                logger.info(f"✅ {config.name} disponible")
                return True
            except psycopg2.Error:
                time.sleep(2)
                
        logger.error(f"❌ {config.name} no disponible después de {max_retries} intentos")
        return False

    def check_table_exists(self, cursor, table_name):
        """Verifica si una tabla existe"""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (table_name,))
        return cursor.fetchone()[0]

    def create_publication(self, cursor, config: DatabaseConfig):
        """Crea la publicación para CDC"""
        try:
            # Verificar si la publicación ya existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_publication 
                    WHERE pubname = %s
                );
            """, (config.publication_name,))
            
            publication_exists = cursor.fetchone()[0]
            
            if publication_exists:
                logger.info(f"📰 Eliminando publicación existente: {config.publication_name}")
                cursor.execute(f"DROP PUBLICATION {config.publication_name};")
            
            # Verificar que las tablas existen
            existing_tables = []
            for table in config.tables:
                if self.check_table_exists(cursor, table):
                    existing_tables.append(f"public.{table}")
                else:
                    logger.warning(f"⚠️  Tabla {table} no existe en {config.name}")
            
            if not existing_tables:
                logger.error(f"❌ No hay tablas válidas para publicación en {config.name}")
                return False
                
            # Crear publicación
            tables_list = ", ".join(existing_tables)
            create_pub_sql = f"CREATE PUBLICATION {config.publication_name} FOR TABLE {tables_list};"
            cursor.execute(create_pub_sql)
            
            logger.info(f"✅ Publicación {config.publication_name} creada con tablas: {tables_list}")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"❌ Error creando publicación en {config.name}: {e}")
            return False

    def create_replication_slot(self, cursor, config: DatabaseConfig):
        """Crea el slot de replicación para Debezium"""
        try:
            # Verificar si el slot ya existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_replication_slots 
                    WHERE slot_name = %s
                );
            """, (config.slot_name,))
            
            slot_exists = cursor.fetchone()[0]
            
            if slot_exists:
                logger.info(f"🔌 Eliminando slot existente: {config.slot_name}")
                cursor.execute(f"SELECT pg_drop_replication_slot('{config.slot_name}');")
            
            # Crear nuevo slot
            cursor.execute(f"""
                SELECT pg_create_logical_replication_slot(
                    '{config.slot_name}', 
                    'pgoutput'
                );
            """)
            
            logger.info(f"✅ Slot de replicación {config.slot_name} creado")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"❌ Error creando slot en {config.name}: {e}")
            return False

    def setup_database_cdc(self, config: DatabaseConfig):
        """Configura CDC para una base de datos específica"""
        logger.info(f"\n🔧 Configurando CDC para {config.name}")
        
        if not self.wait_for_database(config):
            return False
            
        try:
            conn = psycopg2.connect(
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                dbname=config.dbname
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Verificar configuración de WAL
            cursor.execute("SHOW wal_level;")
            wal_level = cursor.fetchone()[0]
            logger.info(f"📊 WAL Level: {wal_level}")
            
            if wal_level != 'logical':
                logger.warning(f"⚠️  WAL level debería ser 'logical', está en '{wal_level}'")
            
            # Crear publicación y slot
            pub_success = self.create_publication(cursor, config)
            slot_success = self.create_replication_slot(cursor, config)
            
            cursor.close()
            conn.close()
            
            if pub_success and slot_success:
                logger.info(f"✅ CDC configurado exitosamente para {config.name}")
                return True
            else:
                logger.error(f"❌ Falló la configuración CDC para {config.name}")
                return False
                
        except psycopg2.Error as e:
            logger.error(f"❌ Error conectando a {config.name}: {e}")
            return False

    def setup_all_databases(self):
        """Configura CDC para todas las bases de datos"""
        logger.info("🚀 Iniciando configuración CDC para todas las bases de datos")
        
        success_count = 0
        total_count = len(self.databases)
        
        for db_config in self.databases:
            if self.setup_database_cdc(db_config):
                success_count += 1
                
        logger.info(f"\n📈 Resumen: {success_count}/{total_count} bases configuradas exitosamente")
        return success_count == total_count

def main():
    initializer = PostgresCDCInitializer()
    
    if initializer.setup_all_databases():
        logger.info("🎉 ¡Configuración CDC completada exitosamente!")
        return 0
    else:
        logger.error("💥 Falló la configuración CDC")
        return 1

if __name__ == "__main__":
    exit(main())
