# 🚀 InstaShop Big Data Pipeline - Nico Scripts

> 📊 **Ver diagrama completo**: [ARCHITECTURE.md](./ARCHITECTURE.md)  
> 🗄️ **Ver DER de bases de datos**: [DATABASE_ERD.md](./DATABASE_ERD.md)

## 📋 **Flujo Completo del Pipeline**

### **1. 📊 Generación de Datos Realistas**
- **Script**: `realistic_data_generator.py`
- **Función**: Genera transacciones y eventos de comportamiento en tiempo real
- **Datos**: Inserta en PostgreSQL (`instashop` y `crm_db`) usando timestamps UTC
- **Frecuencia**: ~10 eventos por segundo (70% transacciones, 30% comportamientos)
- **Características**: Auto-inicialización de tablas, creación de datos básicos, manejo de secuencias PostgreSQL

### **2. 📤 Producer Kafka Dinámico**
- **Script**: `kafka-streaming/dynamic_producer.py`
- **Función**: Lee datos recientes de PostgreSQL y los envía a Kafka
- **Topics**: `transactions`, `user_behavior`, `searches`, `cart_events`
- **Frecuencia**: Consulta cada 2 segundos, envía TODOS los datos (sin protección contra duplicados)
- **Ventana**: Lee datos de los últimos 2 minutos

### **3. 📥 Consumer Kafka**
- **Script**: `kafka-streaming/dynamic_consumer.py`
- **Función**: Consume mensajes de Kafka y los procesa
- **Destino**: Almacena datos procesados en Data Warehouse (DWH)
- **Tabla**: `realtime_events` en PostgreSQL DWH
- **Configuración**: Group ID único, `auto_offset_reset='earliest'`, commit manual
- **Envío adicional**: Envía eventos `transaction_item` enriquecidos a Kafka para Spark

### **4. ⚡ Spark Streaming + Redis**
- **Script**: `spark-streaming/realtime_metrics_producer.py`
- **Función**: Procesa streams de Kafka y envía métricas a Redis
- **Topics**: `transactions`, `user_behavior`, `transaction_items`
- **Análisis**: Agregaciones en tiempo real (ventanas de 30 segundos)
- **Métricas**: Transacciones, comportamiento, productos por categoría
- **Salida**: Métricas almacenadas en Redis para dashboard en tiempo real

### **5. 📊 Dashboard Streamlit + Redis + DWH**
- **Script**: `dashboards/realtime_spark_dashboard.py`
- **Función**: Visualización en tiempo real de métricas de Spark y datos históricos del DWH
- **Fuentes**: Redis (métricas en tiempo real), PostgreSQL DWH (datos históricos)
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

### **Generador de Datos**
```
🚀 Iniciando generación de datos realistas por 60 minutos
📊 Estado inicial: 50 clientes, 100 compradores, 200 productos
🔄 Iniciando bucle de generación de datos...
📈 Progreso: 50 eventos generados (35 transacciones, 15 comportamientos)
```

### **Producer Kafka**
```
🚀 Dynamic Kafka Producer inicializado
📤 Enviando 8 transacciones a Kafka
🔄 Transacción 1234 con 3 items
✅ Enviado exitosamente a transactions: transaction - Cliente 28
💓 Producer activo - enviando datos a Kafka...
```

### **Consumer Kafka**
```
🚀 Dynamic Kafka Consumer inicializado
🆔 Group ID: instashop-dynamic-group-1694895600
⚙️ Auto offset reset: earliest
📨 Mensaje recibido de topic: transactions, offset: 15
✅ Evento #1 procesado exitosamente
📤 Enviado transaction_item a Kafka: iPhone 15 (Electronics)
```

### **Spark Streaming + Redis**
```
🚀 Realtime Metrics Producer inicializado
📊 Esperando datos de Kafka para procesar...
🔄 Procesando batch 1 con 5 filas
📊 Métricas de transacciones actualizadas: {'transaction_count': 5, 'total_revenue': 1250.5}
📊 Métricas de productos actualizadas: Electronics = {'product_sales': 3, 'category_revenue': 800.0}
```

### **Dashboard Real-time**
```
⚡ InstaShop Real-time Spark Metrics
🕐 Última actualización: 2025-09-16T22:50:00Z
✅ Redis: Conectado
✅ Spark: Procesando datos
✅ Kafka: Datos fluyendo
📊 Total de Eventos: 4,796
```

---

## 🎯 **URLs Importantes**
- **Dashboard**: http://localhost:8501
- **Spark UI**: http://localhost:8080
- **Jupyter**: http://localhost:8888

---

## ⚙️ **Características Técnicas**

### **Configuraciones Optimizadas**
- **Generador**: Intervalo de 0.1 segundos, 70% transacciones, timestamps UTC
- **Producer**: Consulta cada 2 segundos, ventana de 2 minutos, sin protección contra duplicados
- **Consumer**: Group ID único, `auto_offset_reset='earliest'`, commit manual
- **Spark**: Watermark de 10 segundos, ventanas de 30 segundos, `startingOffsets='earliest'`
- **Dashboard**: Auto-refresh cada 5 segundos, conexión a Redis y DWH

### **Dependencias Principales**
- **Python**: 3.8+
- **PostgreSQL**: Múltiples instancias (instashop, crm_db, dwh_db)
- **Kafka**: 3 brokers (kafka1, kafka2, kafka3)
- **Spark**: 3.3.4 con Java 17
- **Redis**: Para métricas en tiempo real
- **Streamlit**: Para dashboard interactivo

### **Topics de Kafka**
- `transactions`: Eventos de transacciones
- `user_behavior`: Eventos de comportamiento de usuarios
- `searches`: Eventos de búsqueda
- `cart_events`: Eventos de carrito
- `transaction_items`: Eventos enriquecidos de items de transacción

---

## 🔧 **Troubleshooting**

### **Consumer no recibe mensajes**
- **Problema**: Consumer configurado con `auto_offset_reset='latest'`
- **Solución**: Cambiar a `auto_offset_reset='earliest'` y usar Group ID único

### **Dashboard muestra gráficos vacíos**
- **Problema**: `transaction_metrics` vacío en Redis
- **Solución**: Verificar que Spark esté procesando eventos `transaction_item`

### **Generador falla con errores de foreign key**
- **Problema**: IDs de productos/clientes no existen
- **Solución**: El generador auto-inicializa datos básicos si las tablas están vacías

### **Spark no encuentra datos**
- **Problema**: `startingOffsets='latest'` en Spark
- **Solución**: Cambiar a `startingOffsets='earliest'` y reducir watermark a 10 segundos

### **Redis sin métricas de productos**
- **Problema**: Kafka messages con `items: []` vacíos
- **Solución**: Verificar que el generador inserte `TransactionDetail` correctamente

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
