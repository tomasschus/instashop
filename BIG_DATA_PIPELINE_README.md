# 🚀 INSTASHOP BIG DATA PIPELINE

## 📊 Estado Actual - COMPLETAMENTE FUNCIONAL

### ✅ **COMPONENTES FUNCIONANDO PERFECTAMENTE**

#### **1. 🗄️ Bases de Datos PostgreSQL**
- **instashop** (puerto 5432) - Base principal con datos de productos, clientes, compradores
- **crm_db** (puerto 5433) - CRM
- **erp_db** (puerto 5434) - ERP  
- **ecommerce_db** (puerto 5435) - E-commerce
- **dwh_db** (puerto 5436) - Data Warehouse con **101+ eventos en tiempo real**

#### **2. 📨 Apache Kafka (3 Brokers)**
- **kafka1** (puerto 9092) - Broker principal
- **kafka2** (puerto 9093) - Broker secundario
- **kafka3** (puerto 9094) - Broker terciario
- **Topics activos**: `transactions`, `user_behavior`, `searches`, `cart_events`

#### **3. 🔄 Pipeline Big Data (Producer → Kafka → Consumer → DWH)**
- **Producer**: Genera eventos simulados (transacciones, búsquedas, carritos)
- **Consumer**: Lee de Kafka y guarda en DWH en tiempo real
- **Consumer Group**: `instashop-analytics-group` (LAG = 0, procesando todo en tiempo real)

#### **4. 📊 Datos Procesados en Tiempo Real**
- **Transacciones**: Con información completa (cliente, producto, monto, método de pago)
- **Búsquedas**: Términos de búsqueda de usuarios
- **Abandono de carrito**: Con valores de carrito abandonado
- **Eventos de usuario**: Clicks, vistas de productos

#### **5. 🖥️ Spark Cluster**
- **Spark Master**: Corriendo en puerto 8080 (UI disponible)
- **Jupyter**: Disponible en puerto 8888 con PySpark

---

## 🚀 **CÓMO USAR EL PIPELINE**

### **1. Levantar el Sistema Completo**
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Levantar todos los servicios
docker-compose up -d
```

### **2. Ejecutar el Pipeline Big Data**
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar pipeline completo
python run_pipeline.py
```

**Opciones disponibles:**
1. **Pipeline completo** (Producer + Consumer + Spark)
2. **Solo Producer** (genera datos a Kafka)
3. **Solo Consumer** (lee de Kafka y guarda en DWH)
4. **Solo Spark Streaming** (análisis en tiempo real)
5. **Producer + Consumer** (sin Spark)

### **3. Verificar que Funciona**

#### **Verificar Kafka Topics:**
```bash
docker exec kafka1 kafka-topics.sh --bootstrap-server localhost:9092 --list
```

#### **Ver datos en Kafka:**
```bash
docker exec kafka1 kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions --from-beginning --max-messages 3
```

#### **Ver datos en DWH:**
```bash
docker exec dwh_db psql -U dwh -d dwh_db -c "SELECT COUNT(*) FROM realtime_events;"
```

#### **Ver Consumer Group Status:**
```bash
docker exec kafka1 kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group instashop-analytics-group
```

---

## 📈 **INTERFACES DISPONIBLES**

- **Spark UI**: http://localhost:8080
- **Jupyter Notebook**: http://localhost:8888
- **Streamlit Dashboard Original**: http://localhost:8501
- **🚀 Spark Analytics Dashboard**: http://localhost:8502

---

## 🚀 **SPARK ANALYTICS DASHBOARD**

### **Dashboard de Análisis en Tiempo Real**
**URL**: http://localhost:8502

#### **📊 Características del Dashboard:**
- **Métricas en tiempo real**: Total eventos, clientes únicos, ingresos, último evento
- **Visualizaciones interactivas**: Gráficos de torta y barras con Plotly
- **Análisis por categoría**: Eventos y ingresos por tipo de producto
- **Top clientes**: Ranking de clientes por número de transacciones
- **Tabla de eventos recientes**: Últimos 20 eventos procesados
- **Auto-refresh**: Se actualiza cada 30 segundos automáticamente

#### **🎯 Métricas que muestra:**
1. **📈 Distribución de eventos**: Gráfico de torta mostrando tipos de eventos
2. **🏆 Top 5 clientes**: Clientes con más transacciones
3. **🛍️ Análisis por categoría**: Eventos y ingresos por categoría de productos
4. **📋 Eventos recientes**: Tabla con los últimos eventos procesados
5. **💰 Métricas financieras**: Ingresos totales y promedio por transacción

