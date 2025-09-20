# 🏗️ InstaShop Big Data Pipeline - Arquitectura

## 📊 Diagrama de Arquitectura

```mermaid
graph TB
    %% Generación de Datos
    subgraph "📊 Generación de Datos"
        DG[realistic_data_generator.py]
        DG --> |"Transacciones + Eventos"| PG1[(PostgreSQL<br/>instashop)]
        DG --> |"Interacciones CRM"| PG2[(PostgreSQL<br/>crm_db)]
    end

    %% Kafka Producer
    subgraph "📤 Kafka Producer"
        KP[dynamic_producer.py]
        PG1 --> |"Consulta cada 2s<br/>Ventana: 2 min"| KP
        PG2 --> |"Consulta cada 2s<br/>Ventana: 2 min"| KP
    end

    %% Kafka Cluster
    subgraph "📨 Kafka Cluster"
        K1[kafka1:9092]
        K2[kafka2:9093]
        K3[kafka3:9094]
        
        KP --> |"transactions"| K1
        KP --> |"user_behavior"| K2
        KP --> |"searches"| K3
        KP --> |"cart_events"| K1
    end

    %% Kafka Consumer
    subgraph "📥 Kafka Consumer"
        KC[dynamic_consumer.py]
        K1 --> KC
        K2 --> KC
        K3 --> KC
    end

    %% Data Warehouse
    subgraph "🏢 Data Warehouse"
        DWH[(PostgreSQL<br/>dwh_db)]
        KC --> |"realtime_events"| DWH
        KC --> |"transaction_items<br/>enriquecidos"| K1
    end

    %% Spark Streaming
    subgraph "⚡ Spark Streaming"
        SS[realtime_metrics_producer.py]
        K1 --> |"transactions"| SS
        K2 --> |"user_behavior"| SS
        K1 --> |"transaction_items"| SS
    end

    %% Redis
    subgraph "💾 Redis Cache"
        RD[(Redis<br/>redis-metrics)]
        SS --> |"Métricas en tiempo real"| RD
    end

    %% Dashboard
    subgraph "📊 Dashboard"
        DS[realtime_spark_dashboard.py]
        RD --> |"Métricas en tiempo real"| DS
        DWH --> |"Datos históricos"| DS
    end

    %% Usuario
    USER[👤 Usuario] --> |"http://localhost:8501"| DS

    %% Estilos
    classDef generator fill:#e1f5fe
    classDef kafka fill:#fff3e0
    classDef database fill:#f3e5f5
    classDef spark fill:#e8f5e8
    classDef dashboard fill:#fff8e1

    class DG,KP generator
    class K1,K2,K3,KC kafka
    class PG1,PG2,DWH,RD database
    class SS spark
    class DS,USER dashboard
```

## 🔄 Flujo de Datos Detallado

### **1. Generación de Datos (realistic_data_generator.py)**
```
┌─────────────────┐    ┌─────────────────┐
│   Generador     │───▶│   PostgreSQL    │
│   - Transacciones│    │   instashop     │
│   - Comportamiento│   │   crm_db        │
└─────────────────┘    └─────────────────┘
```

### **2. Producer Kafka (dynamic_producer.py)**
```
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │───▶│   Producer      │
│   - Consulta 2s │    │   - Sin duplicados│
│   - Ventana 2min│    │   - Todos topics│
└─────────────────┘    └─────────────────┘
```

### **3. Kafka Cluster**
```
┌─────────────────┐    ┌─────────────────┐
│   Producer      │───▶│   Kafka Topics  │
│                 │    │   - transactions │
│                 │    │   - user_behavior│
│                 │    │   - searches     │
│                 │    │   - cart_events  │
└─────────────────┘    └─────────────────┘
```

### **4. Consumer Kafka (dynamic_consumer.py)**
```
┌─────────────────┐    ┌─────────────────┐
│   Kafka Topics  │───▶│   Consumer      │
│                 │    │   - Group ID único│
│                 │    │   - earliest     │
│                 │    │   - commit manual│
└─────────────────┘    └─────────────────┘
```

### **5. Data Warehouse**
```
┌─────────────────┐    ┌─────────────────┐
│   Consumer      │───▶│   DWH PostgreSQL │
│                 │    │   - realtime_events│
│                 │    │   - Datos históricos│
└─────────────────┘    └─────────────────┘
```

### **6. Spark Streaming (realtime_metrics_producer.py)**
```
┌─────────────────┐    ┌─────────────────┐
│   Kafka Topics  │───▶│   Spark         │
│                 │    │   - Watermark 10s│
│                 │    │   - Ventana 30s │
│                 │    │   - Agregaciones│
└─────────────────┘    └─────────────────┘
```

### **7. Redis Cache**
```
┌─────────────────┐    ┌─────────────────┐
│   Spark         │───▶│   Redis         │
│                 │    │   - Métricas    │
│                 │    │   - TTL 1 hora  │
│                 │    │   - Tiempo real │
└─────────────────┘    └─────────────────┘
```

### **8. Dashboard (realtime_spark_dashboard.py)**
```
┌─────────────────┐    ┌─────────────────┐
│   Redis + DWH   │───▶│   Streamlit     │
│                 │    │   - Auto-refresh│
│                 │    │   - Gráficos    │
│                 │    │   - KPIs        │
└─────────────────┘    └─────────────────┘
```

## 🎯 Componentes por Puerto

| Componente | Puerto | Descripción |
|------------|--------|-------------|
| **PostgreSQL instashop** | 5432 | Base de datos principal |
| **PostgreSQL crm_db** | 5432 | Base de datos CRM |
| **PostgreSQL dwh_db** | 5436 | Data Warehouse |
| **Kafka kafka1** | 9092 | Broker Kafka 1 |
| **Kafka kafka2** | 9093 | Broker Kafka 2 |
| **Kafka kafka3** | 9094 | Broker Kafka 3 |
| **Redis** | 6379 | Cache de métricas |
| **Spark Master** | 8080 | UI de Spark |
| **Streamlit** | 8501 | Dashboard |

## 🔧 Configuraciones Clave

### **Generador**
- **Frecuencia**: 0.1 segundos
- **Distribución**: 70% transacciones, 30% comportamientos
- **Timestamps**: UTC
- **Auto-inicialización**: Tablas y datos básicos

### **Producer**
- **Consulta**: Cada 2 segundos
- **Ventana**: Últimos 2 minutos
- **Duplicados**: Sin protección (envía todo)
- **Topics**: transactions, user_behavior, searches, cart_events

### **Consumer**
- **Group ID**: Único por timestamp
- **Offset**: earliest (lee mensajes viejos)
- **Commit**: Manual después de procesar
- **Envío adicional**: transaction_items a Kafka

### **Spark**
- **Watermark**: 10 segundos
- **Ventana**: 30 segundos
- **Starting offsets**: earliest
- **Métricas**: Transacciones, comportamiento, productos

### **Dashboard**
- **Auto-refresh**: Cada 5 segundos
- **Fuentes**: Redis (tiempo real) + DWH (histórico)
- **Gráficos**: KPIs, productos, comportamiento, histórico
