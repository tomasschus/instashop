#!/usr/bin/env python3
"""
CDC Spark Redis - Procesamiento completo de métricas
CDC → Spark → Redis con métricas significativas
"""

import json
import redis
import base64
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, count, sum as spark_sum, avg, 
    window, approx_count_distinct, lit, when, 
    expr, current_timestamp
)
from pyspark.sql.types import StructType, StructField, StringType, MapType

# Crear SparkSession con configuración Kafka
spark = SparkSession.builder \
    .appName("CDCSparkRedis") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/cdc-spark-checkpoint") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Cliente Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def decode_decimal_amount(amount_bytes_str):
    """Decodificar amount de Debezium (bytes → decimal)"""
    try:
        if not amount_bytes_str:
            return 0.0
        # Decodificar base64 y convertir a decimal
        amount_bytes = base64.b64decode(amount_bytes_str)
        # Convertir bytes a int y dividir por 100 (2 decimales)
        amount_int = int.from_bytes(amount_bytes, byteorder='big', signed=True)
        return amount_int / 100.0
    except:
        return 0.0

def process_transactions_batch(df, batch_id):
    """Procesar transacciones CDC y calcular métricas significativas"""
    print(f"🔄 Procesando batch {batch_id} - Transacciones")
    
    try:
        if df.count() == 0:
            print(f"⚠️  Batch {batch_id} vacío")
            return
        
        # Parsear JSON de Kafka
        parsed_df = df.select(
            from_json(col("value").cast("string"), 
                     StructType([
                         StructField("payload", StructType([
                             StructField("after", MapType(StringType(), StringType())),
                             StructField("op", StringType())
                         ]))
                     ])).alias("data")
        ).select("data.payload.*")
        
        # Filtrar solo eventos CREATE/UPDATE de transacciones
        transaction_events = parsed_df.filter(
            (col("op") == "c") | (col("op") == "u")
        ).filter(
            col("after").isNotNull()
        )
        
        if transaction_events.count() == 0:
            print("⚠️  No hay eventos de transacciones válidos")
            return
        
        # Extraer datos de transacciones
        transactions = transaction_events.select(
            col("after")["transaction_id"].alias("transaction_id"),
            col("after")["customer_id"].alias("customer_id"),
            col("after")["total_amount"].alias("total_amount_raw"),
            col("after")["payment_method"].alias("payment_method"),
            col("after")["status"].alias("status")
        ).filter(
            col("transaction_id").isNotNull()
        )
        
        # Calcular métricas agregadas
        total_transactions = transactions.count()
        unique_customers = transactions.select("customer_id").distinct().count()
        
        # Decodificar amounts y calcular totales
        amounts = []
        for row in transactions.select("total_amount_raw").collect():
            amount = decode_decimal_amount(row["total_amount_raw"])
            amounts.append(amount)

        total_revenue = sum(amounts) if amounts else 0.0
        avg_amount = total_revenue / total_transactions if total_transactions > 0 else 0.0
        max_amount = max(amounts) if amounts else 0.0
        min_amount = min(amounts) if amounts else 0.0
        
        # Contar por método de pago
        payment_methods = {}
        for row in transactions.select("payment_method").collect():
            method = row["payment_method"] or "Unknown"
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        # Crear métricas finales
        metrics = {
            "total_transactions": total_transactions,
            "total_revenue": round(total_revenue, 2),
            "avg_amount": round(avg_amount, 2),
            "max_transaction": round(max_amount, 2),
            "min_transaction": round(min_amount, 2),
            "unique_customers": unique_customers,
            "payment_methods": payment_methods,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "batch_id": batch_id
        }
        
        # Guardar en Redis
        redis_client.setex("cdc_spark_metrics:transactions", 300, json.dumps(metrics))
        
        print(f"✅ Métricas guardadas:")
        print(f"   📊 Transacciones: {total_transactions}")
        print(f"   💰 Revenue: ${total_revenue:,.2f}")
        print(f"   📈 Promedio: ${avg_amount:,.2f}")
        print(f"   🔺 Máxima: ${max_amount:,.2f}")
        print(f"   🔻 Mínima: ${min_amount:,.2f}")
        print(f"   👥 Clientes únicos: {unique_customers}")
        print(f"   💳 Métodos pago: {payment_methods}")
        
    except Exception as e:
        print(f"❌ Error procesando batch {batch_id}: {e}")
        import traceback
        traceback.print_exc()

