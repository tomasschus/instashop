# 🚀 InstaShop Big Data Pipeline - Nico Scripts (CDC Architecture)

> 📊 **Ver diagrama completo**: [ARCHITECTURE.md](./ARCHITECTURE.md)  
> 🗄️ **Ver DER de bases de datos**: [DATABASE_ERD.md](./DATABASE_ERD.md)  
> 🏢 **Ver DER del Data Warehouse**: [DWH_ERD.md](./DWH_ERD.md)

## 📋 **Flujo CDC Completo del Pipeline**

### **1. 📊 Generación de Datos Realistas**
- **Script**: `realistic_data_generator.py`
- **Función**: Genera transacciones y eventos de comportamiento en tiempo real
- **Datos**: Inserta en PostgreSQL (`instashop`, `crm_db`, `erp_db`, `ecommerce_db`) usando timestamps UTC
- **Frecuencia**: ~10 eventos por segundo (70% transacciones, 30% comportamientos)
- **Características**: Auto-inicialización de tablas, creación de datos básicos, manejo de secuencias PostgreSQL

### **2. 🔄 Debezium Change Data Capture (CDC)**
- **Script**: `setup_debezium.py` + `init_postgres_cdc.py`
- **Función**: Configuración automática de Debezium para capturar cambios en PostgreSQL
- **Conectores**: 4 conectores CDC (InstashopDB, CRM, ERP, E-commerce)
- **Topics CDC**: `transaction`, `customer`, `product`, `transactiondetail`, `interaction`, `stock`, `carrier`, `shipment`
- **Configuración**: Logical replication, replication slots, publications automáticas
- **Plugin**: `pgoutput` (nativo de PostgreSQL)

### **3. 📥 CDC Redis Producer**
- **Script**: `cdc_redis_producer.py`
- **Función**: Consume eventos CDC de Debezium y popula métricas en Redis
- **Topics**: Todos los tópicos CDC de Debezium
- **Destino**: Métricas agregadas en Redis para dashboard en tiempo real
- **Características**: Procesamiento de eventos `create`, `update`, `delete`, `read`
- **Métricas**: Contadores de transacciones, clientes, productos, revenue total/diario

### **4. ⚡ Spark Streaming + Redis**
- **Script**: `spark-streaming/realtime_metrics_producer.py`
- **Función**: Procesa streams CDC de Kafka y envía métricas avanzadas a Redis
- **Topics**: `transaction`, `customer`, `product`, `transaction_items` (renombrado por Debezium)
- **Análisis**: Agregaciones en tiempo real (ventanas de 30 segundos)
- **Métricas**: Análisis avanzados de transacciones, categorías, comportamientos
- **Salida**: Métricas complejas almacenadas en Redis para dashboard

### **5. 📊 Dashboard Streamlit + Redis + DWH**
- **Script**: `dashboards/realtime_spark_dashboard.py`
- **Función**: Visualización en tiempo real de métricas de Spark y datos históricos del DWH
- **Fuentes**: Redis (métricas en tiempo real), PostgreSQL DWH (datos históricos)
- **Características**: KPIs en tiempo real, gráficos dinámicos, auto-refresh cada 5s
- **URL**: http://localhost:8501

---

## 🚀 **Comandos de Ejecución CDC**

### **Activar Entorno Virtual**
```bash
source venv/bin/activate
```

### **Levantar Docker**
```bash
docker-compose up -d
```

### **Configurar PostgreSQL para CDC**
```bash
python nico-scripts/init_postgres_cdc.py
```

### **Desplegar Conectores Debezium**
```bash
python nico-scripts/setup_debezium.py
```

### **Generar Eventos en PostgreSQL**
```bash
python nico-scripts/realistic_data_generator.py
```

### **CDC Redis Producer (Terminal 2)**
```bash
python nico-scripts/cdc_redis_producer.py
```

### **Spark Streaming + Redis (Terminal 3)**
```bash
python nico-scripts/spark-streaming/realtime_metrics_producer.py
```

### **Dashboard Real-time (Terminal 4)**
```bash
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py
```

---

## 🔍 **Comandos de Monitoreo CDC**

### **Ver Topics CDC de Kafka**
```bash
docker exec kafka1 kafka-topics.sh --list --bootstrap-server localhost:19092
```

### **Ver Mensajes CDC - Transactions**
```bash
docker exec kafka1 kafka-console-consumer.sh --bootstrap-server localhost:19092 --topic transaction --from-beginning --max-messages 1
```

### **Ver Mensajes CDC - Customers**
```bash
docker exec kafka1 kafka-console-consumer.sh --bootstrap-server localhost:19092 --topic customer --from-beginning --max-messages 1
```

### **Ver Estado de Conectores Debezium**
```bash
curl -s http://localhost:8083/connectors | jq
curl -s http://localhost:8083/connectors/instashop-connector/status | jq
```

### **Ver Métricas CDC en Redis**
```bash
docker exec redis-metrics redis-cli GET "metrics:dashboard"
docker exec redis-metrics redis-cli KEYS "metrics:*"
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

### **Topics CDC de Kafka**
- `transaction`: Eventos CDC de transacciones (InstashopDB)
- `customer`: Eventos CDC de clientes (InstashopDB)
- `product`: Eventos CDC de productos (InstashopDB)
- `transactiondetail`: Eventos CDC de detalles de transacción (InstashopDB)
- `interaction`: Eventos CDC de interacciones (CRM)
- `stock`: Eventos CDC de inventario (ERP)
- `carrier`: Eventos CDC de transportistas (E-commerce)
- `shipment`: Eventos CDC de envíos (E-commerce)

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

## ⚡ **Comando Rápido CDC (Todo en Secuencia)**
```bash
# 1. Activar entorno e iniciar servicios
source venv/bin/activate
docker-compose up -d
sleep 60

# 2. Configurar CDC
python nico-scripts/init_postgres_cdc.py
python nico-scripts/setup_debezium.py
sleep 10

# 3. Iniciar pipeline CDC
python nico-scripts/realistic_data_generator.py &
python nico-scripts/cdc_redis_producer.py &
python nico-scripts/spark-streaming/realtime_metrics_producer.py &
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py
```
