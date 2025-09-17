# 🚀 Comandos para Ejecutar el Pipeline CDC Completo

## 📋 Lista de Comandos Paso a Paso - Dual Pipeline CDC

### **1. 🐍 Activar Entorno Virtual**
```bash
# Navegar al directorio del proyecto
cd /home/nicolas/Documents/uade/instashop

# Activar entorno virtual
source venv/bin/activate
```

### **2. 🐳 Levantar Docker (Todos los Servicios)**
```bash
# Levantar todos los contenedores
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

### **3. 🔧 Configurar CDC (Change Data Capture)**
```bash
# Configurar PostgreSQL para CDC
python nico-scripts/init_postgres_cdc.py

# Desplegar conectores Debezium
python nico-scripts/setup_debezium.py
```

### **4. 📊 Generar Eventos en PostgreSQL**
```bash
# Generar datos iniciales
python fake-data.py

# Ejecutar generador de datos realistas (CDC automático)
python nico-scripts/realistic_data_generator.py
```

### **5. 🗄️ Pipeline Histórico: CDC → Data Warehouse**
```bash
# En una nueva terminal (mantener activado el venv)
source venv/bin/activate

# Ejecutar consumer CDC → DWH
python nico-scripts/cdc_dwh_consumer.py
```

### **6. ⚡ Pipeline Tiempo Real: CDC → Spark → Redis**
```bash
# En otra nueva terminal (mantener activado el venv)
source venv/bin/activate

# Ejecutar Spark Streaming CDC → Redis
python nico-scripts/spark-streaming/cdc_spark_redis.py
```

### **7. 📊 Levantar Dashboard**
```bash
# En otra nueva terminal (mantener activado el venv)
source venv/bin/activate

# Ejecutar dashboard de Streamlit (CDC + Spark + Redis)
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py
```

---

## 🔄 Orden Recomendado de Ejecución - Dual Pipeline CDC

### **Terminal 1: Generador de Datos (CDC Automático)**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
python nico-scripts/realistic_data_generator.py
```

### **Terminal 2: Pipeline Histórico (CDC → DWH)**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
python nico-scripts/cdc_dwh_consumer.py
```

### **Terminal 3: Pipeline Tiempo Real (CDC → Spark → Redis)**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
python nico-scripts/spark-streaming/cdc_spark_redis.py
```

### **Terminal 4: Dashboard (CDC + Spark + Redis)**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py
```

---

## 🎯 URLs Importantes

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Dashboard** | http://localhost:8501 | Streamlit Analytics |
| **Spark UI** | http://localhost:8080 | Spark Web Interface |
| **Jupyter** | http://localhost:8888 | Jupyter Notebooks |

---

## 🔍 Comandos de Monitoreo

### **Ver Logs de Docker**
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f kafka1
docker-compose logs -f spark
docker-compose logs -f dwh-db
```

### **Ver Estado de Contenedores**
```bash
# Estado de todos los contenedores
docker-compose ps

# Ver uso de recursos
docker stats
```

### **Verificar Conexiones**
```bash
# Verificar Kafka
docker exec -it kafka1 kafka-topics.sh --list --bootstrap-server localhost:9092

# Verificar PostgreSQL
docker exec -it postgres_db psql -U insta -d instashop -c "SELECT COUNT(*) FROM Transaction;"
```

---

## 🛠️ Comandos de Troubleshooting

### **Reiniciar Servicios**
```bash
# Reiniciar un servicio específico
docker-compose restart kafka1

# Reiniciar todos los servicios
docker-compose restart
```

### **Limpiar y Reiniciar**
```bash
# Detener todos los servicios
docker-compose down

# Limpiar volúmenes (¡CUIDADO! Borra datos)
docker-compose down -v

# Levantar de nuevo
docker-compose up -d
```

### **Ver Logs de Error**
```bash
# Ver logs de error de un servicio
docker-compose logs --tail=50 kafka1

# Ver logs en tiempo real
docker-compose logs -f --tail=100
```

---

## 📊 Dual Pipeline CDC Completo

```
PostgreSQL ──→ Debezium ──→ Kafka ──→ Python Consumer ──→ DWH ──→ Dashboard
    ↑              ↑           ↑            ↑              ↑
realistic_data  CDC Engine  CDC Topics   cdc_dwh_    Streamlit
_generator.py   (Automatic)             consumer.py  Dashboard
                                    ↓
                               Spark Streaming
                               (cdc_spark_redis.py)
                                    ↓
                                  Redis
                               (Real-time Cache)
```

### 🔄 Flujos de Datos

#### **Pipeline Histórico (DWH)**
```
PostgreSQL → Debezium → Kafka → Python Consumer → DWH PostgreSQL
```
- **Datos**: Eventos individuales preservados
- **Propósito**: Análisis histórico y reportes
- **Latencia**: Cerca de tiempo real

#### **Pipeline Tiempo Real (Redis)**
```
PostgreSQL → Debezium → Kafka → Spark Streaming → Redis → Dashboard
```
- **Datos**: Métricas agregadas y calculadas
- **Propósito**: Dashboard interactivo
- **Latencia**: Sub-segundo

---

## ⚡ Comandos Rápidos

### **Ejecutar Dual Pipeline CDC en Secuencia**
```bash
# 1. Activar venv
source venv/bin/activate

# 2. Levantar Docker
docker-compose up -d

# 3. Esperar 30 segundos para que los servicios estén listos
sleep 30

# 4. Configurar CDC
python nico-scripts/init_postgres_cdc.py
python nico-scripts/setup_debezium.py

# 5. Generar datos iniciales
python fake-data.py

# 6. Ejecutar generador CDC (en background)
python nico-scripts/realistic_data_generator.py &

# 7. Ejecutar pipeline histórico (en background)
python nico-scripts/cdc_dwh_consumer.py &

# 8. Ejecutar pipeline tiempo real (en background)
python nico-scripts/spark-streaming/cdc_spark_redis.py &

# 9. Levantar dashboard
streamlit run nico-scripts/dashboards/realtime_spark_dashboard.py
```

---

## 🎉 ¡Dual Pipeline CDC Listo!

Con estos comandos tienes todo el sistema CDC funcionando:
- ✅ **CDC Automático**: Debezium captura cambios de PostgreSQL
- ✅ **Pipeline Histórico**: CDC → DWH para análisis histórico
- ✅ **Pipeline Tiempo Real**: CDC → Spark → Redis para dashboard
- ✅ **Dashboard Interactivo**: Métricas en tiempo real
- ✅ **Monitoreo Completo**: Ambos pipelines funcionando simultáneamente

### 🎯 Beneficios del Dual Pipeline CDC
- **📊 Tiempo Real**: Dashboard con métricas actualizadas al instante
- **🗄️ Histórico**: Datos preservados para análisis a largo plazo
- **⚡ Escalabilidad**: Separación de responsabilidades
- **🔄 Resiliencia**: Fallback entre sistemas
- **🎨 Flexibilidad**: Diferentes latencias para diferentes necesidades