def process_products_batch(df, batch_id):
    """Procesar productos CDC y calcular métricas por categoría"""
    print(f"🔄 Procesando batch {batch_id} - Productos")
    
    try:
        if df.count() == 0:
            print(f"⚠️  Batch {batch_id} productos vacío")
            return
        
        # Parsear JSON de Kafka para transactiondetail (contiene product_id y cantidad)
        parsed_df = df.select(
            from_json(col("value").cast("string"), 
                     StructType([
                         StructField("payload", StructType([
                             StructField("after", MapType(StringType(), StringType())),
                             StructField("op", StringType())
                         ]))
                     ])).alias("data"),
            col("topic")
        ).select("data.payload.*", "topic")
        
        # Filtrar eventos de transaction_items (ventas de productos)
        detail_events = parsed_df.filter(
            (col("topic") == "transaction_items") &
            ((col("op") == "c") | (col("op") == "u")) &
            col("after").isNotNull()
        )
        
        if detail_events.count() == 0:
            print("⚠️  No hay eventos de transactiondetail válidos")
            return
        
        # Extraer datos de productos vendidos
        product_sales = detail_events.select(
            col("after")["product_id"].alias("product_id"),
            col("after")["quantity"].alias("quantity"),
            col("after")["unit_price"].alias("unit_price_raw")
        ).filter(
            col("product_id").isNotNull()
        )
        
        # Simular categorías para productos (ya que no tenemos JOIN en tiempo real)
        categories = ["electronics", "clothing", "home", "sports", "books"]
        
        category_metrics = []
        for i, category in enumerate(categories):
            # Filtrar productos por ID (simulando categorías)
            # Productos 1-2000 = electronics, 2001-4000 = clothing, etc.
            min_id = i * 2000 + 1
            max_id = (i + 1) * 2000
            
            category_sales = product_sales.filter(
                (col("product_id").cast("int") >= min_id) & 
                (col("product_id").cast("int") <= max_id)
            )
            
            if category_sales.count() > 0:
                # Calcular métricas de la categoría
                sales_data = category_sales.collect()
                total_sales = len(sales_data)
                total_revenue = 0.0
                
                for row in sales_data:
                    try:
                        quantity = int(row["quantity"]) if row["quantity"] else 1
                        # Decodificar precio unitario
                        unit_price = decode_decimal_amount(row["unit_price_raw"]) if row["unit_price_raw"] else 10.0
                        total_revenue += quantity * unit_price
                    except:
                        total_revenue += 10.0  # Valor por defecto
                
                category_metrics.append({
                    "category": category,
                    "product_sales": total_sales,
                    "category_revenue": round(total_revenue, 2)
                })
        
        if category_metrics:
            # Guardar métricas de productos en Redis
            redis_client.setex("cdc_spark_metrics:products", 300, json.dumps(category_metrics))
            
            print(f"✅ Métricas de productos guardadas:")
            for metric in category_metrics:
                print(f"   🛍️ {metric['category']}: {metric['product_sales']} ventas, ${metric['category_revenue']:.2f}")
        
    except Exception as e:
        print(f"❌ Error procesando productos batch {batch_id}: {e}")
        import traceback
        traceback.print_exc()

def process_behavior_batch(df, batch_id):
    """Procesar eventos de comportamiento CDC"""
    print(f"🔄 Procesando batch {batch_id} - Comportamiento")
    
    try:
        if df.count() == 0:
            print(f"⚠️  Batch {batch_id} comportamiento vacío")
            return
        
        # Parsear JSON de Kafka para userbehavior
        parsed_df = df.select(
            from_json(col("value").cast("string"), 
                     StructType([
                         StructField("payload", StructType([
                             StructField("after", MapType(StringType(), StringType())),
                             StructField("op", StringType())
                         ]))
                     ])).alias("data"),
            col("topic")
        ).select("data.payload.*", "topic")
        
        # Filtrar eventos de userbehavior
        behavior_events = parsed_df.filter(
            (col("topic") == "userbehavior") &
            ((col("op") == "c") | (col("op") == "u")) &
            col("after").isNotNull()
        )
        
        if behavior_events.count() == 0:
            print("⚠️  No hay eventos de comportamiento válidos")
            return
        
        # Extraer datos de comportamiento
        behavior_data = behavior_events.select(
            col("after")["customer_id"].alias("customer_id"),
            col("after")["event_type"].alias("event_type"),
            col("after")["product_id"].alias("product_id"),
            col("after")["session_id"].alias("session_id")
        ).filter(
            col("event_type").isNotNull()
        )
        
        # Contar eventos por tipo
        behavior_metrics = {}
        for row in behavior_data.collect():
            event_type = row["event_type"]
            behavior_metrics[event_type] = behavior_metrics.get(event_type, 0) + 1
        
        # Guardar métricas de comportamiento en Redis (formato esperado por dashboard)
        for event_type, count in behavior_metrics.items():
            behavior_key = f"metrics:behavior:{event_type}"
            behavior_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "event_count": count,
                "batch_id": batch_id
            }
            redis_client.setex(behavior_key, 300, json.dumps(behavior_data))
        
        if behavior_metrics:
            print(f"✅ Métricas de comportamiento guardadas:")
            for event_type, count in behavior_metrics.items():
                print(f"   🎯 {event_type}: {count} eventos")
        
    except Exception as e:
        print(f"❌ Error procesando comportamiento batch {batch_id}: {e}")
        import traceback
        traceback.print_exc()

# Leer de Kafka - múltiples topics CDC
kafka_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "transaction,transaction_items,customer,product,userbehavior") \
    .option("startingOffsets", "latest") \
    .load()

# Stream para transacciones
transaction_stream = kafka_stream.filter(col("topic") == "transaction")
transaction_query = transaction_stream.writeStream \
    .foreachBatch(process_transactions_batch) \
    .trigger(processingTime="15 seconds") \
    .start()

# Stream para productos (desde transaction_items)
product_stream = kafka_stream.filter(col("topic") == "transaction_items")
product_query = product_stream.writeStream \
    .foreachBatch(process_products_batch) \
    .trigger(processingTime="15 seconds") \
    .start()

# Stream para comportamiento (desde userbehavior)
behavior_stream = kafka_stream.filter(col("topic") == "userbehavior")
behavior_query = behavior_stream.writeStream \
    .foreachBatch(process_behavior_batch) \
    .trigger(processingTime="15 seconds") \
    .start()

print("🚀 Spark CDC → Redis con métricas completas iniciado")
print("📊 Escuchando topics: transaction, transaction_items, customer, product, userbehavior")
print("💰 Generando métricas: revenue, transacciones, clientes únicos, métodos pago")
print("🛍️ Generando métricas: productos por categoría, ventas por categoría")
print("🎯 Generando métricas: eventos de comportamiento (búsquedas, vistas, carrito)")

# Esperar todas las queries
transaction_query.awaitTermination()
product_query.awaitTermination()
behavior_query.awaitTermination()
