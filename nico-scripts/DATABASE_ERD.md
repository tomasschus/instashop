# 🗄️ InstaShop Database ERD - Diagrama Entidad-Relación

## 📊 Diagrama ERD Completo

```mermaid
erDiagram
    %% ===========================================
    %% BASE DE DATOS: instashop (Puerto 5432)
    %% ===========================================
    
    Customer {
        bigserial customer_id PK
        varchar name
        varchar business_name
        varchar email
        varchar phone
        varchar subscription_plan
        varchar logo_url
        varchar store_url
    }
    
    Buyer {
        bigserial buyer_id PK
        varchar name
        varchar email
        varchar phone
        varchar shipping_address
    }
    
    Product {
        bigserial product_id PK
        bigint customer_id FK
        varchar name
        text description
        varchar category
        decimal price
        varchar currency
        varchar status
        varchar image_url
    }
    
    Transaction {
        bigserial transaction_id PK
        bigint buyer_id FK
        bigint customer_id FK
        timestamp transaction_date
        decimal total_amount
        varchar payment_method
        varchar status
    }
    
    TransactionDetail {
        bigserial transaction_detail_id PK
        bigint transaction_id FK
        bigint product_id FK
        int quantity
        decimal unit_price
    }
    
    %% ===========================================
    %% BASE DE DATOS: erp_db (Puerto 5434)
    %% ===========================================
    
    Stock {
        bigserial stock_id PK
        bigint product_id
        int available_quantity
        int reorder_point
        varchar warehouse_location
    }
    
    InventoryMovement {
        bigserial movement_id PK
        bigint product_id
        timestamp movement_date
        varchar movement_type
        int quantity
        varchar reason
    }
    
    %% ===========================================
    %% BASE DE DATOS: ecommerce_db (Puerto 5435)
    %% ===========================================
    
    Carrier {
        bigserial carrier_id PK
        varchar name
        varchar phone
        varchar tracking_number
    }
    
    Shipment {
        bigserial shipment_id PK
        bigint transaction_id
        bigint buyer_id
        varchar delivery_address
        varchar shipping_method
        varchar status
        timestamp estimated_delivery_date
    }
    
    %% ===========================================
    %% BASE DE DATOS: crm_db (Puerto 5433)
    %% ===========================================
    
    Interaction {
        bigserial interaction_id PK
        bigint customer_id
        varchar interaction_type
        varchar channel
        timestamp interaction_date
        varchar status
    }
    
    Segment {
        bigserial segment_id PK
        varchar segment_name
        text criteria
    }
    
    CustomerSegment {
        bigserial customer_segment_id PK
        bigint customer_id
        bigint segment_id
    }
    
    %% ===========================================
    %% BASE DE DATOS: dwh_db (Puerto 5436)
    %% ===========================================
    
    RealtimeEvents {
        bigserial id PK
        varchar event_type
        bigint customer_id
        bigint transaction_id
        bigint product_id
        varchar event_data
        timestamp timestamp
        timestamp processed_at
        varchar source
    }
    
    %% ===========================================
    %% RELACIONES PRINCIPALES
    %% ===========================================
    
    Customer ||--o{ Product : "owns"
    Customer ||--o{ Transaction : "receives"
    Buyer ||--o{ Transaction : "makes"
    Transaction ||--o{ TransactionDetail : "contains"
    Product ||--o{ TransactionDetail : "included_in"
    
    %% ===========================================
    %% RELACIONES SECUNDARIAS
    %% ===========================================
    
    Customer ||--o{ Interaction : "has"
    Customer ||--o{ CustomerSegment : "belongs_to"
    Segment ||--o{ CustomerSegment : "includes"
    
    %% ===========================================
    %% RELACIONES DE LOGÍSTICA
    %% ===========================================
    
    Transaction ||--o| Shipment : "shipped_via"
    Buyer ||--o{ Shipment : "receives"
    
    %% ===========================================
    %% RELACIONES DE INVENTARIO
    %% ===========================================
    
    Product ||--o{ Stock : "tracked_in"
    Product ||--o{ InventoryMovement : "moved_in"
```

## 🏗️ Estructura por Base de Datos

### **1. 📊 instashop (Puerto 5432) - E-commerce Principal**

```mermaid
erDiagram
    Customer {
        bigserial customer_id PK
        varchar name
        varchar business_name
        varchar email
        varchar phone
        varchar subscription_plan
        varchar logo_url
        varchar store_url
    }
    
    Buyer {
        bigserial buyer_id PK
        varchar name
        varchar email
        varchar phone
        varchar shipping_address
    }
    
    Product {
        bigserial product_id PK
        bigint customer_id FK
        varchar name
        text description
        varchar category
        decimal price
        varchar currency
        varchar status
        varchar image_url
    }
    
    Transaction {
        bigserial transaction_id PK
        bigint buyer_id FK
        bigint customer_id FK
        timestamp transaction_date
        decimal total_amount
        varchar payment_method
        varchar status
    }
    
    TransactionDetail {
        bigserial transaction_detail_id PK
        bigint transaction_id FK
        bigint product_id FK
        int quantity
        decimal unit_price
    }
    
    Customer ||--o{ Product : "owns"
    Customer ||--o{ Transaction : "receives"
    Buyer ||--o{ Transaction : "makes"
    Transaction ||--o{ TransactionDetail : "contains"
    Product ||--o{ TransactionDetail : "included_in"
```

