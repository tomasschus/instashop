# 🚀 Comandos para Ejecutar el Pipeline Completo

## 📋 Lista de Comandos Paso a Paso

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

### **3. 📊 Generar Eventos en PostgreSQL**
```bash
# Ejecutar generador de datos realistas
python nico-scripts/realistic_data_generator.py

# O usar el script de setup
python nico-scripts/setup_and_run.py
```

### **4. 📤 Ver Logs de Pusheo a Kafka (Producer)**
```bash
# En una nueva terminal (mantener activado el venv)
source venv/bin/activate

# Ejecutar producer dinámico
python nico-scripts/kafka-streaming/dynamic_producer.py
```

### **5. 📥 Ver Logs de Consumo Kafka (Consumer)**
```bash
# En otra nueva terminal (mantener activado el venv)
source venv/bin/activate

# Ejecutar consumer dinámico
python nico-scripts/kafka-streaming/dynamic_consumer.py
```

### **6. ⚡ Ver Logs de Spark Streaming**
```bash
# En otra nueva terminal (mantener activado el venv)
source venv/bin/activate

# Ejecutar Spark Streaming desde Kafka
python nico-scripts/spark-streaming/kafka_streaming_analytics.py
```

### **7. 📊 Levantar Dashboard**
```bash
# En otra nueva terminal (mantener activado el venv)
source venv/bin/activate

# Ejecutar dashboard de Streamlit
streamlit run nico-scripts/dashboards/realtime_analytics_dashboard.py
```

---

## 🔄 Orden Recomendado de Ejecución

### **Terminal 1: Generador de Datos**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
python nico-scripts/realistic_data_generator.py
```

### **Terminal 2: Producer Kafka**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
python nico-scripts/kafka-streaming/dynamic_producer.py
```

### **Terminal 3: Consumer Kafka**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
python nico-scripts/kafka-streaming/dynamic_consumer.py
```

### **Terminal 4: Spark Streaming**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
python nico-scripts/spark-streaming/kafka_streaming_analytics.py
```

### **Terminal 5: Dashboard**
```bash
cd /home/nicolas/Documents/uade/instashop
source venv/bin/activate
streamlit run nico-scripts/dashboards/realtime_analytics_dashboard.py
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

## 📊 Pipeline Completo

```
PostgreSQL ──→ Producer ──→ Kafka ──→ Consumer ──→ DWH ──→ Dashboard
    ↑              ↑           ↑         ↑         ↑
realistic_data  dynamic_   Topics    dynamic_  Streamlit
_generator.py   producer.py          consumer.py Dashboard
                                    ↓
                               Spark Streaming
                               (kafka_streaming_analytics.py)
```

---

## ⚡ Comandos Rápidos

### **Ejecutar Todo en Secuencia**
```bash
# 1. Activar venv
source venv/bin/activate

# 2. Levantar Docker
docker-compose up -d

# 3. Esperar 30 segundos para que los servicios estén listos
sleep 30

# 4. Ejecutar generador (en background)
python nico-scripts/realistic_data_generator.py &

# 5. Ejecutar producer (en background)
python nico-scripts/kafka-streaming/dynamic_producer.py &

# 6. Ejecutar consumer (en background)
python nico-scripts/kafka-streaming/dynamic_consumer.py &

# 7. Ejecutar Spark (en background)
python nico-scripts/spark-streaming/kafka_streaming_analytics.py &

# 8. Levantar dashboard
streamlit run nico-scripts/dashboards/realtime_analytics_dashboard.py
```

---

## 🎉 ¡Listo para Ejecutar!

Con estos comandos tienes todo el pipeline funcionando:
- ✅ Generación de datos en PostgreSQL
- ✅ Streaming a Kafka
- ✅ Procesamiento con Spark
- ✅ Dashboard en tiempo real
- ✅ Monitoreo completo
