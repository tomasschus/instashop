import random

import psycopg2
from faker import Faker

fake = Faker()

# ---- conexiones a múltiples DBs ----
conns = {
    "onlinestore": psycopg2.connect(
        dbname="instashop", user="insta", password="insta123", host="localhost", port="5432"
    ),
    "inventory": psycopg2.connect(
        dbname="erp_db", user="erp", password="erp123", host="localhost", port="5434"
    ),
    "logistics": psycopg2.connect(
        dbname="ecommerce_db", user="ecommerce", password="ecommerce123", host="localhost", port="5435"
    ),
    "crm": psycopg2.connect(
        dbname="crm_db", user="crm", password="crm123", host="localhost", port="5433"
    ),
}
cursors = {k: v.cursor() for k, v in conns.items()}

# =====================================================
# OnlineStore
# =====================================================
cursors["onlinestore"].execute("""
CREATE TABLE IF NOT EXISTS Customer (
    customer_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    business_name VARCHAR(150),
    email VARCHAR(100),
    phone VARCHAR(20),
    subscription_plan VARCHAR(50),
    logo_url VARCHAR(255),
    store_url VARCHAR(255)
);
""")
cursors["onlinestore"].execute("""
CREATE TABLE IF NOT EXISTS Buyer (
    buyer_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    shipping_address VARCHAR(255)
);
""")
cursors["onlinestore"].execute("""
CREATE TABLE IF NOT EXISTS Product (
    product_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES Customer(customer_id),
    name VARCHAR(150),
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(12,2),
    currency VARCHAR(10),
    status VARCHAR(20),
    image_url VARCHAR(255)
);
""")
cursors["onlinestore"].execute("""
CREATE TABLE IF NOT EXISTS Transaction (
    transaction_id BIGSERIAL PRIMARY KEY,
    buyer_id BIGINT REFERENCES Buyer(buyer_id),
    customer_id BIGINT REFERENCES Customer(customer_id),
    transaction_date TIMESTAMP,
    total_amount DECIMAL(12,2),
    payment_method VARCHAR(50),
    status VARCHAR(20)
);
""")
cursors["onlinestore"].execute("""
CREATE TABLE IF NOT EXISTS TransactionDetail (
    transaction_detail_id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT REFERENCES Transaction(transaction_id),
    product_id BIGINT REFERENCES Product(product_id),
    quantity INT,
    unit_price DECIMAL(12,2)
);
""")

# =====================================================
# Inventory
# =====================================================
cursors["inventory"].execute("""
CREATE TABLE IF NOT EXISTS Stock (
    stock_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT,
    available_quantity INT,
    reorder_point INT,
    warehouse_location VARCHAR(100)
);
""")
cursors["inventory"].execute("""
CREATE TABLE IF NOT EXISTS InventoryMovement (
    movement_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT,
    movement_date TIMESTAMP,
    movement_type VARCHAR(10),
    quantity INT,
    reason VARCHAR(100)
);
""")

# =====================================================
# Logistics
# =====================================================
cursors["logistics"].execute("""
CREATE TABLE IF NOT EXISTS Carrier (
    carrier_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    tracking_number VARCHAR(50)
);
""")
cursors["logistics"].execute("""
CREATE TABLE IF NOT EXISTS Shipment (
    shipment_id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT,
    buyer_id BIGINT,
    delivery_address VARCHAR(255),
    shipping_method VARCHAR(50),
    status VARCHAR(20),
    estimated_delivery_date TIMESTAMP
);
""")

# =====================================================
# CRM
# =====================================================
cursors["crm"].execute("""
CREATE TABLE IF NOT EXISTS Interaction (
    interaction_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT,
    interaction_type VARCHAR(50),
    channel VARCHAR(50),
    interaction_date TIMESTAMP,
    status VARCHAR(20)
);
""")
cursors["crm"].execute("""
CREATE TABLE IF NOT EXISTS Segment (
    segment_id BIGSERIAL PRIMARY KEY,
    segment_name VARCHAR(100),
    criteria TEXT
);
""")
cursors["crm"].execute("""
CREATE TABLE IF NOT EXISTS CustomerSegment (
    customer_segment_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT,
    segment_id BIGINT
);
""")

