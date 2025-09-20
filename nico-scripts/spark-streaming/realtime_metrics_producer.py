#!/usr/bin/env python3
"""
🚀 Spark Streaming + Redis - Productor de Métricas en Tiempo Real
Lee de Kafka, procesa con Spark, y envía métricas a Redis para Streamlit
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.types import TimestampType
import json
import redis
import logging
from datetime import datetime, timezone

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealtimeMetricsProducer:
    def __init__(self):
        # Crear SparkSession
        self.spark = SparkSession.builder \
            .appName("InstaShopRealtimeMetrics") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Conectar a Redis
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Schema para parsing de JSON
        self.event_schema = StructType([
            StructField("event_type", StringType(), True),
            StructField("transaction_id", IntegerType(), True),
            StructField("customer_id", IntegerType(), True),
            StructField("total_amount", DoubleType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("session_id", StringType(), True),
            StructField("product_id", IntegerType(), True),
            StructField("product_name", StringType(), True),
            StructField("search_term", StringType(), True),
            StructField("category", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("quantity", IntegerType(), True),  # Agregar quantity al schema principal
            StructField("unit_price", DoubleType(), True),  # Agregar unit_price al schema principal
            StructField("source", StringType(), True),
            StructField("items", ArrayType(StructType([
                StructField("product_name", StringType(), True),
                StructField("category", StringType(), True),
                StructField("quantity", IntegerType(), True),
                StructField("unit_price", DoubleType(), True),
                StructField("product_price", DoubleType(), True)
            ])), True)
        ])
        
        logger.info("🚀 Realtime Metrics Producer inicializado")
    
    def create_kafka_stream(self, topics):
        """Crear stream de Kafka"""
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092,localhost:9093,localhost:9094") \
            .option("subscribe", ",".join(topics)) \
                .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        return df.selectExpr("CAST(value AS STRING) as json_value")
    
    def parse_json_events(self, df):
        """Parsear eventos JSON del stream"""
        return df.select(
            from_json(col("json_value"), self.event_schema).alias("data")
        ).select("data.*").withColumn(
            "timestamp", 
            col("timestamp").cast("timestamp")
        )
    
    def process_transaction_metrics(self, df):
        """Procesar métricas de transacciones"""
        return df.filter(col("event_type") == "transaction") \
            .withWatermark("timestamp", "10 seconds") \
            .groupBy(window(col("timestamp"), "30 seconds")) \
            .agg(
                count("*").alias("transaction_count"),
                sum("total_amount").alias("total_revenue"),
                avg("total_amount").alias("avg_transaction_value"),
                approx_count_distinct("customer_id").alias("unique_customers"),
                max("total_amount").alias("max_transaction"),
                min("total_amount").alias("min_transaction")
            )
    
    def process_behavior_metrics(self, df):
        """Procesar métricas de comportamiento"""
        return df.filter(col("event_type") != "transaction") \
            .withWatermark("timestamp", "10 seconds") \
            .groupBy(window(col("timestamp"), "30 seconds"), col("event_type")) \
            .agg(count("*").alias("event_count"))
    
    def process_product_metrics(self, df):
        """Procesar métricas de productos"""
        # Procesar eventos de transaction_item de Kafka
        product_df = df.filter(col("event_type") == "transaction_item")
        
        return product_df \
            .withWatermark("timestamp", "10 seconds") \
            .groupBy(window(col("timestamp"), "30 seconds"), col("category")) \
            .agg(
                count("*").alias("product_sales"),
                sum("amount").alias("category_revenue"),
                avg("amount").alias("avg_category_value"),
                sum("quantity").alias("total_quantity"),
                approx_count_distinct("customer_id").alias("unique_customers"),
                approx_count_distinct("product_id").alias("unique_products")
            )
    
    def write_to_redis(self, df, epoch_id):
        """Escribir métricas a Redis"""
        try:
            # Recopilar datos del DataFrame
            rows = df.collect()
            
            logger.info(f"🔄 Procesando batch {epoch_id} con {len(rows)} filas")
            
            current_time = datetime.now(timezone.utc).isoformat()
            
            for row in rows:
                logger.info(f"📄 Procesando fila: {row.asDict()}")
                
                # Métricas de transacciones
                if 'transaction_count' in row.asDict():
                    metrics = {
                        'timestamp': current_time,
                        'transaction_count': row['transaction_count'],
                        'total_revenue': float(row['total_revenue']) if row['total_revenue'] else 0,
                        'avg_transaction_value': float(row['avg_transaction_value']) if row['avg_transaction_value'] else 0,
                        'unique_customers': row['unique_customers'],
                        'max_transaction': float(row['max_transaction']) if row['max_transaction'] else 0,
                        'min_transaction': float(row['min_transaction']) if row['min_transaction'] else 0
                    }
                    
                    # Guardar en Redis con TTL de 1 hora
                    self.redis_client.setex(
                        "metrics:transactions", 
                        3600, 
                        json.dumps(metrics)
                    )
                    
                    logger.info(f"📊 Métricas de transacciones actualizadas: {metrics}")
                
                # Métricas de comportamiento
                elif 'event_count' in row.asDict():
                    event_type = row['event_type']
                    event_count = row['event_count']
                    
                    # Guardar métricas por tipo de evento
                    behavior_key = f"metrics:behavior:{event_type}"
                    self.redis_client.setex(
                        behavior_key,
                        3600,
                        json.dumps({
                            'timestamp': current_time,
                            'event_type': event_type,
                            'event_count': event_count
                        })
                    )
                    
                    logger.info(f"📊 Métricas de comportamiento actualizadas: {event_type} = {event_count}")
                
                # Métricas de productos/categorías
                elif 'product_sales' in row.asDict():
                    category = row['category']
                    product_metrics = {
                        'timestamp': current_time,
                        'category': category,
                        'product_sales': row['product_sales'],
                        'category_revenue': float(row['category_revenue']) if row['category_revenue'] else 0,
                        'avg_category_value': float(row['avg_category_value']) if row['avg_category_value'] else 0,
                        'total_quantity': row['total_quantity'],
                        'unique_customers': row['unique_customers'],
                        'unique_products': row['unique_products']
                    }
                    
                    # Guardar métricas de productos
                    product_key = f"metrics:products:{category}"
                    self.redis_client.setex(
                        product_key,
                        3600,
                        json.dumps(product_metrics)
                    )
                    
                    logger.info(f"📊 Métricas de productos actualizadas: {category} = {product_metrics}")
            
            if not rows:
                logger.info("📊 No hay datos en este batch")
            
        except Exception as e:
            logger.error(f"❌ Error escribiendo a Redis: {e}")
            import traceback
            traceback.print_exc()
    
    def start_streaming(self):
        """Iniciar el streaming de métricas"""
        try:
            # Crear stream de Kafka
            kafka_stream = self.create_kafka_stream([
                "transactions", "user_behavior", "searches", "cart_events", "transaction_items"
            ])
            
            # Parsear eventos
            events_df = self.parse_json_events(kafka_stream)
            
            # Procesar métricas de transacciones
            transaction_metrics = self.process_transaction_metrics(events_df)
            
            # Procesar métricas de comportamiento
            behavior_metrics = self.process_behavior_metrics(events_df)
            
            # Procesar métricas de productos
            product_metrics = self.process_product_metrics(events_df)
            
            # Escribir métricas a Redis
            transaction_query = transaction_metrics \
                .writeStream \
                .outputMode("update") \
                .foreachBatch(self.write_to_redis) \
                .trigger(processingTime='30 seconds') \
                .start()
            
            behavior_query = behavior_metrics \
                .writeStream \
                .outputMode("update") \
                .foreachBatch(self.write_to_redis) \
                .trigger(processingTime='30 seconds') \
                .start()
            
            product_query = product_metrics \
                .writeStream \
                .outputMode("update") \
                .foreachBatch(self.write_to_redis) \
                .trigger(processingTime='30 seconds') \
                .start()
            
            logger.info("🚀 Streaming de métricas iniciado")
            logger.info("📊 Esperando datos de Kafka para procesar...")
            
            # Esperar terminación
            transaction_query.awaitTermination()
            behavior_query.awaitTermination()
            product_query.awaitTermination()
            
        except Exception as e:
            logger.error(f"❌ Error en streaming: {e}")
        finally:
            self.spark.stop()

def main():
    producer = RealtimeMetricsProducer()
    producer.start_streaming()

if __name__ == "__main__":
    main()
