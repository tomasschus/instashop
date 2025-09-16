#!/usr/bin/env python3
"""
🚀 Spark Streaming desde Kafka - Análisis en Tiempo Real
Lee directamente de Kafka topics y procesa datos en tiempo real
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstaShopKafkaStreamingAnalytics:
    def __init__(self):
        # Crear SparkSession con configuración optimizada
        self.spark = SparkSession.builder \
            .appName("InstaShopKafkaStreamingAnalytics") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("🚀 Spark Streaming Analytics inicializado")
    
    def create_kafka_stream(self, topics):
        """Crear stream de Kafka para múltiples topics"""
        try:
            df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "localhost:9092,localhost:9093,localhost:9094") \
                .option("subscribe", ",".join(topics)) \
                .option("startingOffsets", "latest") \
                .option("failOnDataLoss", "false") \
                .load()
            
            logger.info(f"✅ Stream creado para topics: {topics}")
            return df
        except Exception as e:
            logger.error(f"❌ Error creando stream de Kafka: {e}")
            return None
    
    def parse_event_schema(self):
        """Schema para parsear eventos JSON"""
        return StructType([
            StructField("event_type", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("customer_id", IntegerType(), True),
            StructField("customer_name", StringType(), True),
            StructField("subscription_plan", StringType(), True),
            StructField("buyer_id", IntegerType(), True),
            StructField("buyer_name", StringType(), True),
            StructField("product_id", IntegerType(), True),
            StructField("product_name", StringType(), True),
            StructField("category", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("quantity", IntegerType(), True),
            StructField("total_amount", DoubleType(), True),
            StructField("payment_method", StringType(), True),
            StructField("status", StringType(), True),
            StructField("interaction_type", StringType(), True),
            StructField("channel", StringType(), True),
            StructField("session_id", StringType(), True),
            StructField("search_query", StringType(), True),
            StructField("results_count", IntegerType(), True),
            StructField("cart_total", DoubleType(), True),
            StructField("source", StringType(), True)
        ])
    
    def process_transactions_stream(self):
        """Procesar stream de transacciones en tiempo real"""
        logger.info("📊 Procesando stream de transacciones...")
        
        kafka_df = self.create_kafka_stream(["transactions"])
        if kafka_df is None:
            return None
        
        json_schema = self.parse_event_schema()
        
        # Parsear JSON y filtrar transacciones
        parsed_df = kafka_df \
            .select(from_json(col("value").cast("string"), json_schema).alias("data")) \
            .select("data.*") \
            .filter(col("event_type") == "transaction") \
            .filter(col("total_amount").isNotNull())
        
        # Agregaciones en tiempo real con ventanas
        transaction_metrics = parsed_df \
            .withWatermark("timestamp", "2 minutes") \
            .withColumn("timestamp_ts", to_timestamp(col("timestamp"))) \
            .groupBy(window(col("timestamp_ts"), "1 minute")) \
            .agg(
                count("*").alias("transaction_count"),
                sum("total_amount").alias("total_revenue"),
                avg("total_amount").alias("avg_order_value"),
                countDistinct("customer_id").alias("unique_customers"),
                countDistinct("product_id").alias("unique_products"),
                sum("quantity").alias("total_items_sold")
            ) \
            .select(
                col("window.start").alias("time_window"),
                col("transaction_count"),
                col("total_revenue"),
                col("avg_order_value"),
                col("unique_customers"),
                col("unique_products"),
                col("total_items_sold")
            )
        
        return transaction_metrics
    
    def process_behavior_stream(self):
        """Procesar stream de comportamiento de usuarios"""
        logger.info("👥 Procesando stream de comportamiento...")
        
        kafka_df = self.create_kafka_stream(["user_behavior"])
        if kafka_df is None:
            return None
        
        json_schema = self.parse_event_schema()
        
        # Parsear JSON y filtrar eventos de comportamiento
        parsed_df = kafka_df \
            .select(from_json(col("value").cast("string"), json_schema).alias("data")) \
            .select("data.*") \
            .filter(col("event_type") == "user_behavior")
        
        # Agregaciones por tipo de interacción
        behavior_metrics = parsed_df \
            .withWatermark("timestamp", "2 minutes") \
            .withColumn("timestamp_ts", to_timestamp(col("timestamp"))) \
            .groupBy(window(col("timestamp_ts"), "1 minute"), "interaction_type", "channel") \
            .agg(
                count("*").alias("interaction_count"),
                countDistinct("customer_id").alias("unique_users"),
                countDistinct("session_id").alias("unique_sessions")
            ) \
            .select(
                col("window.start").alias("time_window"),
                col("interaction_type"),
                col("channel"),
                col("interaction_count"),
                col("unique_users"),
                col("unique_sessions")
            )
        
        return behavior_metrics
    
    def process_searches_stream(self):
        """Procesar stream de búsquedas"""
        logger.info("🔍 Procesando stream de búsquedas...")
        
        kafka_df = self.create_kafka_stream(["searches"])
        if kafka_df is None:
            return None
        
        json_schema = self.parse_event_schema()
        
        parsed_df = kafka_df \
            .select(from_json(col("value").cast("string"), json_schema).alias("data")) \
            .select("data.*") \
            .filter(col("event_type") == "search") \
            .filter(col("search_query").isNotNull())
        
        # Top términos de búsqueda
        search_metrics = parsed_df \
            .withWatermark("timestamp", "2 minutes") \
            .withColumn("timestamp_ts", to_timestamp(col("timestamp"))) \
            .groupBy(window(col("timestamp_ts"), "1 minute"), "search_query") \
            .agg(
                count("*").alias("search_count"),
                countDistinct("customer_id").alias("unique_searchers"),
                avg("results_count").alias("avg_results")
            ) \
            .select(
                col("window.start").alias("time_window"),
                col("search_query"),
                col("search_count"),
                col("unique_searchers"),
                col("avg_results")
            )
        
        return search_metrics
    
    def process_cart_events_stream(self):
        """Procesar stream de eventos de carrito"""
        logger.info("🛒 Procesando stream de eventos de carrito...")
        
        kafka_df = self.create_kafka_stream(["cart_events"])
        if kafka_df is None:
            return None
        
        json_schema = self.parse_event_schema()
        
        parsed_df = kafka_df \
            .select(from_json(col("value").cast("string"), json_schema).alias("data")) \
            .select("data.*") \
            .filter(col("event_type") == "cart_abandonment") \
            .filter(col("cart_total").isNotNull())
        
        # Métricas de abandono de carrito
        cart_metrics = parsed_df \
            .withWatermark("timestamp", "2 minutes") \
            .withColumn("timestamp_ts", to_timestamp(col("timestamp"))) \
            .groupBy(window(col("timestamp_ts"), "1 minute")) \
            .agg(
                count("*").alias("abandoned_carts"),
                sum("cart_total").alias("lost_revenue"),
                avg("cart_total").alias("avg_cart_value"),
                countDistinct("customer_id").alias("unique_customers_abandoned")
            ) \
            .select(
                col("window.start").alias("time_window"),
                col("abandoned_carts"),
                col("lost_revenue"),
                col("avg_cart_value"),
                col("unique_customers_abandoned")
            )
        
        return cart_metrics
    
    def start_streaming_analytics(self):
        """Iniciar análisis de streaming completo"""
        logger.info("🚀 Iniciando análisis de streaming completo...")
        
        try:
            # Crear streams para cada tipo de evento
            transaction_stream = self.process_transactions_stream()
            behavior_stream = self.process_behavior_stream()
            search_stream = self.process_searches_stream()
            cart_stream = self.process_cart_events_stream()
            
            if transaction_stream is None:
                logger.error("❌ No se pudo crear stream de transacciones")
                return
            
            # Configurar queries de salida
            queries = []
            
            # Query para transacciones
            if transaction_stream:
                transaction_query = transaction_stream \
                    .writeStream \
                    .outputMode("update") \
                    .format("console") \
                    .option("truncate", False) \
                    .option("numRows", 20) \
                    .trigger(processingTime="30 seconds") \
                    .start()
                queries.append(transaction_query)
                logger.info("✅ Stream de transacciones iniciado")
            
            # Query para comportamiento
            if behavior_stream:
                behavior_query = behavior_stream \
                    .writeStream \
                    .outputMode("update") \
                    .format("console") \
                    .option("truncate", False) \
                    .option("numRows", 20) \
                    .trigger(processingTime="30 seconds") \
                    .start()
                queries.append(behavior_query)
                logger.info("✅ Stream de comportamiento iniciado")
            
            # Query para búsquedas
            if search_stream:
                search_query = search_stream \
                    .writeStream \
                    .outputMode("update") \
                    .format("console") \
                    .option("truncate", False) \
                    .option("numRows", 20) \
                    .trigger(processingTime="30 seconds") \
                    .start()
                queries.append(search_query)
                logger.info("✅ Stream de búsquedas iniciado")
            
            # Query para carrito
            if cart_stream:
                cart_query = cart_stream \
                    .writeStream \
                    .outputMode("update") \
                    .format("console") \
                    .option("truncate", False) \
                    .option("numRows", 20) \
                    .trigger(processingTime="30 seconds") \
                    .start()
                queries.append(cart_query)
                logger.info("✅ Stream de carrito iniciado")
            
            logger.info("🎯 Todos los streams iniciados. Presiona Ctrl+C para detener...")
            
            # Esperar terminación de todos los queries
            for query in queries:
                query.awaitTermination()
            
        except KeyboardInterrupt:
            logger.info("⏹️ Streaming detenido por usuario")
        except Exception as e:
            logger.error(f"❌ Error en streaming: {e}")
        finally:
            # Detener todos los queries
            for query in queries:
                try:
                    query.stop()
                except:
                    pass
            
            self.spark.stop()
            logger.info("✅ Spark Streaming finalizado")

def main():
    analytics = InstaShopKafkaStreamingAnalytics()
    analytics.start_streaming_analytics()

if __name__ == "__main__":
    main()
