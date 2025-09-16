# 🚀 InstaShop Big Data Pipeline - Nico Scripts

## 📋 **Flujo Completo del Pipeline**

### **1. 📊 Generación de Datos Realistas**
- **Script**: `realistic_data_generator.py`
- **Función**: Genera transacciones y eventos de comportamiento en tiempo real
- **Datos**: Inserta en PostgreSQL (`instashop` y `crm_db`) usando timestamps UTC
- **Frecuencia**: ~10 eventos por segundo (70% transacciones, 30% comportamientos)

### **2. 📤 Producer Kafka Dinámico**
- **Script**: `kafka-streaming/dynamic_producer.py`
- **Función**: Lee datos recientes de PostgreSQL y los envía a Kafka
- **Topics**: `transactions`, `user_behavior`, `searches`, `cart_events`
- **Frecuencia**: Consulta cada 2 segundos, envía datos nuevos

### **3. 📥 Consumer Kafka**
- **Script**: `kafka-streaming/dynamic_consumer.py`
- **Función**: Consume mensajes de Kafka y los procesa
- **Destino**: Almacena datos procesados en Data Warehouse (DWH)
- **Tabla**: `realtime_events` en PostgreSQL DWH

### **4. ⚡ Spark Streaming + Redis**
- **Script**: `spark-streaming/realtime_metrics_producer.py`
- **Función**: Procesa streams de Kafka y envía métricas a Redis
- **Análisis**: Agregaciones en tiempo real (ventanas de 1 minuto)
- **Salida**: Métricas almacenadas en Redis para dashboard en tiempo real

### **5. 📊 Dashboard Streamlit + Redis**
- **Script**: `dashboards/realtime_spark_dashboard.py`
- **Función**: Visualización en tiempo real de métricas de Spark
- **Características**: KPIs en tiempo real, gráficos dinámicos, auto-refresh cada 5s
- **URL**: http://localhost:8501

---

## 🚀 **Comandos de Ejecución**

### **Activar Entorno Virtual**
```bash
source venv/bin/activate
```

### **Levantar Docker**
```bash
docker-compose up -d
```

### **Generar Eventos en PostgreSQL**
```bash
python nico-scripts/realistic_data_generator.py
```

### **Producer Kafka (Terminal 2)**
```bash
python nico-scripts/kafka-streaming/dynamic_producer.py
```

### **Consumer Kafka (Terminal 3)**
```bash
python nico-scripts/kafka-streaming/dynamic_consumer.py
```

### **Spark Streaming + Redis (Terminal 4)**
```bash
python nico-scripts/spark-streaming/realtime_metrics_producer.py
```

### **Dashboard Real-time (Terminal 5)**
```bash
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py
```

---

## 🔍 **Comandos de Monitoreo**

### **Ver Topics de Kafka**
```bash
docker exec -it kafka1 kafka-topics.sh --list --bootstrap-server localhost:9092
```

### **Ver Mensajes Kafka - Transactions**
```bash
docker exec -it kafka1 kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions --from-beginning
```

### **Ver Mensajes Kafka - User Behavior**
```bash
docker exec -it kafka1 kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic user_behavior --from-beginning
```

### **Ver Eventos en DWH**
```bash
docker exec -it postgres-dwh psql -U dwh -d dwh_db -c "SELECT COUNT(*) FROM realtime_events;"
```

### **Ver Eventos Recientes en DWH**
```bash
docker exec -it postgres-dwh psql -U dwh -d dwh_db -c "SELECT event_type, customer_id, timestamp, processed_at FROM realtime_events ORDER BY processed_at DESC LIMIT 5;"
```

### **Logs de Spark Master**
```bash
docker logs spark-master -f
```

### **Logs de Spark Worker**
```bash
docker logs spark-worker-1 -f
```

### **Ver Métricas en Redis**
```bash
docker exec -it redis-metrics redis-cli
> KEYS metrics:*
> GET metrics:transactions
```

### **Logs Generales Docker**
```bash
docker-compose logs -f
```

---

## 📊 **Logs Esperados**

### **Producer Kafka**
```
📤 Enviando 5 transacciones a Kafka
📤 Enviando 3 eventos de comportamiento a Kafka
📈 Progreso: 20 eventos procesados (15 transacciones, 5 comportamientos)
```

### **Consumer Kafka**
```
✅ Evento procesado: transaction - Cliente 28
✅ Evento procesado: page_view - Cliente 65
📈 Progreso: 10 eventos procesados
```

### **Spark Streaming + Redis**
```
📊 Métricas de transacciones actualizadas: {'transaction_count': 5, 'total_revenue': 1250.50}
📊 Métricas de comportamiento actualizadas: page_view = 12
🚀 Streaming de métricas iniciado
```

### **Dashboard Real-time**
```
⚡ InstaShop Real-time Spark Metrics
🕐 Última actualización: 2025-09-16T22:50:00Z
✅ Redis: Conectado
✅ Spark: Procesando datos
✅ Kafka: Datos fluyendo
```

---

## 🎯 **URLs Importantes**
- **Dashboard**: http://localhost:8501
- **Spark UI**: http://localhost:8080
- **Jupyter**: http://localhost:8888

---

## ⚡ **Comando Rápido (Todo en Secuencia)**
```bash
source venv/bin/activate
docker-compose up -d
sleep 30
python nico-scripts/realistic_data_generator.py &
python nico-scripts/kafka-streaming/dynamic_producer.py &
python nico-scripts/kafka-streaming/dynamic_consumer.py &
python nico-scripts/spark-streaming/realtime_metrics_producer.py &
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py
```