### **2. 📦 erp_db (Puerto 5434) - Gestión de Inventario**

```mermaid
erDiagram
    Stock {
        bigserial stock_id PK
        bigint product_id
        int available_quantity
        int reorder_point
        varchar warehouse_location
    }
    
    InventoryMovement {
        bigserial movement_id PK
        bigint product_id
        timestamp movement_date
        varchar movement_type
        int quantity
        varchar reason
    }
    
    Product ||--o{ Stock : "tracked_in"
    Product ||--o{ InventoryMovement : "moved_in"
```

### **3. 🚚 ecommerce_db (Puerto 5435) - Logística**

```mermaid
erDiagram
    Carrier {
        bigserial carrier_id PK
        varchar name
        varchar phone
        varchar tracking_number
    }
    
    Shipment {
        bigserial shipment_id PK
        bigint transaction_id
        bigint buyer_id
        varchar delivery_address
        varchar shipping_method
        varchar status
        timestamp estimated_delivery_date
    }
    
    Transaction ||--o| Shipment : "shipped_via"
    Buyer ||--o{ Shipment : "receives"
```

### **4. 👥 crm_db (Puerto 5433) - Gestión de Clientes**

```mermaid
erDiagram
    Interaction {
        bigserial interaction_id PK
        bigint customer_id
        varchar interaction_type
        varchar channel
        timestamp interaction_date
        varchar status
    }
    
    Segment {
        bigserial segment_id PK
        varchar segment_name
        text criteria
    }
    
    CustomerSegment {
        bigserial customer_segment_id PK
        bigint customer_id
        bigint segment_id
    }
    
    Customer ||--o{ Interaction : "has"
    Customer ||--o{ CustomerSegment : "belongs_to"
    Segment ||--o{ CustomerSegment : "includes"
```

### **5. 🏢 dwh_db (Puerto 5436) - Data Warehouse**

```mermaid
erDiagram
    RealtimeEvents {
        bigserial id PK
        varchar event_type
        bigint customer_id
        bigint transaction_id
        bigint product_id
        varchar event_data
        timestamp timestamp
        timestamp processed_at
        varchar source
    }
```

## 📋 Descripción de Tablas

### **🏪 E-commerce Principal (instashop)**

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| **Customer** | Clientes que venden productos | customer_id, name, business_name, subscription_plan |
| **Buyer** | Compradores que realizan compras | buyer_id, name, email, shipping_address |
| **Product** | Productos vendidos por clientes | product_id, customer_id, name, category, price |
| **Transaction** | Transacciones de compra | transaction_id, buyer_id, customer_id, total_amount |
| **TransactionDetail** | Detalles de productos en transacciones | transaction_detail_id, transaction_id, product_id, quantity |

### **📦 Gestión de Inventario (erp_db)**

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| **Stock** | Control de inventario por producto | stock_id, product_id, available_quantity, reorder_point |
| **InventoryMovement** | Movimientos de inventario | movement_id, product_id, movement_type, quantity |

### **🚚 Logística (ecommerce_db)**

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| **Carrier** | Empresas de transporte | carrier_id, name, tracking_number |
| **Shipment** | Envíos de productos | shipment_id, transaction_id, buyer_id, status |

### **👥 CRM (crm_db)**

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| **Interaction** | Interacciones con clientes | interaction_id, customer_id, interaction_type, channel |
| **Segment** | Segmentos de clientes | segment_id, segment_name, criteria |
| **CustomerSegment** | Relación cliente-segmento | customer_segment_id, customer_id, segment_id |

### **🏢 Data Warehouse (dwh_db)**

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| **RealtimeEvents** | Eventos en tiempo real procesados | id, event_type, customer_id, timestamp, source |

## 🔗 Relaciones Principales

1. **Customer** → **Product** (1:N) - Un cliente puede tener muchos productos
2. **Customer** → **Transaction** (1:N) - Un cliente puede recibir muchas transacciones
3. **Buyer** → **Transaction** (1:N) - Un comprador puede hacer muchas transacciones
4. **Transaction** → **TransactionDetail** (1:N) - Una transacción puede tener muchos detalles
5. **Product** → **TransactionDetail** (1:N) - Un producto puede estar en muchos detalles
6. **Customer** → **Interaction** (1:N) - Un cliente puede tener muchas interacciones
7. **Transaction** → **Shipment** (1:1) - Una transacción puede tener un envío

## 🎯 Tipos de Datos Utilizados

- **BIGSERIAL**: Claves primarias auto-incrementales
- **BIGINT**: Claves foráneas
- **VARCHAR**: Texto de longitud variable
- **TEXT**: Texto largo
- **DECIMAL(12,2)**: Números decimales para precios
- **TIMESTAMP**: Fechas y horas
- **INT**: Números enteros