# =====================================================
# Generadores de datos
# =====================================================
def generate_customers(n):
    return [
        (
            fake.name(),
            fake.company(),
            fake.email(),
            fake.phone_number()[:20],  # Limitar a 20 caracteres
            random.choice(["Free", "Pro", "Enterprise"]),
            fake.image_url(),
            fake.url()
        )
        for _ in range(n)
    ]

def generate_buyers(n):
    return [
        (fake.name(), fake.email(), fake.phone_number()[:20], fake.address())  # Limitar a 20 caracteres
        for _ in range(n)
    ]

def generate_products(n, customer_ids):
    return [
        (
            random.choice(customer_ids),
            fake.word().title(),
            fake.text(max_nb_chars=50),
            random.choice(["Clothing", "Electronics", "Books", "Home", "Toys"]),
            round(random.uniform(5, 500), 2),
            "USD",
            random.choice(["active", "inactive"]),
            fake.image_url()
        )
        for _ in range(n)
    ]

def generate_transactions(n, buyer_ids, customer_ids):
    return [
        (
            random.choice(buyer_ids),
            random.choice(customer_ids),
            fake.date_time_this_year(),
            round(random.uniform(20, 1000), 2),
            random.choice(["Credit Card", "PayPal", "Wire"]),
            random.choice(["completed", "pending", "failed"])
        )
        for _ in range(n)
    ]

def generate_transaction_details(transaction_ids, product_ids):
    data = []
    for t_id in transaction_ids:
        for _ in range(random.randint(1, 5)):
            product_id = random.choice(product_ids)
            qty = random.randint(1, 3)
            price = round(random.uniform(5, 200), 2)
            data.append((t_id, product_id, qty, price))
    return data

def generate_stock(product_ids):
    return [
        (
            pid,
            random.randint(0, 500),
            random.randint(10, 50),
            fake.city()
        ) for pid in product_ids
    ]

def generate_inventory_movements(product_ids, n=500):
    return [
        (
            random.choice(product_ids),
            fake.date_time_this_year(),
            random.choice(["in", "out"]),
            random.randint(1, 50),
            random.choice(["purchase", "sale", "return"])
        )
        for _ in range(n)
    ]

def generate_carriers(n):
    return [
        (fake.company(), fake.phone_number()[:20], fake.uuid4()[:12].upper())  # Limitar teléfono a 20 caracteres
        for _ in range(n)
    ]

def generate_shipments(transactions, buyer_ids):
    return [
        (
            t_id,
            random.choice(buyer_ids),
            fake.address(),
            random.choice(["Standard", "Express", "Pickup"]),
            random.choice(["in_transit", "delivered", "pending"]),
            fake.date_time_between(start_date="now", end_date="+30d")
        )
        for t_id in transactions
    ]

def generate_segments():
    return [
        ("High Spenders", "Customers with monthly spend > 1000"),
        ("New Customers", "First transaction in last 30 days"),
        ("Inactive", "No purchase in last 6 months")
    ]

def generate_customer_segments(customer_ids, segment_ids):
    data = []
    for cid in customer_ids:
        if random.random() < 0.6:  # 60% entran a algún segmento
            sid = random.choice(segment_ids)
            data.append((cid, sid))
    return data

def generate_interactions(customer_ids, n=300):
    return [
        (
            random.choice(customer_ids),
            random.choice(["support", "complaint", "inquiry"]),
            random.choice(["chat", "email", "phone"]),
            fake.date_time_this_year(),
            random.choice(["open", "closed", "pending"])
        )
        for _ in range(n)
    ]

