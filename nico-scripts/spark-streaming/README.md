# 🚀 Spark Streaming Scripts - CDC Architecture

## 📋 **Scripts Disponibles**

### **1. 📊 CDC Redis Producer**
- **Script**: `cdc_redis_producer.py`
- **Función**: Consumer especializado para eventos CDC de Debezium
- **Entrada**: Topics CDC de Kafka (`transaction`, `customer`, `product`, etc.)
- **Salida**: Métricas agregadas en Redis para dashboard
- **Características**:
  - ✅ Procesa eventos CDC en tiempo real
  - ✅ Maneja operaciones `create`, `update`, `delete`, `read`
  - ✅ Contador de transacciones, clientes, productos
  - ✅ Cálculo de revenue total y diario
  - ✅ Actualización automática cada 5 eventos
  - ✅ Manejo graceful de señales (SIGINT/SIGTERM)

### **2. ⚡ Realtime Metrics Producer (Spark)**
- **Script**: `realtime_metrics_producer.py`
- **Función**: Spark Streaming para análisis avanzados
- **Entrada**: Topics CDC de Kafka
- **Salida**: Métricas complejas en Redis
- **Características**:
  - ✅ Agregaciones en ventanas de tiempo
  - ✅ Análisis por categorías de productos
  - ✅ Métricas de comportamiento de usuarios
  - ✅ Watermarks para datos tardíos

### **3. 📈 Simple Metrics Producer**
- **Script**: `simple_metrics_producer.py`
- **Función**: Métricas básicas sin Spark
- **Uso**: Para pruebas rápidas y debugging

### **4. 📊 Kafka Streaming Analytics**
- **Script**: `kafka_streaming_analytics.py`
- **Función**: Análisis general de streams de Kafka
- **Uso**: Análisis exploratorios y métricas personalizadas

---

## 🚀 **Uso Recomendado**

### **Para Dashboard en Tiempo Real**
```bash
# Usar CDC Redis Producer (más eficiente)
source venv/bin/activate
python nico-scripts/cdc_redis_producer.py
```

### **Para Análisis Avanzados**
```bash
# Usar Spark Streaming en paralelo
source venv/bin/activate
python nico-scripts/spark-streaming/realtime_metrics_producer.py
```

### **Ejecutar Ambos (Configuración Completa)**
```bash
# Terminal 1: CDC Redis Producer
python nico-scripts/cdc_redis_producer.py &

# Terminal 2: Spark Streaming
python nico-scripts/spark-streaming/realtime_metrics_producer.py &
```

---

## 📊 **Métricas Generadas**

### **CDC Redis Producer**
```json
{
  "total_transactions": 3207,
  "total_customers": 805,
  "total_products": 2701,
  "total_events": 18884,
  "revenue_total": 125847.50,
  "transactions_today": 45,
  "revenue_today": 2150.75,
  "last_updated": "2025-09-17T02:00:25.729511",
  "status": "active"
}
```

### **Spark Streaming**
- Métricas por ventanas de tiempo
- Agregaciones por categoría
- Análisis de comportamiento
- Trends y patrones

---

## 🔍 **Monitoreo**

### **Verificar Métricas en Redis**
```bash
# Ver todas las métricas
docker exec redis-metrics redis-cli GET "metrics:dashboard"

# Ver claves disponibles
docker exec redis-metrics redis-cli KEYS "metrics:*"

# Monitorear en tiempo real
watch -n 1 'docker exec redis-metrics redis-cli GET "metrics:dashboard" | jq'
```

### **Logs de CDC Redis Producer**
```bash
# Ejecutar con logs visibles
python nico-scripts/cdc_redis_producer.py

# Logs esperados:
# ✅ Conexión a Redis establecida
# ✅ Consumer Kafka CDC configurado
# 📥 CDC Event - Topic: transaction, Op: c
# 💰 Transacción procesada: ID=1234, Total=$99.99
# 📊 Métricas actualizadas en Redis: 5 eventos procesados
```

### **Logs de Spark Streaming**
```bash
# Ver logs de Spark
python nico-scripts/spark-streaming/realtime_metrics_producer.py

# Logs esperados:
# 🚀 Realtime Metrics Producer inicializado
# 📊 Esperando datos de Kafka para procesar...
# 🔄 Procesando batch 1 con 5 filas
# 📊 Métricas actualizadas en Redis
```

---

## ⚙️ **Configuración**

### **CDC Redis Producer**
- **Bootstrap Servers**: `localhost:9092`, `localhost:9093`, `localhost:9094`
- **Redis**: `localhost:6379`
- **Group ID**: `cdc-redis-producer-{timestamp}`
- **Auto Offset Reset**: `earliest`
- **Update Frequency**: Cada 5 eventos

### **Spark Streaming**
- **Spark Master**: `local[*]`
- **Watermark**: 10 segundos
- **Window Size**: 30 segundos
- **Batch Interval**: Por defecto

---

## 🔧 **Troubleshooting**

### **CDC Redis Producer no recibe eventos**
1. **Verificar Debezium**: `curl http://localhost:8083/connectors`
2. **Verificar Topics**: `docker exec kafka1 kafka-topics.sh --list --bootstrap-server localhost:19092`
3. **Verificar Redis**: `docker exec redis-metrics redis-cli ping`

### **Spark Streaming no encuentra topics**
1. **Verificar configuración de topics** en el script
2. **Verificar conectividad**: Usar puertos internos (`19092`) para Kafka
3. **Revisar logs**: Buscar errores de `UNKNOWN_TOPIC_OR_PARTITION`

### **Métricas no se actualizan**
1. **Verificar que CDC Redis Producer esté procesando eventos**
2. **Verificar logs**: Buscar mensajes de "Métricas actualizadas en Redis"
3. **Verificar claves Redis**: `KEYS metrics:*`

---

## 📈 **Performance**

### **CDC Redis Producer**
- ✅ **Alto throughput**: Procesa ~18K eventos en 15 segundos
- ✅ **Bajo overhead**: Sin Spark, consumo mínimo de memoria
- ✅ **Tiempo real**: Actualización cada 5 eventos

### **Spark Streaming**
- ✅ **Análisis complejos**: Ventanas, agregaciones, joins
- ✅ **Escalabilidad**: Se adapta a volúmenes altos
- ✅ **Fault tolerance**: Checkpointing automático

---

## 💡 **Recomendaciones**

1. **Usar CDC Redis Producer** para métricas básicas en tiempo real
2. **Usar Spark Streaming** para análisis complejos y agregaciones avanzadas
3. **Ejecutar ambos en paralelo** para cobertura completa
4. **Monitorear Redis** para verificar que las métricas se actualizan
5. **Verificar Debezium** regularmente para asegurar CDC activo
