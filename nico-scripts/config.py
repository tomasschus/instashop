#!/usr/bin/env python3
"""
⚙️ Configuración para Nico Scripts
Configuración centralizada para todos los scripts de generación de datos
"""

# Configuración de bases de datos
DATABASE_CONFIG = {
    'instashop': {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'instashop',
        'user': 'insta',
        'password': 'insta123'
    },
    'crm': {
        'host': 'localhost',
        'port': 5433,
        'dbname': 'crm_db',
        'user': 'crm',
        'password': 'crm123'
    },
    'erp': {
        'host': 'localhost',
        'port': 5434,
        'dbname': 'erp_db',
        'user': 'erp',
        'password': 'erp123'
    },
    'ecommerce': {
        'host': 'localhost',
        'port': 5435,
        'dbname': 'ecommerce_db',
        'user': 'ecommerce',
        'password': 'ecommerce123'
    },
    'dwh': {
        'host': 'localhost',
        'port': 5436,
        'dbname': 'dwh_db',
        'user': 'dwh',
        'password': 'dwh123'
    }
}

# Configuración de patrones de comportamiento
BEHAVIOR_PATTERNS = {
    'customer_segments': {
        'high_value': {
            'frequency': 0.15,
            'avg_order_value': (200, 800),
            'purchase_frequency': (2, 8),
            'preferred_categories': ['Electronics', 'Home'],
            'payment_methods': ['Credit Card', 'Wire Transfer'],
            'subscription_plans': ['Enterprise', 'Pro']
        },
        'regular': {
            'frequency': 0.60,
            'avg_order_value': (50, 200),
            'purchase_frequency': (1, 3),
            'preferred_categories': ['Clothing', 'Books'],
            'payment_methods': ['Credit Card', 'PayPal'],
            'subscription_plans': ['Pro', 'Free']
        },
        'bargain_hunter': {
            'frequency': 0.25,
            'avg_order_value': (10, 80),
            'purchase_frequency': (3, 10),
            'preferred_categories': ['Toys', 'Books'],
            'payment_methods': ['PayPal'],
            'subscription_plans': ['Free']
        }
    },
    'time_patterns': {
        'hourly_activity': {
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
}

# Configuración de productos
PRODUCT_CATALOG = {
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
        'price_volatility': 0.05
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

# Configuración de eventos
EVENT_CONFIG = {
    'event_types': ['transaction', 'page_view', 'product_view', 'search', 'add_to_cart', 'remove_from_cart', 'checkout'],
    'event_weights': {
        'page_view': 0.40,
        'product_view': 0.25,
        'search': 0.15,
        'add_to_cart': 0.15,
        'remove_from_cart': 0.05
    },
    'transaction_status': {
        'completed': 0.85,
        'pending': 0.10,
        'failed': 0.05
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file_handlers': {
        'data_generator': 'nico-scripts/data_generator.log',
        'behavior_simulator': 'nico-scripts/behavior_simulator.log',
        'realtime_monitor': 'nico-scripts/realtime_monitor.log'
    }
}

# Configuración de puertos
PORTS = {
    'streamlit_dashboard': 8503,
    'jupyter': 8888,
    'spark_ui': 8080
}

# Configuración de intervalos
INTERVALS = {
    'base_event_interval': 30,  # segundos
    'market_trend_update': 300,  # segundos (5 minutos)
    'metrics_log_interval': 50,  # eventos
    'dashboard_refresh': 30  # segundos
}

# Configuración de límites
LIMITS = {
    'max_customers': 100,
    'max_products_per_category': 8,
    'max_cart_items': 5,
    'max_session_duration': 600,  # segundos
    'max_events_per_batch': 100
}
