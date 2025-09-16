#!/usr/bin/env python3
"""
📊 InstaShop Real-time Monitor
Monitor en tiempo real de métricas y estadísticas del sistema
"""

import psycopg2
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimeMonitor:
    def __init__(self):
        self.conns = self._setup_connections()
        self.cursors = {k: v.cursor() for k, v in self.conns.items()}
        
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

    def get_realtime_metrics(self):
        """Obtener métricas en tiempo real"""
        metrics = {}
        
        try:
            # Métricas de transacciones (última hora)
            transaction_query = """
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_transactions,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_transactions
                FROM transaction 
                WHERE transaction_date >= NOW() - INTERVAL '1 hour'
            """
            
            self.cursors["instashop"].execute(transaction_query)
            transaction_data = self.cursors["instashop"].fetchone()
            
            metrics['transactions'] = {
                'total': transaction_data[0] or 0,
                'revenue': float(transaction_data[1] or 0),
                'avg_order_value': float(transaction_data[2] or 0),
                'completed': transaction_data[3] or 0,
                'failed': transaction_data[4] or 0
            }
            
            # Métricas de eventos en tiempo real (últimos 30 minutos)
            events_query = """
                SELECT 
                    event_type,
                    COUNT(*) as count,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM realtime_events 
                WHERE timestamp >= NOW() - INTERVAL '30 minutes'
                GROUP BY event_type
            """
            
            self.cursors["dwh"].execute(events_query)
            events_data = self.cursors["dwh"].fetchall()
            
            metrics['events'] = {}
            total_events = 0
            total_customers = set()
            
            for event_type, count, unique_customers in events_data:
                metrics['events'][event_type] = {
                    'count': count,
                    'unique_customers': unique_customers
                }
                total_events += count
                total_customers.add(unique_customers)
            
            metrics['events']['total'] = total_events
            metrics['events']['unique_customers'] = len(total_customers)
            
            # Métricas de sesiones (última hora)
            sessions_query = """
                SELECT 
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN outcome = 'conversion' THEN 1 END) as conversions,
                    COUNT(CASE WHEN outcome = 'cart_abandonment' THEN 1 END) as cart_abandonments,
                    COUNT(CASE WHEN outcome = 'bounce' THEN 1 END) as bounces,
                    AVG(EXTRACT(EPOCH FROM (timestamp - (session_data->>'start_time')::timestamp))) as avg_session_duration
                FROM customer_sessions 
                WHERE timestamp >= NOW() - INTERVAL '1 hour'
            """
            
            self.cursors["dwh"].execute(sessions_query)
            sessions_data = self.cursors["dwh"].fetchone()
            
            metrics['sessions'] = {
                'total': sessions_data[0] or 0,
                'conversions': sessions_data[1] or 0,
                'cart_abandonments': sessions_data[2] or 0,
                'bounces': sessions_data[3] or 0,
                'avg_duration': float(sessions_data[4] or 0)
            }
            
            # Calcular tasas
            if metrics['sessions']['total'] > 0:
                metrics['sessions']['conversion_rate'] = (metrics['sessions']['conversions'] / metrics['sessions']['total']) * 100
                metrics['sessions']['abandonment_rate'] = (metrics['sessions']['cart_abandonments'] / metrics['sessions']['total']) * 100
                metrics['sessions']['bounce_rate'] = (metrics['sessions']['bounces'] / metrics['sessions']['total']) * 100
            else:
                metrics['sessions']['conversion_rate'] = 0
                metrics['sessions']['abandonment_rate'] = 0
                metrics['sessions']['bounce_rate'] = 0
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            metrics = self._get_default_metrics()
        
        return metrics

    def _get_default_metrics(self):
        """Obtener métricas por defecto en caso de error"""
        return {
            'transactions': {'total': 0, 'revenue': 0, 'avg_order_value': 0, 'completed': 0, 'failed': 0},
            'events': {'total': 0, 'unique_customers': 0},
            'sessions': {'total': 0, 'conversions': 0, 'cart_abandonments': 0, 'bounces': 0, 'avg_duration': 0, 'conversion_rate': 0, 'abandonment_rate': 0, 'bounce_rate': 0}
        }

    def get_trending_products(self, limit=10):
        """Obtener productos trending"""
        try:
            query = """
                SELECT 
                    p.name,
                    p.category,
                    COUNT(td.transaction_id) as purchase_count,
                    SUM(td.quantity) as total_quantity,
                    AVG(td.unit_price) as avg_price
                FROM product p
                JOIN transactiondetail td ON p.product_id = td.product_id
                JOIN transaction t ON td.transaction_id = t.transaction_id
                WHERE t.transaction_date >= NOW() - INTERVAL '24 hours'
                GROUP BY p.product_id, p.name, p.category
                ORDER BY purchase_count DESC
                LIMIT %s
            """
            
            self.cursors["instashop"].execute(query, (limit,))
            return self.cursors["instashop"].fetchall()
            
        except Exception as e:
            logger.error(f"Error obteniendo productos trending: {e}")
            return []

    def get_customer_activity(self, hours=24):
        """Obtener actividad de clientes por hora"""
        try:
            query = """
                SELECT 
                    DATE_TRUNC('hour', transaction_date) as hour,
                    COUNT(*) as transactions,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    SUM(total_amount) as revenue
                FROM transaction
                WHERE transaction_date >= NOW() - INTERVAL '%s hours'
                GROUP BY DATE_TRUNC('hour', transaction_date)
                ORDER BY hour
            """
            
            self.cursors["instashop"].execute(query, (hours,))
            return self.cursors["instashop"].fetchall()
            
        except Exception as e:
            logger.error(f"Error obteniendo actividad de clientes: {e}")
            return []

    def get_category_performance(self):
        """Obtener rendimiento por categoría"""
        try:
            query = """
                SELECT 
                    p.category,
                    COUNT(td.transaction_id) as transactions,
                    SUM(td.quantity) as units_sold,
                    SUM(td.quantity * td.unit_price) as revenue,
                    AVG(td.unit_price) as avg_price
                FROM product p
                JOIN transactiondetail td ON p.product_id = td.product_id
                JOIN transaction t ON td.transaction_id = t.transaction_id
                WHERE t.transaction_date >= NOW() - INTERVAL '24 hours'
                GROUP BY p.category
                ORDER BY revenue DESC
            """
            
            self.cursors["instashop"].execute(query)
            return self.cursors["instashop"].fetchall()
            
        except Exception as e:
            logger.error(f"Error obteniendo rendimiento por categoría: {e}")
            return []

    def get_realtime_events_stream(self, limit=50):
        """Obtener stream de eventos en tiempo real"""
        try:
            query = """
                SELECT 
                    customer_id,
                    event_type,
                    event_data,
                    timestamp
                FROM realtime_events
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            self.cursors["dwh"].execute(query, (limit,))
            return self.cursors["dwh"].fetchall()
            
        except Exception as e:
            logger.error(f"Error obteniendo stream de eventos: {e}")
            return []

    def cleanup(self):
        """Limpiar conexiones"""
        for cursor in self.cursors.values():
            cursor.close()
        for conn in self.conns.values():
            conn.close()

def create_dashboard():
    """Crear dashboard de Streamlit"""
    st.set_page_config(
        page_title="InstaShop Real-time Monitor",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 InstaShop Real-time Monitor")
    st.markdown("---")
    
    # Inicializar monitor
    monitor = RealTimeMonitor()
    
    # Sidebar con controles
    st.sidebar.title("🎛️ Controles")
    refresh_interval = st.sidebar.slider("Intervalo de actualización (segundos)", 5, 60, 30)
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = monitor.get_realtime_metrics()
    
    with col1:
        st.metric(
            label="🛒 Transacciones (1h)",
            value=metrics['transactions']['total'],
            delta=f"${metrics['transactions']['revenue']:,.2f}"
        )
    
    with col2:
        st.metric(
            label="💰 Ingresos (1h)",
            value=f"${metrics['transactions']['revenue']:,.2f}",
            delta=f"AOV: ${metrics['transactions']['avg_order_value']:,.2f}"
        )
    
    with col3:
        st.metric(
            label="👥 Sesiones (1h)",
            value=metrics['sessions']['total'],
            delta=f"{metrics['sessions']['conversion_rate']:.1f}% conversión"
        )
    
    with col4:
        st.metric(
            label="📈 Eventos (30min)",
            value=metrics['events']['total'],
            delta=f"{metrics['events']['unique_customers']} usuarios únicos"
        )
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Actividad por Categoría")
        category_data = monitor.get_category_performance()
        
        if category_data:
            df_categories = pd.DataFrame(category_data, columns=[
                'Categoría', 'Transacciones', 'Unidades', 'Ingresos', 'Precio Promedio'
            ])
            
            fig = px.pie(
                df_categories, 
                values='Ingresos', 
                names='Categoría',
                title="Distribución de Ingresos por Categoría"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de categorías disponibles")
    
    with col2:
        st.subheader("🔥 Productos Trending")
        trending_products = monitor.get_trending_products()
        
        if trending_products:
            df_trending = pd.DataFrame(trending_products, columns=[
                'Producto', 'Categoría', 'Compras', 'Cantidad', 'Precio Promedio'
            ])
            
            fig = px.bar(
                df_trending.head(10), 
                x='Compras', 
                y='Producto',
                orientation='h',
                title="Top 10 Productos Más Vendidos (24h)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de productos trending disponibles")
    
    # Actividad temporal
    st.subheader("⏰ Actividad Temporal")
    activity_data = monitor.get_customer_activity(24)
    
    if activity_data:
        df_activity = pd.DataFrame(activity_data, columns=[
            'Hora', 'Transacciones', 'Usuarios Únicos', 'Ingresos'
        ])
        df_activity['Hora'] = pd.to_datetime(df_activity['Hora'])
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Transacciones por Hora', 'Ingresos por Hora'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(x=df_activity['Hora'], y=df_activity['Transacciones'], 
                      mode='lines+markers', name='Transacciones'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df_activity['Hora'], y=df_activity['Ingresos'], 
                      mode='lines+markers', name='Ingresos', line=dict(color='green')),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de actividad temporal disponibles")
    
    # Stream de eventos en tiempo real
    st.subheader("🔄 Stream de Eventos en Tiempo Real")
    
    events_stream = monitor.get_realtime_events_stream(20)
    
    if events_stream:
        for event in events_stream:
            customer_id, event_type, event_data, timestamp = event
            
            # Parsear datos del evento
            try:
                data = json.loads(event_data) if isinstance(event_data, str) else event_data
            except:
                data = {}
            
            # Crear tarjeta de evento
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.write(f"👤 Cliente {customer_id}")
                
                with col2:
                    st.write(f"📝 {event_type}")
                    if 'product_name' in data:
                        st.write(f"🛍️ {data['product_name']}")
                    if 'search_term' in data:
                        st.write(f"🔍 Buscó: {data['search_term']}")
                
                with col3:
                    st.write(f"⏰ {timestamp.strftime('%H:%M:%S')}")
                
                st.markdown("---")
    else:
        st.info("No hay eventos en tiempo real disponibles")
    
    # Métricas de sesiones
    st.subheader("📈 Métricas de Sesiones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Tasa de Conversión",
            value=f"{metrics['sessions']['conversion_rate']:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Tasa de Abandono",
            value=f"{metrics['sessions']['abandonment_rate']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Tasa de Rebote",
            value=f"{metrics['sessions']['bounce_rate']:.1f}%"
        )
    
    # Footer
    st.markdown("---")
    st.markdown(f"🕐 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Limpiar conexiones
    monitor.cleanup()

def main():
    """Función principal para ejecutar el monitor"""
    print("📊 InstaShop Real-time Monitor")
    print("=" * 50)
    print("Iniciando dashboard en http://localhost:8503")
    print("Presiona Ctrl+C para detener")
    
    try:
        # Ejecutar dashboard
        import subprocess
        import sys
        
        # Crear archivo temporal para el dashboard
        dashboard_code = """
import streamlit as st
from realtime_monitor import create_dashboard

if __name__ == "__main__":
    create_dashboard()
"""
        
        with open("nico-scripts/temp_dashboard.py", "w") as f:
            f.write(dashboard_code)
        
        # Ejecutar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "nico-scripts/temp_dashboard.py", 
            "--server.port", "8503"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitor detenido")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
