# 🛒 InstaShop Analytics Platform

Plataforma completa de análisis de datos para comercio electrónico usando **Change Data Capture (CDC)**, **Apache Kafka**, **Apache Spark** y **Redis** con dashboard en tiempo real.

## 🏗️ Arquitectura CDC + Dual Pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Debezium     │    │   Apache Kafka  │
│   (5 bases)     │───▶│   CDC Engine   │───▶│   (3 brokers)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         │                        │                        │
         │                        │                        ▼
         │                        │              ┌─────────────────┐
         │                        │              │   Apache Spark │
         │                        │              │   Streaming    │
         │                        │              └─────────────────┘
         │                        │                        │
         │                        │                        ▼
         │                        │              ┌─────────────────┐
         │                        │              │     Redis      │
         │                        │              │   (Cache)      │
         │                        │              └─────────────────┘
         │                        │                        │
         │                        │                        ▼
         │                        │              ┌─────────────────┐
         │                        │              │ 🎯 Streamlit   │
         │                        │              │   Dashboard    │
         │                        │              │ 📊 Real-time   │
         │                        │              └─────────────────┘
         │                        │
         │                        ▼
         │              ┌─────────────────┐
         │              │   Python        │
         │              │   Consumer      │
         │              │   (CDC → DWH)   │
         │              └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│   Data          │    │   Data          │
│   Warehouse     │    │   Warehouse     │
│   (DWH)         │    │   (DWH)         │
│   Historical    │    │   Real-time     │
└─────────────────┘    └─────────────────┘
```

### 🔄 Dos Flujos Principales

#### **1. 📊 CDC → Spark → Redis → Dashboard (Tiempo Real)**
```
PostgreSQL → Debezium → Kafka → Spark Streaming → Redis → Streamlit Dashboard
```
- **Propósito**: Métricas en tiempo real para dashboards
- **Latencia**: Sub-segundo
- **Datos**: Agregaciones y métricas calculadas

#### **2. 🗄️ CDC → Python Consumer → Data Warehouse (Histórico)**
```
PostgreSQL → Debezium → Kafka → Python Consumer → DWH PostgreSQL
```
- **Propósito**: Almacenamiento histórico para análisis
- **Latencia**: Cerca de tiempo real
- **Datos**: Eventos individuales preservados

### 🗄️ Bases de Datos (PostgreSQL)
- **instashop** (Puerto 5432): Base principal con transacciones, customers y productos
- **crm_db** (Puerto 5433): Sistema CRM con datos de clientes
- **erp_db** (Puerto 5434): Sistema ERP con inventario y stock
- **ecommerce_db** (Puerto 5435): Datos de e-commerce
- **dwh_db** (Puerto 5436): Data Warehouse para análisis

### ⚡ Streaming (Apache Kafka + Debezium CDC)
- **kafka1** (Puerto 9092): Broker principal
- **kafka2** (Puerto 9093): Broker secundario  
- **kafka3** (Puerto 9094): Broker terciario
- **debezium-connect** (Puerto 8083): CDC Engine para PostgreSQL

### 🔥 Big Data (Apache Spark + Redis)
- **Spark Master** (Puerto 8080): Interfaz web de Spark
- **Redis** (Puerto 6379): Cache en tiempo real para métricas
- **Jupyter Notebook** (Puerto 8888): Análisis interactivo

## 🚀 Inicio Rápido

### 1. Levantar la Infraestructura
```bash
docker compose up -d
```

### 2. Configurar CDC (Change Data Capture)
```bash
# Activar entorno virtual
source venv/bin/activate

# Configurar PostgreSQL para CDC
python nico-scripts/init_postgres_cdc.py

# Desplegar conectores Debezium
python nico-scripts/setup_debezium.py
```

### 3. Poblar con Datos de Prueba
```bash
# Generar datos iniciales
python fake-data.py

# Generar datos realistas en tiempo real
python nico-scripts/realistic_data_generator.py
```

### 4. Ejecutar Dual Pipeline CDC
```bash
# Terminal 1: CDC → Data Warehouse (Histórico)
python nico-scripts/cdc_dwh_consumer.py

