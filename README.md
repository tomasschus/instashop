# 🛒 InstaShop Analytics Platform

Plataforma completa de análisis de datos para comercio electrónico usando Docker, PostgreSQL, Kafka y Apache Spark con dashboard en tiempo real.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Kafka      │    │   Apache Spark  │
│   (5 bases)     │    │   (3 brokers)   │    │   + Jupyter     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
         ┌─────────────────────────────────────────────────────┐
         │              🎯 Streamlit Dashboard                │
         │           📊 Business Intelligence                 │
         └─────────────────────────────────────────────────────┘
```

### 🗄️ Bases de Datos (PostgreSQL)
- **instashop** (Puerto 5432): Base principal con transacciones, customers y productos
- **crm_db** (Puerto 5433): Sistema CRM con datos de clientes
- **erp_db** (Puerto 5434): Sistema ERP con inventario y stock
- **ecommerce_db** (Puerto 5435): Datos de e-commerce
- **dwh_db** (Puerto 5436): Data Warehouse para análisis

### ⚡ Streaming (Apache Kafka)
- **kafka1** (Puerto 9092): Broker principal
- **kafka2** (Puerto 9093): Broker secundario  
- **kafka3** (Puerto 9094): Broker terciario

### 🔥 Big Data (Apache Spark)
- **Spark Master** (Puerto 8080): Interfaz web de Spark
- **Jupyter Notebook** (Puerto 8888): Análisis interactivo

## 🚀 Inicio Rápido

### 1. Levantar la Infraestructura
```bash
docker compose up -d
```

### 2. Poblar con Datos de Prueba
```bash
# Activar entorno virtual
.\env\Scripts\activate

# Ejecutar generación de datos
python fake-data.py
```

### 3. Ejecutar ETL Pipeline
```bash
python local_etl.py
```

### 4. Lanzar Dashboard
```bash
streamlit run dashboard.py --server.port 8501
```

**🌐 Dashboard disponible en:** http://localhost:8501

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
├── 🐳 docker-compose.yml       # Orquestación de servicios
├── 🎯 dashboard.py             # Dashboard Streamlit
├── 🔄 local_etl.py            # Pipeline ETL
├── 📊 fake-data.py            # Generador de datos
├── 📁 data/                   # Datos persistentes PostgreSQL
├── 🐍 env/                    # Entorno virtual Python
└── 📋 README.md              # Este archivo
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

# Generar datos de prueba
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

*Desarrollado con ❤️ usando Docker, Python y Streamlit*
