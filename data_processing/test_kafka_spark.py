"""
Script de prueba para Kafka + Spark Streaming
Ejecuta el pipeline completo paso a paso
"""

import subprocess
import time
import threading
import sys

def run_producer():
    """Ejecutar Kafka Producer"""
    print("🚀 Iniciando Kafka Producer...")
    try:
        subprocess.run([sys.executable, "kafka_producer.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en Producer: {e}")

def run_consumer():
    """Ejecutar Kafka Consumer"""
    print("🚀 Iniciando Kafka Consumer...")
    try:
        subprocess.run([sys.executable, "kafka_consumer.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en Consumer: {e}")

def run_spark_streaming():
    """Ejecutar Spark Streaming"""
    print("🚀 Iniciando Spark Streaming...")
    try:
        subprocess.run([sys.executable, "spark_streaming.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en Spark Streaming: {e}")

def main():
    print("🎯 PRUEBA COMPLETA: Kafka + Spark Streaming")
    print("=" * 50)
    
    print("\n📋 Pasos de la prueba:")
    print("1. Instalar dependencias")
    print("2. Ejecutar Kafka Producer (envía datos)")
    print("3. Ejecutar Kafka Consumer (procesa datos)")
    print("4. Ejecutar Spark Streaming (análisis en tiempo real)")
    
    print("\n🔧 Instalando dependencias...")
    try:
        subprocess.run(["pip", "install", "kafka-python", "pyspark"], check=True)
        print("✅ Dependencias instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return
    
    print("\n🚀 Iniciando prueba...")
    
    # Ejecutar en threads separados
    producer_thread = threading.Thread(target=run_producer)
    consumer_thread = threading.Thread(target=run_consumer)
    
    # Iniciar producer y consumer
    producer_thread.start()
    time.sleep(2)  # Esperar que producer inicie
    consumer_thread.start()
    
    # Esperar que terminen
    producer_thread.join()
    consumer_thread.join()
    
    print("\n✅ Prueba completada!")
    print("\n📊 Para ver Spark Streaming en acción:")
    print("   python spark_streaming.py")

if __name__ == "__main__":
    main()