# Terminal 2: CDC → Spark → Redis (Tiempo Real)
python nico-scripts/spark-streaming/cdc_spark_redis.py
```

### 5. Lanzar Dashboard
```bash
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py --server.port 8501
```

**🌐 Dashboard disponible en:** http://localhost:8501

## 🔄 Dual Pipeline CDC

### 📊 Pipeline Tiempo Real (Spark + Redis)
**Propósito**: Dashboard interactivo con métricas en tiempo real

```bash
# Ejecutar Spark Streaming
python nico-scripts/spark-streaming/cdc_spark_redis.py
```

**Métricas generadas en Redis:**
- `cdc_spark_metrics:transactions` - Transacciones, revenue, clientes únicos
- `cdc_spark_metrics:products` - Ventas por categoría
- `metrics:behavior:*` - Eventos de comportamiento (búsquedas, vistas, carrito)

### 🗄️ Pipeline Histórico (DWH)
**Propósito**: Almacenamiento histórico para análisis y reportes

```bash
# Ejecutar Consumer CDC → DWH
python nico-scripts/cdc_dwh_consumer.py
```

**Datos almacenados en DWH:**
- `realtime_events` - Todos los eventos CDC preservados
- Eventos de transacciones, comportamiento, productos
- Timestamps precisos para análisis temporal

### 🎯 Beneficios del Dual Pipeline
- **Tiempo Real**: Dashboard responsivo con métricas actualizadas
- **Histórico**: Análisis de tendencias y patrones a largo plazo
- **Escalabilidad**: Separación de responsabilidades
- **Resiliencia**: Fallback entre sistemas

## 📊 KPIs y Métricas

### 💰 Métricas Financieras
- **Revenue Total**: Ingresos acumulados
- **AOV (Average Order Value)**: Valor promedio por pedido
- **Revenue 30d**: Ingresos últimos 30 días
- **Growth Rate**: Tasa de crecimiento

### 👥 Métricas de Clientes
- **Customers Activos**: Clientes con transacciones
- **Segmentación por Plan**: Basic, Premium, Enterprise
- **Customer Lifetime Value**: Valor de vida del cliente
- **Retention Rate**: Tasa de retención

### 📦 Métricas de Inventario
- **Stock Status**: Crítico, Bajo, Óptimo
- **Productos Críticos**: Stock por debajo del punto de reorden
- **Rotación de Inventario**: Velocidad de movimiento
- **Almacenes**: Distribución por ubicación

### 🛍️ Métricas de Ventas
- **Transacciones Diarias**: Volumen de operaciones
- **Categorías Top**: Productos más vendidos
- **Métodos de Pago**: Distribución de pagos
- **Tendencias**: Análisis temporal

## 📁 Estructura del Proyecto

```
instashop/
├── 🐳 docker-compose.yml                    # Orquestación de servicios
├── 📊 fake-data.py                         # Generador de datos iniciales
├── 📁 debezium-config/                     # Configuraciones CDC
│   ├── instashop-connector.json            # Conector principal
│   ├── crm-connector.json                  # Conector CRM
│   ├── erp-connector.json                  # Conector ERP
│   └── ecommerce-connector.json            # Conector E-commerce
├── 📁 nico-scripts/                        # Scripts principales
│   ├── init_postgres_cdc.py               # Configuración CDC PostgreSQL
│   ├── setup_debezium.py                 # Despliegue conectores CDC
│   ├── realistic_data_generator.py        # Generador datos realistas
│   ├── cdc_dwh_consumer.py                # Consumer CDC → DWH
│   ├── 📁 spark-streaming/                # Scripts Spark
│   │   └── cdc_spark_redis.py            # Spark CDC → Redis
│   └── 📁 dashboards/                     # Dashboards
│       └── realtime_spark_dashboard.py    # Dashboard principal
├── 📁 data/                               # Datos persistentes PostgreSQL
├── 🐍 venv/                               # Entorno virtual Python
└── 📋 README.md
```

## 🛠️ Tecnologías

### Backend
- **🐳 Docker & Docker Compose**: Orquestación de contenedores
- **🗄️ PostgreSQL 15**: Base de datos relacional
- **⚡ Apache Kafka**: Streaming de datos
- **🔥 Apache Spark**: Procesamiento Big Data
- **🐍 Python 3.12**: Lenguaje principal

### Frontend & Analytics
- **🎯 Streamlit**: Dashboard interactivo
- **📊 Plotly**: Visualizaciones dinámicas
- **🐼 Pandas**: Manipulación de datos
- **📓 Jupyter**: Análisis exploratorio

### Librerías Python
```txt
streamlit==1.28.0
plotly==5.17.0
pandas==2.1.0
psycopg2-binary==2.9.7
faker==19.6.0
pyspark==3.4.0
```

## 🔧 Configuración Detallada

### Variables de Entorno
```env
# PostgreSQL
POSTGRES_USER=insta
POSTGRES_PASSWORD=insta123
POSTGRES_DB=instashop

# Kafka
KAFKA_CLUSTER_ID=instashop-cluster-1
KAFKA_BROKERS=kafka1:9092,kafka2:9093,kafka3:9094