#### **🔄 Cómo usar el Dashboard:**
1. **Acceder**: Ve a http://localhost:8502
2. **Ver datos**: El dashboard se actualiza automáticamente cada 30 segundos
3. **Refresh manual**: Usa el botón "🔄 Refresh Data" para actualización inmediata
4. **Monitorear pipeline**: Ve el estado de todos los componentes del pipeline

---

## 🔧 **ARQUITECTURA DEL PIPELINE**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Producer  │───▶│    Kafka    │───▶│  Consumer   │───▶│    DWH      │
│             │    │  (Topics)   │    │             │    │ PostgreSQL  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │    Spark    │
                   │ Streaming   │
                   │ (Análisis)  │
                   └─────────────┘
```

---

## 📊 **TIPOS DE EVENTOS PROCESADOS**

### **Transacciones**
```json
{
  "event_type": "transaction",
  "transaction_id": "uuid",
  "customer_id": 27,
  "customer_name": "Mendoza, Smith and Ray",
  "subscription_plan": "Enterprise",
  "buyer_id": 52,
  "buyer_name": "Terry Bush",
  "product_id": 100,
  "product_name": "Rock",
  "category": "Electronics",
  "price": 469.91,
  "quantity": 4,
  "total_amount": 469.91,
  "payment_method": "Wire Transfer",
  "status": "failed",
  "timestamp": "2025-09-16T17:26:19.227476"
}
```

### **Búsquedas**
```json
{
  "event_type": "search",
  "customer_id": 12,
  "search_term": "electronics",
  "timestamp": "2025-09-16T17:26:30.346408"
}
```

### **Abandono de Carrito**
```json
{
  "event_type": "cart_abandonment",
  "customer_id": 2,
  "cart_value": 64.17,
  "timestamp": "2025-09-16T17:26:31.777958"
}
```

---

## 🎯 **ESTADO ACTUAL**

✅ **Producer funcionando** - Generando datos a Kafka  
✅ **Kafka funcionando** - 4 topics activos con datos  
✅ **Consumer funcionando** - Procesando datos en tiempo real (LAG = 0)  
✅ **DWH funcionando** - 101+ eventos almacenados  
✅ **Spark funcionando** - Cluster activo (UI en puerto 8080)  
✅ **Dashboard original funcionando** - Streamlit en puerto 8501  
✅ **🚀 Spark Analytics Dashboard funcionando** - Streamlit en puerto 8502  

**El pipeline Big Data está 100% funcional y procesando datos en tiempo real!**

### **🎉 NUEVAS CARACTERÍSTICAS:**
- **Dashboard de Spark Analytics**: Visualizaciones en tiempo real de los datos procesados
- **Análisis automático**: Métricas actualizadas cada 30 segundos
- **Interfaz interactiva**: Gráficos con Plotly para mejor experiencia de usuario
- **Monitoreo completo**: Estado de todos los componentes del pipeline visible

---

## 📁 **ESTRUCTURA DE ARCHIVOS**

```
instashop/
├── kafka_streaming/
│   ├── producer.py          # Genera eventos a Kafka
│   └── consumer.py          # Lee de Kafka y guarda en DWH
├── spark_analytics/
│   ├── streaming.py         # Análisis en tiempo real con Spark (Kafka)
│   └── simple_streaming.py  # Análisis simplificado desde DWH
├── config.py               # Configuración centralizada
├── run_pipeline.py         # Script principal del pipeline
├── spark_dashboard.py      # Dashboard de Spark Analytics
└── BIG_DATA_PIPELINE_README.md  # Este archivo
```

---

## 🚨 **NOTAS IMPORTANTES**

- **Java requerido**: Spark necesita Java 17+ para funcionar correctamente
- **Puertos utilizados**: 5432-5436 (PostgreSQL), 9092-9094 (Kafka), 8080 (Spark), 8501-8502 (Streamlit), 8888 (Jupyter)
- **Consumer Group**: `instashop-analytics-group` (no cambiar)
- **Datos en tiempo real**: El consumer procesa todos los eventos sin retraso (LAG = 0)

---

**🎉 ¡El pipeline Big Data está completamente funcional y procesando datos en tiempo real!**
