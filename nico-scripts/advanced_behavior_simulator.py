#!/usr/bin/env python3
"""
🧠 InstaShop Advanced Behavior Simulator
Simulador avanzado de comportamiento de usuarios con patrones complejos
"""

import random
import time
import json
import psycopg2
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
from collections import defaultdict, deque
import logging
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional
import math

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

fake = Faker('es_ES')

@dataclass
class CustomerJourney:
    """Representa el journey de un cliente"""
    customer_id: int
    session_id: str
    start_time: datetime
    current_page: str
    cart_items: List[Dict]
    total_value: float
    behavior_score: float
    conversion_probability: float

@dataclass
class MarketTrend:
    """Representa tendencias del mercado"""
    category: str
    demand_multiplier: float
    price_trend: float
    seasonality_factor: float
    competitor_activity: float

class AdvancedBehaviorSimulator:
    def __init__(self):
        self.conns = self._setup_connections()
        self.cursors = {k: v.cursor() for k, v in self.conns.items()}
        
        # Estado del simulador
        self.active_sessions = {}  # customer_id -> CustomerJourney
        self.market_trends = self._initialize_market_trends()
        self.behavior_patterns = self._create_advanced_patterns()
        self.running = True
        
        # Métricas en tiempo real
        self.metrics = {
            'total_sessions': 0,
            'conversions': 0,
            'cart_abandonments': 0,
            'bounce_rate': 0,
            'avg_session_duration': 0,
            'revenue': 0
        }
        
        logger.info("🧠 AdvancedBehaviorSimulator inicializado")

    def _setup_connections(self):
        """Configurar conexiones a las bases de datos"""
        return {
            "instashop": psycopg2.connect(
                dbname="instashop", user="insta", password="insta123", 
                host="localhost", port="5432"
            ),
            "dwh": psycopg2.connect(
                dbname="dwh_db", user="dwh", password="dwh123", 
                host="localhost", port="5436"
            )
        }

    def _initialize_market_trends(self):
        """Inicializar tendencias del mercado"""
        trends = {}
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Toys']
        
        for category in categories:
            trends[category] = MarketTrend(
                category=category,
                demand_multiplier=random.uniform(0.8, 1.3),
                price_trend=random.uniform(-0.1, 0.1),  # -10% a +10%
                seasonality_factor=random.uniform(0.7, 1.4),
                competitor_activity=random.uniform(0.5, 1.5)
            )
        
        return trends

    def _create_advanced_patterns(self):
        """Crear patrones de comportamiento avanzados"""
        return {
            'customer_segments': {
                'explorer': {
                    'frequency': 0.20,
                    'browse_time': (120, 300),  # segundos
                    'pages_per_session': (5, 15),
                    'conversion_rate': 0.15,
                    'preferred_actions': ['search', 'browse', 'compare']
                },
                'buyer': {
                    'frequency': 0.35,
                    'browse_time': (60, 180),
                    'pages_per_session': (3, 8),
                    'conversion_rate': 0.45,
                    'preferred_actions': ['direct_purchase', 'quick_buy']
                },
                'researcher': {
                    'frequency': 0.25,
                    'browse_time': (300, 600),
                    'pages_per_session': (10, 25),
                    'conversion_rate': 0.25,
                    'preferred_actions': ['read_reviews', 'compare_specs', 'research']
                },
                'window_shopper': {
                    'frequency': 0.20,
                    'browse_time': (30, 120),
                    'pages_per_session': (2, 6),
                    'conversion_rate': 0.05,
                    'preferred_actions': ['browse', 'view', 'leave']
                }
            },
            'time_patterns': {
                'rush_hours': [8, 12, 18, 20],  # Horas pico
                'quiet_hours': [2, 3, 4, 5],   # Horas tranquilas
                'weekend_multiplier': 1.3,     # Más actividad en fin de semana
                'lunch_break_boost': 1.2      # Boost durante almuerzo
            },
            'seasonal_patterns': {
                'holiday_season': {'months': [11, 12], 'multiplier': 2.0},
                'back_to_school': {'months': [8, 9], 'multiplier': 1.5},
                'summer_sale': {'months': [6, 7], 'multiplier': 1.3},
                'new_year': {'months': [1], 'multiplier': 1.4}
            }
        }

    def _calculate_dynamic_pricing(self, base_price: float, category: str, demand_level: float) -> float:
        """Calcular precios dinámicos basados en demanda y tendencias"""
        trend = self.market_trends[category]
        
        # Factor de demanda
        demand_factor = 1 + (demand_level - 0.5) * 0.2  # ±10% basado en demanda
        
        # Factor de tendencia de precios
        price_trend_factor = 1 + trend.price_trend
        
        # Factor de competencia
        competition_factor = 1 - (trend.competitor_activity - 1) * 0.1
        
        # Factor de estacionalidad
        seasonal_factor = trend.seasonality_factor
        
        # Precio final con variación aleatoria
        final_price = base_price * demand_factor * price_trend_factor * competition_factor * seasonal_factor
        final_price *= random.uniform(0.95, 1.05)  # ±5% variación aleatoria
        
        return round(final_price, 2)

    def _simulate_customer_journey(self, customer_id: int) -> CustomerJourney:
        """Simular el journey completo de un cliente"""
        # Determinar segmento de cliente
        segment = self._get_customer_segment(customer_id)
        segment_data = self.behavior_patterns['customer_segments'][segment]
        
        # Crear sesión
        session_id = f"session_{customer_id}_{int(time.time())}"
        start_time = datetime.now()
        
        # Simular tiempo de navegación
        browse_time = random.uniform(*segment_data['browse_time'])
        pages_to_visit = random.randint(*segment_data['pages_per_session'])
        
        # Inicializar journey
        journey = CustomerJourney(
            customer_id=customer_id,
            session_id=session_id,
            start_time=start_time,
            current_page="homepage",
            cart_items=[],
            total_value=0.0,
            behavior_score=0.0,
            conversion_probability=segment_data['conversion_rate']
        )
        
        return journey

    def _get_customer_segment(self, customer_id: int) -> str:
        """Determinar segmento de cliente basado en comportamiento histórico"""
        # Simular segmento basado en ID (en producción sería ML)
        segments = list(self.behavior_patterns['customer_segments'].keys())
        weights = np.array([data['frequency'] for data in self.behavior_patterns['customer_segments'].values()])
        weights = weights / weights.sum()  # Normalizar
        
        return np.random.choice(segments, p=weights)

    def _simulate_page_interaction(self, journey: CustomerJourney) -> Dict:
        """Simular interacción en una página"""
        segment = self._get_customer_segment(journey.customer_id)
        segment_data = self.behavior_patterns['customer_segments'][segment]
        
        # Determinar acción basada en preferencias del segmento
        action_weights = {
            'search': 0.25,
            'browse': 0.30,
            'view_product': 0.20,
            'add_to_cart': 0.15,
            'remove_from_cart': 0.05,
            'checkout': 0.05
        }
        
        # Ajustar pesos según segmento
        if segment == 'buyer':
            action_weights['add_to_cart'] = 0.30
            action_weights['checkout'] = 0.20
        elif segment == 'researcher':
            action_weights['view_product'] = 0.40
            action_weights['search'] = 0.30
        
        # Normalizar las probabilidades
        weights = np.array(list(action_weights.values()))
        weights = weights / weights.sum()  # Normalizar
        
        action = np.random.choice(list(action_weights.keys()), p=weights)
        
        interaction_data = {
            'customer_id': journey.customer_id,
            'session_id': journey.session_id,
            'action': action,
            'timestamp': datetime.now(),
            'page': journey.current_page,
            'segment': segment
        }
        
        # Simular datos específicos de la acción
        if action == 'search':
            search_terms = [
                'smartphone', 'laptop', 'ropa de invierno', 'libros de programación',
                'juguetes educativos', 'electrodomésticos', 'decoración hogar',
                'zapatos deportivos', 'accesorios moda', 'herramientas'
            ]
            interaction_data['search_term'] = random.choice(search_terms)
            interaction_data['results_count'] = random.randint(10, 100)
        
        elif action in ['view_product', 'add_to_cart']:
            categories = list(self.market_trends.keys())
            category = random.choice(categories)
            
            # Simular productos realistas
            products = self._get_realistic_products(category)
            product = random.choice(products)
            
            interaction_data['product_name'] = product['name']
            interaction_data['product_category'] = category
            interaction_data['product_price'] = self._calculate_dynamic_pricing(
                product['base_price'], category, random.uniform(0.3, 0.8)
            )
            
            if action == 'add_to_cart':
                quantity = random.randint(1, 3)
                journey.cart_items.append({
                    'product_name': product['name'],
                    'price': interaction_data['product_price'],
                    'quantity': quantity,
                    'category': category
                })
                journey.total_value += interaction_data['product_price'] * quantity
        
        elif action == 'checkout':
            interaction_data['cart_value'] = journey.total_value
            interaction_data['payment_method'] = random.choice(['Credit Card', 'PayPal', 'Wire Transfer'])
            interaction_data['shipping_address'] = fake.address()
        
        return interaction_data

    def _get_realistic_products(self, category: str) -> List[Dict]:
        """Obtener productos realistas por categoría"""
        products = {
            'Electronics': [
                {'name': 'iPhone 15 Pro', 'base_price': 999.99},
                {'name': 'MacBook Air M2', 'base_price': 1299.99},
                {'name': 'Samsung Galaxy S24', 'base_price': 799.99},
                {'name': 'iPad Pro', 'base_price': 1099.99},
                {'name': 'AirPods Pro', 'base_price': 249.99}
            ],
            'Clothing': [
                {'name': 'Camiseta Premium', 'base_price': 29.99},
                {'name': 'Jeans Clásicos', 'base_price': 79.99},
                {'name': 'Zapatillas Deportivas', 'base_price': 129.99},
                {'name': 'Chaqueta de Invierno', 'base_price': 199.99},
                {'name': 'Vestido Elegante', 'base_price': 149.99}
            ],
            'Books': [
                {'name': 'Libro de Programación', 'base_price': 49.99},
                {'name': 'Novela Bestseller', 'base_price': 19.99},
                {'name': 'Libro de Cocina', 'base_price': 34.99},
                {'name': 'Biografía Histórica', 'base_price': 24.99},
                {'name': 'Libro Infantil', 'base_price': 14.99}
            ],
            'Home': [
                {'name': 'Aspiradora Robot', 'base_price': 299.99},
                {'name': 'Cafetera Espresso', 'base_price': 199.99},
                {'name': 'Sofá Modular', 'base_price': 899.99},
                {'name': 'Lámpara LED', 'base_price': 79.99},
                {'name': 'Cortinas Elegantes', 'base_price': 129.99}
            ],
            'Toys': [
                {'name': 'Lego Creator', 'base_price': 89.99},
                {'name': 'Muñeca Interactiva', 'base_price': 59.99},
                {'name': 'Coche Teledirigido', 'base_price': 79.99},
                {'name': 'Puzzle 1000 Piezas', 'base_price': 24.99},
                {'name': 'Set de Química', 'base_price': 49.99}
            ]
        }
        return products.get(category, [])

    def _calculate_conversion_probability(self, journey: CustomerJourney) -> float:
        """Calcular probabilidad de conversión basada en comportamiento"""
        base_probability = journey.conversion_probability
        
        # Factores que aumentan conversión
        cart_value_factor = min(journey.total_value / 100, 1.0)  # Más valor = más conversión
        session_duration_factor = min(len(journey.cart_items) / 5, 1.0)  # Más items = más conversión
        
        # Factores que disminuyen conversión
        time_factor = 1.0  # Tiempo en sitio (implementar si es necesario)
        
        # Factor de tendencias del mercado
        market_factor = 1.0
        if journey.cart_items:
            category = journey.cart_items[0]['category']
            market_factor = self.market_trends[category].demand_multiplier
        
        final_probability = base_probability * (1 + cart_value_factor * 0.3) * (1 + session_duration_factor * 0.2) * market_factor
        
        return min(final_probability, 0.95)  # Máximo 95%

    def _simulate_session_completion(self, journey: CustomerJourney) -> Dict:
        """Simular finalización de sesión"""
        conversion_probability = self._calculate_conversion_probability(journey)
        
        # Determinar resultado de la sesión
        if random.random() < conversion_probability:
            # Conversión exitosa
            result = {
                'outcome': 'conversion',
                'transaction_id': f"txn_{journey.customer_id}_{int(time.time())}",
                'total_amount': journey.total_value,
                'payment_method': random.choice(['Credit Card', 'PayPal', 'Wire Transfer']),
                'status': 'completed'
            }
            self.metrics['conversions'] += 1
            self.metrics['revenue'] += journey.total_value
            
        elif journey.cart_items and random.random() < 0.3:
            # Abandono de carrito
            result = {
                'outcome': 'cart_abandonment',
                'abandoned_value': journey.total_value,
                'cart_items_count': len(journey.cart_items)
            }
            self.metrics['cart_abandonments'] += 1
            
        else:
            # Bounce (salida sin acción significativa)
            result = {
                'outcome': 'bounce',
                'pages_visited': random.randint(1, 3),
                'session_duration': random.randint(10, 60)
            }
            self.metrics['bounce_rate'] += 1
        
        result.update({
            'customer_id': journey.customer_id,
            'session_id': journey.session_id,
            'session_duration': (datetime.now() - journey.start_time).total_seconds(),
            'timestamp': datetime.now()
        })
        
        return result

    def _insert_session_data(self, session_data: Dict):
        """Insertar datos de sesión en DWH"""
        try:
            # Crear tabla si no existe
            create_table_query = """
                CREATE TABLE IF NOT EXISTS customer_sessions (
                    session_id VARCHAR(100) PRIMARY KEY,
                    customer_id BIGINT,
                    session_data JSONB,
                    outcome VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            self.cursors["dwh"].execute(create_table_query)
            
            # Preparar datos para JSON (convertir datetime a string)
            json_data = session_data.copy()
            if 'timestamp' in json_data:
                json_data['timestamp'] = json_data['timestamp'].isoformat()
            if 'start_time' in json_data:
                json_data['start_time'] = json_data['start_time'].isoformat()
            
            # Insertar sesión
            insert_query = """
                INSERT INTO customer_sessions (session_id, customer_id, session_data, outcome, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                session_data = EXCLUDED.session_data,
                outcome = EXCLUDED.outcome,
                timestamp = EXCLUDED.timestamp
            """
            
            self.cursors["dwh"].execute(insert_query, (
                session_data['session_id'],
                session_data['customer_id'],
                json.dumps(json_data),
                session_data['outcome'],
                session_data['timestamp']
            ))
            
            self.conns["dwh"].commit()
            
        except Exception as e:
            logger.error(f"❌ Error insertando sesión: {e}")
            self.conns["dwh"].rollback()

    def _update_market_trends(self):
        """Actualizar tendencias del mercado dinámicamente"""
        for category, trend in self.market_trends.items():
            # Simular cambios en demanda
            trend.demand_multiplier += random.uniform(-0.05, 0.05)
            trend.demand_multiplier = max(0.5, min(2.0, trend.demand_multiplier))
            
            # Simular cambios en precios
            trend.price_trend += random.uniform(-0.02, 0.02)
            trend.price_trend = max(-0.2, min(0.2, trend.price_trend))
            
            # Simular actividad de competencia
            trend.competitor_activity += random.uniform(-0.1, 0.1)
            trend.competitor_activity = max(0.3, min(2.0, trend.competitor_activity))

    def start_advanced_simulation(self, duration_minutes=60):
        """Iniciar simulación avanzada"""
        logger.info(f"🧠 Iniciando simulación avanzada por {duration_minutes} minutos")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time and self.running:
            try:
                # Calcular nivel de actividad actual
                activity_level = self._get_current_activity_level()
                
                # Generar nueva sesión o continuar existente
                if random.random() < 0.3 or not self.active_sessions:
                    # Nueva sesión
                    customer_id = random.randint(1, 100)
                    journey = self._simulate_customer_journey(customer_id)
                    self.active_sessions[customer_id] = journey
                    self.metrics['total_sessions'] += 1
                
                # Procesar sesiones activas
                for customer_id, journey in list(self.active_sessions.items()):
                    # Simular interacción
                    interaction = self._simulate_page_interaction(journey)
                    
                    # Actualizar journey
                    journey.current_page = f"page_{random.randint(1, 10)}"
                    journey.behavior_score += random.uniform(0.1, 0.3)
                    
                    # Determinar si la sesión termina
                    if random.random() < 0.2 or journey.behavior_score > 5.0:
                        # Finalizar sesión
                        session_result = self._simulate_session_completion(journey)
                        self._insert_session_data(session_result)
                        del self.active_sessions[customer_id]
                
                # Actualizar tendencias del mercado cada 5 minutos
                if int(time.time() - start_time) % 300 == 0:
                    self._update_market_trends()
                    logger.info("📈 Tendencias del mercado actualizadas")
                
                # Log de métricas cada 50 sesiones
                if self.metrics['total_sessions'] % 50 == 0:
                    self._log_metrics()
                
                # Intervalo dinámico
                interval = random.uniform(5, 15) / activity_level
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Simulación detenida por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en simulación: {e}")
                time.sleep(5)
        
        # Finalizar sesiones activas
        for customer_id, journey in self.active_sessions.items():
            session_result = self._simulate_session_completion(journey)
            self._insert_session_data(session_result)
        
        logger.info("✅ Simulación avanzada completada")
        self._log_final_metrics()
        self._cleanup()

    def _get_current_activity_level(self) -> float:
        """Calcular nivel de actividad actual"""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Factor por hora
        if hour in self.behavior_patterns['time_patterns']['rush_hours']:
            hourly_factor = 1.5
        elif hour in self.behavior_patterns['time_patterns']['quiet_hours']:
            hourly_factor = 0.3
        else:
            hourly_factor = 1.0
        
        # Factor por día de la semana
        if day_of_week >= 5:  # Fin de semana
            weekly_factor = self.behavior_patterns['time_patterns']['weekend_multiplier']
        else:
            weekly_factor = 1.0
        
        # Factor estacional
        month = now.month
        seasonal_factor = 1.0
        for season, data in self.behavior_patterns['seasonal_patterns'].items():
            if month in data['months']:
                seasonal_factor = data['multiplier']
                break
        
        return hourly_factor * weekly_factor * seasonal_factor

    def _log_metrics(self):
        """Log de métricas actuales"""
        conversion_rate = (self.metrics['conversions'] / max(self.metrics['total_sessions'], 1)) * 100
        avg_revenue = self.metrics['revenue'] / max(self.metrics['conversions'], 1)
        
        logger.info(f"📊 Métricas: {self.metrics['total_sessions']} sesiones, "
                   f"{conversion_rate:.1f}% conversión, "
                   f"${avg_revenue:.2f} ingreso promedio")

    def _log_final_metrics(self):
        """Log de métricas finales"""
        logger.info("📈 MÉTRICAS FINALES:")
        logger.info(f"   Total de sesiones: {self.metrics['total_sessions']}")
        logger.info(f"   Conversiones: {self.metrics['conversions']}")
        logger.info(f"   Abandonos de carrito: {self.metrics['cart_abandonments']}")
        logger.info(f"   Rebotes: {self.metrics['bounce_rate']}")
        logger.info(f"   Ingresos totales: ${self.metrics['revenue']:.2f}")
        
        if self.metrics['total_sessions'] > 0:
            conversion_rate = (self.metrics['conversions'] / self.metrics['total_sessions']) * 100
            logger.info(f"   Tasa de conversión: {conversion_rate:.2f}%")

    def _cleanup(self):
        """Limpiar conexiones"""
        for cursor in self.cursors.values():
            cursor.close()
        for conn in self.conns.values():
            conn.close()
        logger.info("🧹 Conexiones cerradas")

    def stop(self):
        """Detener simulación"""
        self.running = False
        logger.info("⏹️ Solicitando detener simulación...")

def main():
    """Función principal"""
    print("🧠 InstaShop Advanced Behavior Simulator")
    print("=" * 50)
    
    simulator = AdvancedBehaviorSimulator()
    
    try:
        duration = int(input("¿Cuántos minutos simular comportamiento? (default: 60): ") or "60")
        simulator.start_advanced_simulation(duration)
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo simulación...")
        simulator.stop()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