# Spark
SPARK_MASTER_URL=spark://spark:7077
```

### Puertos Utilizados
| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| PostgreSQL Main | 5432 | Base principal |
| CRM Database | 5433 | Sistema CRM |
| ERP Database | 5434 | Sistema ERP |
| E-commerce DB | 5435 | E-commerce |
| Data Warehouse | 5436 | DWH Analytics |
| Kafka Broker 1 | 9092 | Streaming |
| Kafka Broker 2 | 9093 | Streaming |
| Kafka Broker 3 | 9094 | Streaming |
| Spark Master | 8080 | Web UI |
| Jupyter | 8888 | Notebooks |
| **Dashboard** | **8501** | **Streamlit App** |

## 📈 Casos de Uso

### 🎯 Business Intelligence
- **Dashboards Ejecutivos**: KPIs en tiempo real
- **Análisis de Ventas**: Tendencias y patrones
- **Segmentación de Clientes**: Perfiles y comportamientos
- **Optimización de Inventario**: Gestión de stock

### 🔍 Análisis Avanzado
- **Predicción de Demanda**: Machine Learning
- **Detección de Anomalías**: Transacciones sospechosas
- **Recomendaciones**: Motor de productos
- **Análisis de Sentimiento**: Feedback de clientes

### 🚀 Escalabilidad
- **Multi-tenant**: Múltiples clientes
- **Microservicios**: Arquitectura distribuida
- **Real-time Processing**: Datos en tiempo real
- **Cloud Ready**: Preparado para la nube

## 🔄 Pipeline ETL

### Extracción
```python
# Datos de múltiples fuentes
- Transacciones (PostgreSQL)
- Clientes CRM (PostgreSQL)
- Inventario ERP (PostgreSQL)
- Eventos Kafka (Streaming)
```

### Transformación
```python
# Cálculos y agregaciones
- KPIs financieros
- Métricas de customer
- Estado de inventario
- Análisis temporal
```

### Carga
```python
# Data Warehouse
- Tablas dimensionales
- Hechos agregados
- Métricas históricas
- Cache del dashboard
```

## 🎨 Features del Dashboard

### 📊 Vista General
- **KPIs Principales**: Métricas clave en tiempo real
- **Filtros Temporales**: Análisis por período
- **Actualización Automática**: Cache de 1 minuto
- **Responsive Design**: Adaptable a dispositivos

### 📈 Análisis de Ventas
- **Gráfico de Tendencias**: Ventas diarias
- **Top Categorías**: Productos más vendidos
- **Métodos de Pago**: Distribución de pagos
- **Análisis Geográfico**: Ventas por región

### 👥 Gestión de Clientes
- **Segmentación**: Por plan de suscripción
- **Top Customers**: Mayores compradores
- **Análisis de Cohortes**: Retención temporal
- **Customer Journey**: Ruta del cliente

### 📦 Control de Inventario
- **Estado del Stock**: Crítico, Bajo, Óptimo
- **Alertas**: Productos con stock crítico
- **Rotación**: Velocidad de inventario
- **Predicción**: Demanda futura

## 🚨 Monitoreo y Alertas

### 🔍 Health Checks
```bash
# Verificar servicios
docker compose ps

# Logs de servicios
docker compose logs [servicio]

# Métricas de base de datos
docker compose exec postgres psql -U insta -d instashop -c "SELECT COUNT(*) FROM transaction;"
```

### 📧 Alertas Automáticas
- **Stock Crítico**: Productos por debajo del mínimo
- **Transacciones Fallidas**: Errores de pago
- **Performance**: Consultas lentas
- **Capacidad**: Uso de recursos

## 🔒 Seguridad

### 🔐 Autenticación
- Usuarios y contraseñas por base de datos
- Conexiones SSL/TLS habilitadas
- Tokens de API para servicios

### 🛡️ Autorización
- Roles por servicio
- Permisos granulares
- Auditoría de accesos

## 📚 Comandos Útiles

### 🐳 Docker
```bash
# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Reiniciar servicio específico
docker compose restart [servicio]

# Limpiar datos
docker compose down -v
```

### 🗄️ Base de Datos
```bash
# Conectar a PostgreSQL
docker compose exec postgres psql -U insta -d instashop

# Backup
docker compose exec postgres pg_dump -U insta instashop > backup.sql

# Restore
docker compose exec postgres psql -U insta -d instashop < backup.sql
```

### 🐍 Python
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar ETL
python local_etl.py

# Lanzar dashboard
streamlit run dashboard.py

python fake-data.py
```

## 🎯 Próximos Pasos

### 📈 Mejoras Planificadas

- [ ] **Machine Learning**: Modelos predictivos
- [ ] **API REST**: Endpoints para integración
- [ ] **Notificaciones**: Email/Slack alerts
- [ ] **Exportación**: PDF/Excel reports
- [ ] **Multi-idioma**: Soporte i18n

### 🚀 Escalabilidad

- [ ] **Kubernetes**: Orquestación avanzada
- [ ] **Redis Cache**: Cache distribuido
- [ ] **Load Balancer**: Alta disponibilidad
- [ ] **Monitoring**: Prometheus + Grafana

## 📞 Soporte

Para problemas o mejoras:

1. **🔍 Verificar logs**: `docker compose logs`
2. **🔄 Reiniciar servicios**: `docker compose restart`
3. **📧 Reportar issues**: Crear ticket con logs

---

**📊 InstaShop Analytics Platform** - Transformando datos en decisiones de negocio

Desarrollado con ❤️ usando Docker, Python y Streamlit
