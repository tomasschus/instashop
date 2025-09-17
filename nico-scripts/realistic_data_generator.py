#!/usr/bin/env python3
"""
🚀 InstaShop Realistic Data Generator
Genera datos en tiempo real con patrones de comportamiento realistas
"""

import random
import time
import threading
import json
import psycopg2
from datetime import datetime, timedelta, timezone
from faker import Faker
import numpy as np
from collections import defaultdict
import logging

# Desactivar logs de debug de Faker
logging.getLogger('faker').setLevel(logging.WARNING)

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

fake = Faker('es_ES')  # Datos en español

class RealisticDataGenerator:
    def __init__(self):
        self.conns = self._setup_connections()
        self.cursors = {k: v.cursor() for k, v in self.conns.items()}
        
        # Patrones de comportamiento realistas
        self.customer_profiles = self._create_customer_profiles()
        self.product_catalog = self._create_product_catalog()
        self.behavior_patterns = self._create_behavior_patterns()
        
        # Estado del sistema
        self.active_customers = set()
        self.session_data = defaultdict(dict)
        self.running = True
        
        # Verificar e inicializar datos básicos si es necesario
        self._initialize_basic_data()
        
        logger.info("🚀 RealisticDataGenerator inicializado")

    def _initialize_basic_data(self):
        """Inicializar datos básicos si las tablas están vacías"""
        try:
            # Verificar si las tablas existen y están vacías
            cursor = self.cursors["instashop"]
            
            # Verificar si las tablas existen
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('customer', 'buyer', 'product')
            """)
            table_count = cursor.fetchone()[0]
            
            if table_count < 3:  # Si no existen las 3 tablas principales
                logger.info("🔧 Tablas no existen, creando...")
                self._create_tables_if_not_exist()
                return
            
            # Verificar tabla Customer
            cursor.execute("SELECT COUNT(*) FROM Customer")
            customer_count = cursor.fetchone()[0]
            
            # Verificar tabla Buyer
            cursor.execute("SELECT COUNT(*) FROM Buyer")
            buyer_count = cursor.fetchone()[0]
            
            # Verificar tabla Product
            cursor.execute("SELECT COUNT(*) FROM Product")
            product_count = cursor.fetchone()[0]
            
            logger.info(f"📊 Estado inicial: {customer_count} clientes, {buyer_count} compradores, {product_count} productos")
            
            # Si no hay datos básicos, crearlos
            if customer_count == 0:
                logger.info("🔧 Inicializando datos básicos...")
                self._create_initial_customers()
                self._create_initial_buyers()
                self._create_initial_products()
                logger.info("✅ Datos básicos inicializados")
            else:
                logger.info("✅ Datos básicos ya existen")
                # Verificar que las secuencias estén correctas
                self._fix_sequences()
                
        except Exception as e:
            logger.error(f"❌ Error verificando datos básicos: {e}")
            logger.info("🔧 Intentando crear tablas...")
            self._create_tables_if_not_exist()

    def _create_tables_if_not_exist(self):
        """Crear tablas si no existen"""
        try:
            # Crear nueva conexión para evitar problemas de transacción
            conn = psycopg2.connect(
                dbname="instashop", user="insta", password="insta123", 
                host="localhost", port="5432"
            )
            cursor = conn.cursor()
            
            # Crear tabla Customer
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Customer (
                    customer_id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    business_name VARCHAR(150),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    subscription_plan VARCHAR(50),
                    logo_url VARCHAR(255),
                    store_url VARCHAR(255)
                )
            """)
            
            # Crear tabla Buyer
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Buyer (
                    buyer_id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    shipping_address VARCHAR(255)
                )
            """)
            
            # Crear tabla Product
            cursor.execute("""
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
                )
            """)
            
            # Crear tabla Transaction
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Transaction (
                    transaction_id BIGSERIAL PRIMARY KEY,
                    buyer_id BIGINT REFERENCES Buyer(buyer_id),
                    customer_id BIGINT REFERENCES Customer(customer_id),
                    transaction_date TIMESTAMP,
                    total_amount DECIMAL(12,2),
                    payment_method VARCHAR(50),
                    status VARCHAR(20)
                )
            """)
            
            # Crear tabla TransactionDetail
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS TransactionDetail (
                    transaction_detail_id BIGSERIAL PRIMARY KEY,
                    transaction_id BIGINT REFERENCES Transaction(transaction_id),
                    product_id BIGINT REFERENCES Product(product_id),
                    quantity INT,
                    unit_price DECIMAL(12,2)
                )
            """)
            
            conn.commit()
            logger.info("✅ Tablas de InstaShop creadas exitosamente")
            
            # Crear tabla Interaction en CRM
            crm_conn = psycopg2.connect(
                dbname="crm_db", user="crm", password="crm123", 
                host="localhost", port="5433"
            )
            crm_cursor = crm_conn.cursor()
            crm_cursor.execute("""
                CREATE TABLE IF NOT EXISTS Interaction (
                    interaction_id BIGSERIAL PRIMARY KEY,
                    customer_id BIGINT,
                    interaction_type VARCHAR(50),
                    channel VARCHAR(50),
                    interaction_date TIMESTAMP,
                    status VARCHAR(20)
                )
            """)
            crm_conn.commit()
            logger.info("✅ Tabla Interaction en CRM creada exitosamente")
            
            # Cerrar conexiones temporales
            cursor.close()
            conn.close()
            crm_cursor.close()
            crm_conn.close()
            
            # Crear datos iniciales
            self._create_initial_customers()
            self._create_initial_buyers()
            self._create_initial_products()
            
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass

    def _fix_sequences(self):
        """Arreglar las secuencias de PostgreSQL para evitar conflictos de IDs"""
        try:
            cursor = self.cursors["instashop"]
            
            # Arreglar secuencia de Customer
            cursor.execute("SELECT setval('customer_customer_id_seq', (SELECT MAX(customer_id) FROM Customer));")
            
            # Arreglar secuencia de Buyer
            cursor.execute("SELECT setval('buyer_buyer_id_seq', (SELECT MAX(buyer_id) FROM Buyer));")
            
            # Arreglar secuencia de Product
            cursor.execute("SELECT setval('product_product_id_seq', (SELECT MAX(product_id) FROM Product));")
            
            # Arreglar secuencia de Transaction
            cursor.execute("SELECT setval('transaction_transaction_id_seq', (SELECT MAX(transaction_id) FROM Transaction));")
            
            # Arreglar secuencia de TransactionDetail
            cursor.execute("SELECT setval('transactiondetail_transaction_detail_id_seq', (SELECT MAX(transaction_detail_id) FROM TransactionDetail));")
            
            self.conns["instashop"].commit()
            logger.info("✅ Secuencias de PostgreSQL arregladas")
            
        except Exception as e:
            logger.error(f"❌ Error arreglando secuencias: {e}")
            self.conns["instashop"].rollback()

    def _create_initial_customers(self):
        """Crear clientes iniciales"""
        try:
            cursor = self.cursors["instashop"]
            
            for i in range(1, 51):  # Crear 50 clientes iniciales
                cursor.execute("""
                    INSERT INTO Customer (customer_id, name, business_name, email, phone, subscription_plan)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id) DO NOTHING
                """, (
                    i,
                    f"Cliente {i}",
                    f"Empresa {i}",
                    f"cliente{i}@example.com",
                    f"+123456789{i:03d}",
                    random.choice(['Free', 'Premium', 'Enterprise'])
                ))
            
            self.conns["instashop"].commit()
            logger.info("✅ 50 clientes iniciales creados")
            
        except Exception as e:
            logger.error(f"❌ Error creando clientes iniciales: {e}")
            self.conns["instashop"].rollback()

    def _create_initial_buyers(self):
        """Crear compradores iniciales"""
        try:
            cursor = self.cursors["instashop"]
            
            for i in range(1, 101):  # Crear 100 compradores iniciales
                cursor.execute("""
                    INSERT INTO Buyer (buyer_id, name, email, phone, shipping_address)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (buyer_id) DO NOTHING
                """, (
                    i,
                    f"Comprador {i}",
                    f"buyer{i}@example.com",
                    f"+987654321{i:03d}",
                    f"Dirección {i}, Ciudad"
                ))
            
            self.conns["instashop"].commit()
            logger.info("✅ 100 compradores iniciales creados")
            
        except Exception as e:
            logger.error(f"❌ Error creando compradores iniciales: {e}")
            self.conns["instashop"].rollback()

    def _create_initial_products(self):
        """Crear productos iniciales"""
        try:
            cursor = self.cursors["instashop"]
            
            categories = ['Electronics', 'Fashion', 'Home', 'Books', 'Toys', 'Sports', 'Food', 'Basic', 'Accessories']
            
            for i in range(1, 201):  # Crear 200 productos iniciales
                customer_id = random.randint(1, 50)
                category = random.choice(categories)
                
                cursor.execute("""
                    INSERT INTO Product (product_id, customer_id, name, description, category, price, currency, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (product_id) DO NOTHING
                """, (
                    i,
                    customer_id,
                    f"Producto {i}",
                    f"Descripción del producto {i}",
                    category,
                    round(random.uniform(10, 500), 2),
                    'USD',
                    'active'
                ))
            
            self.conns["instashop"].commit()
            logger.info("✅ 200 productos iniciales creados")
            
        except Exception as e:
            logger.error(f"❌ Error creando productos iniciales: {e}")
            self.conns["instashop"].rollback()

    def _setup_connections(self):
        """Configurar conexiones a las bases de datos"""
        return {
            "instashop": psycopg2.connect(
                dbname="instashop", user="insta", password="insta123", 
                host="localhost", port="5432"
            ),
            "crm": psycopg2.connect(
                dbname="crm_db", user="crm", password="crm123", 
                host="localhost", port="5433"
            ),
            "erp": psycopg2.connect(
                dbname="erp_db", user="erp", password="erp123", 
                host="localhost", port="5434"
            ),
            "ecommerce": psycopg2.connect(
                dbname="ecommerce_db", user="ecommerce", password="ecommerce123", 
                host="localhost", port="5435"
            ),
            "dwh": psycopg2.connect(
                dbname="dwh_db", user="dwh", password="dwh123", 
                host="localhost", port="5436"
            )
        }

    def _create_customer_profiles(self):
        """Crear perfiles de clientes realistas"""
        profiles = {
            'high_value': {
                'frequency': 0.15,  # 15% de clientes
                'avg_order_value': (200, 800),
                'purchase_frequency': (2, 8),  # veces por semana
                'preferred_categories': ['Electronics', 'Home'],
                'payment_methods': ['Credit Card', 'Wire Transfer'],
                'subscription_plans': ['Enterprise', 'Pro']
            },
            'regular': {
                'frequency': 0.60,  # 60% de clientes
                'avg_order_value': (50, 200),
                'purchase_frequency': (1, 3),
                'preferred_categories': ['Clothing', 'Books'],
                'payment_methods': ['Credit Card', 'PayPal'],
                'subscription_plans': ['Pro', 'Free']
            },
            'bargain_hunter': {
                'frequency': 0.25,  # 25% de clientes
                'avg_order_value': (10, 80),
                'purchase_frequency': (3, 10),
                'preferred_categories': ['Toys', 'Books'],
                'payment_methods': ['PayPal'],
                'subscription_plans': ['Free']
            }
        }
        return profiles

    def _create_product_catalog(self):
        """Crear catálogo de productos con precios realistas"""
        catalog = {
            'Electronics': {
                'products': [
                    ('iPhone 15 Pro', 999.99, 'Smartphone premium'),
                    ('MacBook Air M2', 1299.99, 'Laptop profesional'),
                    ('Samsung Galaxy S24', 799.99, 'Smartphone Android'),
                    ('iPad Pro', 1099.99, 'Tablet profesional'),
                    ('AirPods Pro', 249.99, 'Auriculares inalámbricos'),
                    ('Apple Watch', 399.99, 'Reloj inteligente'),
                    ('Sony PlayStation 5', 499.99, 'Consola de videojuegos'),
                    ('Nintendo Switch', 299.99, 'Consola portátil')
                ],
                'seasonality': {'peak_months': [11, 12], 'low_months': [1, 2]},
                'price_volatility': 0.05  # 5% de variación
            },
            'Clothing': {
                'products': [
                    ('Camiseta Premium', 29.99, 'Camiseta de algodón orgánico'),
                    ('Jeans Clásicos', 79.99, 'Jeans de mezclilla'),
                    ('Zapatillas Deportivas', 129.99, 'Calzado deportivo'),
                    ('Chaqueta de Invierno', 199.99, 'Abrigo para frío'),
                    ('Vestido Elegante', 149.99, 'Vestido para ocasiones especiales'),
                    ('Pantalón Formal', 89.99, 'Pantalón de vestir'),
                    ('Sudadera con Capucha', 59.99, 'Ropa casual'),
                    ('Botas de Cuero', 179.99, 'Calzado de cuero genuino')
                ],
                'seasonality': {'peak_months': [9, 10, 11], 'low_months': [6, 7, 8]},
                'price_volatility': 0.15
            },
            'Books': {
                'products': [
                    ('Libro de Programación', 49.99, 'Guía completa de Python'),
                    ('Novela Bestseller', 19.99, 'Ficción contemporánea'),
                    ('Libro de Cocina', 34.99, 'Recetas internacionales'),
                    ('Biografía Histórica', 24.99, 'Vida de personajes históricos'),
                    ('Libro Infantil', 14.99, 'Cuentos para niños'),
                    ('Manual Técnico', 79.99, 'Guía técnica especializada'),
                    ('Libro de Autoayuda', 16.99, 'Desarrollo personal'),
                    ('Enciclopedia Digital', 99.99, 'Conocimiento general')
                ],
                'seasonality': {'peak_months': [1, 9], 'low_months': [6, 7]},
                'price_volatility': 0.02
            },
            'Home': {
                'products': [
                    ('Aspiradora Robot', 299.99, 'Limpieza automática'),
                    ('Cafetera Espresso', 199.99, 'Café profesional'),
                    ('Sofá Modular', 899.99, 'Mueble de sala'),
                    ('Lámpara LED', 79.99, 'Iluminación moderna'),
                    ('Cortinas Elegantes', 129.99, 'Decoración de ventanas'),
                    ('Mesa de Comedor', 599.99, 'Mueble de comedor'),
                    ('Silla Ergonómica', 249.99, 'Silla de oficina'),
                    ('Alfombra Persa', 399.99, 'Decoración de suelo')
                ],
                'seasonality': {'peak_months': [3, 4, 5], 'low_months': [11, 12]},
                'price_volatility': 0.08
            },
            'Toys': {
                'products': [
                    ('Lego Creator', 89.99, 'Juguete de construcción'),
                    ('Muñeca Interactiva', 59.99, 'Juguete para niñas'),
                    ('Coche Teledirigido', 79.99, 'Vehículo control remoto'),
                    ('Puzzle 1000 Piezas', 24.99, 'Juego de mesa'),
                    ('Set de Química', 49.99, 'Juguete educativo'),
                    ('Pelota de Fútbol', 19.99, 'Deporte y recreación'),
                    ('Kit de Arte', 34.99, 'Materiales creativos'),
                    ('Juego de Mesa Familiar', 39.99, 'Entretenimiento grupal')
                ],
                'seasonality': {'peak_months': [11, 12], 'low_months': [1, 2, 3]},
                'price_volatility': 0.20
            }
        }
        return catalog

    def _create_behavior_patterns(self):
        """Crear patrones de comportamiento basados en horarios reales"""
        return {
            'hourly_activity': {
                # Actividad por hora del día (0-23)
                0: 0.02, 1: 0.01, 2: 0.01, 3: 0.01, 4: 0.01, 5: 0.02,
                6: 0.05, 7: 0.08, 8: 0.12, 9: 0.15, 10: 0.18, 11: 0.20,
                12: 0.25, 13: 0.22, 14: 0.20, 15: 0.18, 16: 0.15, 17: 0.12,
                18: 0.15, 19: 0.20, 20: 0.25, 21: 0.30, 22: 0.20, 23: 0.10
            },
            'weekly_patterns': {
                'Monday': 0.12, 'Tuesday': 0.15, 'Wednesday': 0.18,
                'Thursday': 0.20, 'Friday': 0.25, 'Saturday': 0.30, 'Sunday': 0.20
            },
            'seasonal_multipliers': {
                'Spring': 1.1, 'Summer': 0.9, 'Autumn': 1.2, 'Winter': 1.3
            }
        }

    def _get_current_activity_level(self):
        """Calcular nivel de actividad actual basado en patrones realistas"""
        now = datetime.now(timezone.utc)
        hour = now.hour
        day = now.strftime('%A')
        month = now.month
        
        # Factor por hora
        hourly_factor = self.behavior_patterns['hourly_activity'][hour]
        
        # Factor por día de la semana
        weekly_factor = self.behavior_patterns['weekly_patterns'][day]
        
        # Factor estacional
        if month in [12, 1, 2]:
            seasonal_factor = self.behavior_patterns['seasonal_multipliers']['Winter']
        elif month in [3, 4, 5]:
            seasonal_factor = self.behavior_patterns['seasonal_multipliers']['Spring']
        elif month in [6, 7, 8]:
            seasonal_factor = self.behavior_patterns['seasonal_multipliers']['Summer']
        else:
            seasonal_factor = self.behavior_patterns['seasonal_multipliers']['Autumn']
        
        # Asegurar un mínimo de actividad para generar datos frecuentes
        base_activity = hourly_factor * weekly_factor * seasonal_factor
        return max(base_activity, 0.8)  # Mínimo 0.8 para asegurar datos frecuentes

    def _get_customer_profile(self, customer_id):
        """Obtener perfil de cliente basado en comportamiento histórico"""
        # Simular perfil basado en ID (en producción sería consulta real)
        rand = customer_id % 100
        if rand < 15:
            return 'high_value'
        elif rand < 75:
            return 'regular'
        else:
            return 'bargain_hunter'
    
    def _ensure_customer_exists(self, customer_id):
        """Asegurar que el cliente existe en la base de datos"""
        try:
            cursor = self.cursors["instashop"]
            
            # Verificar si el cliente existe
            query = "SELECT customer_id FROM Customer WHERE customer_id = %s"
            cursor.execute(query, (customer_id,))
            result = cursor.fetchone()
            
            if not result:
                # Crear cliente
                insert_query = """
                    INSERT INTO Customer (customer_id, name, business_name, email, phone, subscription_plan)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    customer_id,
                    f"Cliente {customer_id}",
                    f"Empresa {customer_id}",
                    f"cliente{customer_id}@example.com",
                    f"+123456789{customer_id:03d}",
                    random.choice(['Free', 'Premium', 'Enterprise'])
                ))
                self.conns["instashop"].commit()
                
        except Exception as e:
            logger.error(f"❌ Error creando cliente: {e}")
    
    def _ensure_buyer_exists(self, buyer_id):
        """Asegurar que el comprador existe en la base de datos"""
        try:
            cursor = self.cursors["instashop"]
            
            # Verificar si el comprador existe
            query = "SELECT buyer_id FROM Buyer WHERE buyer_id = %s"
            cursor.execute(query, (buyer_id,))
            result = cursor.fetchone()
            
            if not result:
                # Crear comprador
                insert_query = """
                    INSERT INTO Buyer (buyer_id, name, email, phone, shipping_address)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    buyer_id,
                    f"Comprador {buyer_id}",
                    f"buyer{buyer_id}@example.com",
                    f"+987654321{buyer_id:03d}",
                    f"Dirección {buyer_id}, Ciudad"
                ))
                self.conns["instashop"].commit()
                
        except Exception as e:
            logger.error(f"❌ Error creando comprador {buyer_id}: {e}")
    
    def _get_or_create_product(self, product_name, category, base_price, description, customer_id):
        """Obtener o crear producto en la base de datos"""
        try:
            cursor = self.cursors["instashop"]
            
            # Buscar producto existente
            query = "SELECT product_id FROM Product WHERE name = %s AND customer_id = %s"
            cursor.execute(query, (product_name, customer_id))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Crear nuevo producto
                insert_query = """
                    INSERT INTO Product (customer_id, name, description, category, price, currency, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING product_id
                """
                cursor.execute(insert_query, (
                    customer_id,
                    product_name,
                    description,
                    category,
                    base_price,
                    'USD',
                    'active'
                ))
                product_id = cursor.fetchone()[0]
                self.conns["instashop"].commit()
                return product_id
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo/creando producto: {e}")
            # Rollback para limpiar la transacción abortada
            try:
                self.conns["instashop"].rollback()
            except:
                pass
            # Fallback: buscar un producto existente aleatorio
            try:
                cursor.execute("SELECT product_id FROM Product ORDER BY RANDOM() LIMIT 1")
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
            except:
                return None

    def _generate_realistic_transaction(self):
        """Generar transacción realista"""
        # Obtener cliente activo o crear sesión nueva
        if not self.active_customers or random.random() < 0.3:
            customer_id = random.randint(1, 500)  # Ampliar rango para evitar conflictos
            self.active_customers.add(customer_id)
        else:
            customer_id = random.choice(list(self.active_customers))
        
        # Asegurar que el cliente existe
        self._ensure_customer_exists(customer_id)
        
        profile = self._get_customer_profile(customer_id)
        profile_data = self.customer_profiles[profile]
        
        # Generar productos basados en preferencias del perfil
        category = random.choice(profile_data['preferred_categories'])
        products = self.product_catalog[category]['products']
        
        # Crear carrito de compras realista
        cart_items = []
        num_items = random.randint(1, 5) if profile == 'bargain_hunter' else random.randint(1, 3)
        
        for _ in range(num_items):
            product_name, base_price, description = random.choice(products)
            
            # Obtener product_id real de la base de datos
            product_id = self._get_or_create_product(product_name, category, base_price, description, customer_id)
            
            # Aplicar variación de precio estacional
            price_variation = self.product_catalog[category]['price_volatility']
            price_multiplier = random.uniform(1 - price_variation, 1 + price_variation)
            final_price = round(base_price * price_multiplier, 2)
            
            quantity = random.randint(1, 3) if profile == 'bargain_hunter' else random.randint(1, 2)
            
            cart_items.append({
                'product_id': product_id,
                'product_name': product_name,
                'price': final_price,
                'quantity': quantity,
                'category': category,
                'description': description
            })
        
        # Calcular total
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Aplicar descuentos ocasionales
        if random.random() < 0.15:  # 15% de probabilidad de descuento
            discount = random.uniform(0.05, 0.25)
            total_amount *= (1 - discount)
        
        # Método de pago basado en perfil
        payment_method = random.choice(profile_data['payment_methods'])
        
        # Estado de transacción realista
        if random.random() < 0.05:  # 5% de transacciones fallidas
            status = 'failed'
        elif random.random() < 0.10:  # 10% pendientes
            status = 'pending'
        else:
            status = 'completed'
        
        # Generar buyer_id
        buyer_id = random.randint(1, 500)  # Ampliar rango para evitar conflictos
        
        # Asegurar que el comprador existe
        self._ensure_buyer_exists(buyer_id)
        
        return {
            'customer_id': customer_id,
            'customer_profile': profile,
            'buyer_id': buyer_id,
            'cart_items': cart_items,
            'total_amount': round(total_amount, 2),
            'payment_method': payment_method,
            'status': status,
            'timestamp': datetime.now(timezone.utc)
        }

    def _generate_user_behavior_event(self):
        """Generar evento de comportamiento de usuario"""
        event_types = ['page_view', 'product_view', 'search', 'add_to_cart', 'remove_from_cart']
        
        # Distribución realista de eventos
        event_weights = {
            'page_view': 0.40,
            'product_view': 0.25,
            'search': 0.15,
            'add_to_cart': 0.15,
            'remove_from_cart': 0.05
        }
        
        # Normalizar las probabilidades para asegurar que sumen exactamente 1.0
        weights = list(event_weights.values())
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalizar
        
        event_type = np.random.choice(list(event_weights.keys()), p=weights)
        
        customer_id = random.randint(1, 100)
        
        event_data = {
            'customer_id': customer_id,
            'event_type': event_type,
            'timestamp': datetime.now(timezone.utc),
            'session_id': f"session_{customer_id}_{int(time.time())}"
        }
        
        if event_type == 'search':
            search_terms = [
                'smartphone', 'laptop', 'ropa', 'libros', 'juguetes',
                'electrodomésticos', 'decoración', 'zapatos', 'accesorios'
            ]
            event_data['search_term'] = random.choice(search_terms)
            event_data['results_count'] = random.randint(5, 50)
        
        elif event_type in ['product_view', 'add_to_cart', 'remove_from_cart']:
            category = random.choice(list(self.product_catalog.keys()))
            products = self.product_catalog[category]['products']
            product_name, price, description = random.choice(products)
            
            event_data['product_name'] = product_name
            event_data['product_category'] = category
            event_data['product_price'] = price
        
        return event_data

    def _insert_transaction_to_db(self, transaction_data):
        """Insertar transacción en la base de datos"""
        try:
            # Insertar transacción principal
            transaction_query = """
                INSERT INTO Transaction (buyer_id, customer_id, transaction_date, total_amount, payment_method, status)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING transaction_id
            """
            
            # Usar el buyer_id que ya verificamos en _generate_realistic_transaction
            buyer_id = transaction_data['buyer_id']
            
            self.cursors["instashop"].execute(transaction_query, (
                buyer_id,
                transaction_data['customer_id'],
                transaction_data['timestamp'],
                transaction_data['total_amount'],
                transaction_data['payment_method'],
                transaction_data['status']
            ))
            
            transaction_id = self.cursors["instashop"].fetchone()[0]
            
            # Insertar detalles de transacción
            for item in transaction_data['cart_items']:
                # Buscar product_id por nombre (simplificado)
                product_query = "SELECT product_id FROM Product WHERE name = %s LIMIT 1"
                self.cursors["instashop"].execute(product_query, (item['product_name'],))
                result = self.cursors["instashop"].fetchone()
                
                if result:
                    product_id = result[0]
                    detail_query = """
                        INSERT INTO TransactionDetail (transaction_id, product_id, quantity, unit_price)
                        VALUES (%s, %s, %s, %s)
                    """
                    self.cursors["instashop"].execute(detail_query, (
                        transaction_id, product_id, item['quantity'], item['price']
                    ))
            
            self.conns["instashop"].commit()
            
        except Exception as e:
            logger.error(f"❌ Error insertando transacción: {e}")
            self.conns["instashop"].rollback()


    def _insert_behavior_event_to_crm(self, event_data):
        """Insertar evento de comportamiento en CRM usando tabla Interaction existente"""
        try:
            # Mapear tipos de evento a tipos de interacción
            interaction_mapping = {
                'page_view': 'website_visit',
                'product_view': 'product_inquiry',
                'search': 'search_query',
                'add_to_cart': 'purchase_intent',
                'remove_from_cart': 'cart_abandonment'
            }
            
            interaction_type = interaction_mapping.get(event_data['event_type'], 'general')
            channel = random.choice(['website', 'mobile_app', 'desktop'])
            
            query = """
                INSERT INTO Interaction (customer_id, interaction_type, channel, interaction_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            self.cursors["crm"].execute(query, (
                event_data['customer_id'],
                interaction_type,
                channel,
                event_data['timestamp'],
                'completed'
            ))
            
            self.conns["crm"].commit()
            
        except Exception as e:
            logger.error(f"❌ Error insertando evento en CRM: {e}")
            self.conns["crm"].rollback()

    def start_realistic_data_generation(self, duration_minutes=60):
        """Iniciar generación de datos realistas"""
        logger.info(f"🚀 Iniciando generación de datos realistas por {duration_minutes} minutos")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        transaction_count = 0
        behavior_event_count = 0
        
        logger.info("🔄 Iniciando bucle de generación de datos...")
        logger.info(f"⏰ Duración: {duration_minutes} minutos")
        logger.info(f"🎯 Objetivo: ~{duration_minutes * 600} eventos (~10 por segundo, 70% transacciones)")
        
        while time.time() < end_time and self.running:
            try:
                # Calcular intervalo basado en actividad actual
                activity_level = self._get_current_activity_level()
                
                # Intervalo base entre eventos (en segundos)
                base_interval = 0.1  # 0.1 segundos base para ~10 datos por segundo
                current_interval = base_interval / activity_level
                
                # Agregar variabilidad mínima para mantener ~10 por segundo
                interval = random.uniform(current_interval * 0.8, current_interval * 1.2)
                
                # Decidir qué tipo de evento generar
                if random.random() < 0.7:  # 70% probabilidad de transacción para más datos
                    transaction_data = self._generate_realistic_transaction()
                    self._insert_transaction_to_db(transaction_data)
                    transaction_count += 1
                    
                
                else:  # 30% probabilidad de evento de comportamiento
                    behavior_event = self._generate_user_behavior_event()
                    self._insert_behavior_event_to_crm(behavior_event)
                    behavior_event_count += 1
                
                # Log de progreso cada 50 eventos para reducir spam
                total_events = transaction_count + behavior_event_count
                if total_events % 50 == 0:
                    logger.info(f"📈 Progreso: {total_events} eventos generados ({transaction_count} transacciones, {behavior_event_count} comportamientos)")
                
                
                # Esperar antes del siguiente evento
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Generación detenida por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en generación: {e}")
                time.sleep(5)  # Esperar antes de reintentar
        
        logger.info(f"✅ Generación completada: {transaction_count} transacciones, {behavior_event_count} eventos de comportamiento")
        self._cleanup()

    def _cleanup(self):
        """Limpiar conexiones"""
        for cursor in self.cursors.values():
            cursor.close()
        for conn in self.conns.values():
            conn.close()
        logger.info("🧹 Conexiones cerradas")

    def stop(self):
        """Detener generación"""
        self.running = False
        logger.info("⏹️ Solicitando detener generación...")

def main():
    """Función principal"""
    print("🚀 InstaShop Realistic Data Generator")
    print("=" * 50)
    
    generator = RealisticDataGenerator()
    
    try:
        duration = int(input("¿Cuántos minutos generar datos? (default: 60): ") or "60")
        generator.start_realistic_data_generation(duration)
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo generación...")
        generator.stop()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