# =====================================================
# Inserciones
# =====================================================
print("Insertando Customers y Buyers...")
customers = generate_customers(100)  # Más customers para análisis de segmentación
buyers = generate_buyers(500)       # Más buyers para patrones de compra
cursors["onlinestore"].executemany(
    "INSERT INTO Customer (name, business_name, email, phone, subscription_plan, logo_url, store_url) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    customers
)
cursors["onlinestore"].executemany(
    "INSERT INTO Buyer (name, email, phone, shipping_address) VALUES (%s,%s,%s,%s)",
    buyers
)

cursors["onlinestore"].execute("SELECT customer_id FROM Customer;")
customer_ids = [r[0] for r in cursors["onlinestore"].fetchall()]
cursors["onlinestore"].execute("SELECT buyer_id FROM Buyer;")
buyer_ids = [r[0] for r in cursors["onlinestore"].fetchall()]

print("Insertando Products...")
products = generate_products(500, customer_ids)  # Más productos para análisis de catálogo
cursors["onlinestore"].executemany(
    "INSERT INTO Product (customer_id, name, description, category, price, currency, status, image_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
    products
)
cursors["onlinestore"].execute("SELECT product_id FROM Product;")
product_ids = [r[0] for r in cursors["onlinestore"].fetchall()]

print("Insertando Transactions...")
transactions = generate_transactions(1000, buyer_ids, customer_ids)  # Más transacciones para análisis de tendencias
cursors["onlinestore"].executemany(
    "INSERT INTO Transaction (buyer_id, customer_id, transaction_date, total_amount, payment_method, status) VALUES (%s,%s,%s,%s,%s,%s)",
    transactions
)
cursors["onlinestore"].execute("SELECT transaction_id FROM Transaction;")
transaction_ids = [r[0] for r in cursors["onlinestore"].fetchall()]

print("Insertando TransactionDetails...")
details = generate_transaction_details(transaction_ids, product_ids)
cursors["onlinestore"].executemany(
    "INSERT INTO TransactionDetail (transaction_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
    details
)

print("Insertando Stock e Inventory Movements...")
cursors["inventory"].executemany(
    "INSERT INTO Stock (product_id, available_quantity, reorder_point, warehouse_location) VALUES (%s,%s,%s,%s)",
    generate_stock(product_ids)
)
cursors["inventory"].executemany(
    "INSERT INTO InventoryMovement (product_id, movement_date, movement_type, quantity, reason) VALUES (%s,%s,%s,%s,%s)",
    generate_inventory_movements(product_ids, 1500)  # Más movimientos para análisis de inventario
)

print("Insertando Carriers y Shipments...")
carriers = generate_carriers(5)
cursors["logistics"].executemany(
    "INSERT INTO Carrier (name, phone, tracking_number) VALUES (%s,%s,%s)",
    carriers
)
shipments = generate_shipments(transaction_ids, buyer_ids)
cursors["logistics"].executemany(
    "INSERT INTO Shipment (transaction_id, buyer_id, delivery_address, shipping_method, status, estimated_delivery_date) VALUES (%s,%s,%s,%s,%s,%s)",
    shipments
)

print("Insertando Segments, CustomerSegments e Interactions...")
segments = generate_segments()
cursors["crm"].executemany(
    "INSERT INTO Segment (segment_name, criteria) VALUES (%s,%s)",
    segments
)
cursors["crm"].execute("SELECT segment_id FROM Segment;")
segment_ids = [r[0] for r in cursors["crm"].fetchall()]
customer_segments = generate_customer_segments(customer_ids, segment_ids)
cursors["crm"].executemany(
    "INSERT INTO CustomerSegment (customer_id, segment_id) VALUES (%s,%s)",
    customer_segments
)
interactions = generate_interactions(customer_ids, 800)  # Más interacciones para análisis CRM
cursors["crm"].executemany(
    "INSERT INTO Interaction (customer_id, interaction_type, channel, interaction_date, status) VALUES (%s,%s,%s,%s,%s)",
    interactions
)

# ---- commit & close ----
for k in conns:
    conns[k].commit()
    cursors[k].close()
    conns[k].close()

print("✅ Datos falsos insertados en OnlineStore, Inventory, Logistics y CRM!")
