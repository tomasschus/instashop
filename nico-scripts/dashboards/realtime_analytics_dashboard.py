#!/usr/bin/env python3
"""
📊 InstaShop Real-time Analytics Dashboard
Dashboard interactivo con datos del warehouse y eventos en tiempo real
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la página
st.set_page_config(
    page_title="InstaShop Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class InstaShopAnalyticsDashboard:
    def __init__(self):
        self.dwh_conn = None
        self.instashop_conn = None
        self.crm_conn = None
        self.connect_databases()
    
    def connect_databases(self):
        """Conectar a las bases de datos"""
        try:
            # Conectar a DWH
            self.dwh_conn = psycopg2.connect(
                host='localhost',
                port=5436,
                dbname='dwh_db',
                user='dwh',
                password='dwh123'
            )
            
            # Conectar a InstaShop
            self.instashop_conn = psycopg2.connect(
                host='localhost',
                port=5432,
                dbname='instashop',
                user='insta',
                password='insta123'
            )
            
            # Conectar a CRM
            self.crm_conn = psycopg2.connect(
                host='localhost',
                port=5433,
                dbname='crm_db',
                user='crm',
                password='crm123'
            )
            
            logger.info("✅ Conectado a todas las bases de datos")
        except Exception as e:
            logger.error(f"❌ Error conectando a bases de datos: {e}")
            st.error("Error conectando a las bases de datos")
    
    def get_realtime_events(self, hours=1):
        """Obtener eventos en tiempo real del DWH"""
        try:
            cursor = self.dwh_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT event_type, timestamp, customer_id, customer_name, 
                       product_name, category, amount, session_id, processed_at
                FROM realtime_events 
                WHERE processed_at >= NOW() - INTERVAL '%s hours'
                ORDER BY processed_at DESC
            """
            cursor.execute(query, (hours,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            logger.error(f"❌ Error obteniendo eventos: {e}")
            return pd.DataFrame()
    
    def get_transaction_summary(self, hours=24):
        """Obtener resumen de transacciones"""
        try:
            cursor = self.dwh_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_revenue,
                    AVG(amount) as avg_order_value,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM realtime_events 
                WHERE event_type = 'transaction' 
                AND timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY DATE_TRUNC('hour', timestamp)
                ORDER BY hour
            """
            cursor.execute(query, (hours,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen de transacciones: {e}")
            return pd.DataFrame()
    
    def get_behavior_analysis(self, hours=24):
        """Obtener análisis de comportamiento"""
        try:
            cursor = self.dwh_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    interaction_type,
                    channel,
                    COUNT(*) as interaction_count,
                    COUNT(DISTINCT customer_id) as unique_users,
                    COUNT(DISTINCT session_id) as unique_sessions
                FROM realtime_events 
                WHERE event_type = 'user_behavior' 
                AND timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY interaction_type, channel
                ORDER BY interaction_count DESC
            """
            cursor.execute(query, (hours,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            logger.error(f"❌ Error obteniendo análisis de comportamiento: {e}")
            return pd.DataFrame()
    
    def get_top_customers(self, limit=10):
        """Obtener top clientes por transacciones"""
        try:
            cursor = self.dwh_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    customer_id,
                    customer_name,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_spent,
                    AVG(amount) as avg_order_value
                FROM realtime_events 
                WHERE event_type = 'transaction'
                AND timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY customer_id, customer_name
                ORDER BY total_spent DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            logger.error(f"❌ Error obteniendo top clientes: {e}")
            return pd.DataFrame()
    
    def get_category_analysis(self, hours=24):
        """Obtener análisis por categoría"""
        try:
            cursor = self.dwh_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    category,
                    COUNT(*) as event_count,
                    SUM(amount) as total_revenue,
                    AVG(amount) as avg_amount,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM realtime_events 
                WHERE category IS NOT NULL
                AND timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY category
                ORDER BY total_revenue DESC
            """
            cursor.execute(query, (hours,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            logger.error(f"❌ Error obteniendo análisis por categoría: {e}")
            return pd.DataFrame()
    
    def get_search_analytics(self, hours=24):
        """Obtener análisis de búsquedas"""
        try:
            cursor = self.dwh_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    raw_data->>'search_query' as search_query,
                    COUNT(*) as search_count,
                    COUNT(DISTINCT customer_id) as unique_searchers
                FROM realtime_events 
                WHERE event_type = 'search'
                AND timestamp >= NOW() - INTERVAL '%s hours'
                AND raw_data->>'search_query' IS NOT NULL
                GROUP BY raw_data->>'search_query'
                ORDER BY search_count DESC
                LIMIT 20
            """
            cursor.execute(query, (hours,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            logger.error(f"❌ Error obteniendo análisis de búsquedas: {e}")
            return pd.DataFrame()
    
    def get_cart_abandonment_analysis(self, hours=24):
        """Obtener análisis de abandono de carrito"""
        try:
            cursor = self.dwh_conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    COUNT(*) as abandoned_carts,
                    SUM(amount) as lost_revenue,
                    AVG(amount) as avg_cart_value
                FROM realtime_events 
                WHERE event_type = 'cart_abandonment'
                AND timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY DATE_TRUNC('hour', timestamp)
                ORDER BY hour
            """
            cursor.execute(query, (hours,))
            return pd.DataFrame(cursor.fetchall())
        except Exception as e:
            logger.error(f"❌ Error obteniendo análisis de abandono: {e}")
            return pd.DataFrame()
    
    def create_revenue_chart(self, df):
        """Crear gráfico de ingresos en tiempo real"""
        if df.empty:
            return go.Figure()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['hour'],
            y=df['total_revenue'],
            mode='lines+markers',
            name='Ingresos por Hora',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="💰 Ingresos en Tiempo Real",
            xaxis_title="Hora",
            yaxis_title="Ingresos ($)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_transaction_volume_chart(self, df):
        """Crear gráfico de volumen de transacciones"""
        if df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Transacciones por Hora', 'Clientes Únicos por Hora'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Bar(x=df['hour'], y=df['transaction_count'], 
                   name='Transacciones', marker_color='#4169E1'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=df['hour'], y=df['unique_customers'], 
                   name='Clientes Únicos', marker_color='#FF6347'),
            row=2, col=1
        )
        
        fig.update_layout(
            title="📈 Volumen de Transacciones",
            height=600,
            template='plotly_white'
        )
        
        return fig
    
    def create_behavior_heatmap(self, df):
        """Crear heatmap de comportamiento"""
        if df.empty:
            return go.Figure()
        
        pivot_df = df.pivot_table(
            values='interaction_count', 
            index='interaction_type', 
            columns='channel', 
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale='Blues',
            title="🔥 Heatmap de Comportamiento de Usuarios"
        )
        
        fig.update_layout(
            xaxis_title="Canal",
            yaxis_title="Tipo de Interacción",
            template='plotly_white'
        )
        
        return fig
    
    def create_category_revenue_chart(self, df):
        """Crear gráfico de ingresos por categoría"""
        if df.empty:
            return go.Figure()
        
        fig = px.pie(
            df, 
            values='total_revenue', 
            names='category',
            title="🛍️ Distribución de Ingresos por Categoría",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def create_search_trends_chart(self, df):
        """Crear gráfico de tendencias de búsqueda"""
        if df.empty:
            return go.Figure()
        
        fig = px.bar(
            df.head(10),
            x='search_count',
            y='search_query',
            orientation='h',
            title="🔍 Top 10 Términos de Búsqueda",
            color='search_count',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title="Número de Búsquedas",
            yaxis_title="Término de Búsqueda",
            template='plotly_white'
        )
        
        return fig
    
    def create_cart_abandonment_chart(self, df):
        """Crear gráfico de abandono de carrito"""
        if df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Carritos Abandonados por Hora', 'Ingresos Perdidos por Hora'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Bar(x=df['hour'], y=df['abandoned_carts'], 
                   name='Carritos Abandonados', marker_color='#DC143C'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=df['hour'], y=df['lost_revenue'], 
                   name='Ingresos Perdidos', marker_color='#FF4500'),
            row=2, col=1
        )
        
        fig.update_layout(
            title="🛒 Análisis de Abandono de Carrito",
            height=600,
            template='plotly_white'
        )
        
        return fig
    
    def run_dashboard(self):
        """Ejecutar dashboard principal"""
        st.title("📊 InstaShop Real-time Analytics Dashboard")
        st.markdown("---")
        
        # Sidebar para controles
        st.sidebar.title("🎛️ Controles")
        
        # Selector de tiempo
        time_range = st.sidebar.selectbox(
            "Período de Análisis",
            ["Última hora", "Últimas 6 horas", "Últimas 24 horas", "Última semana"]
        )
        
        time_mapping = {
            "Última hora": 1,
            "Últimas 6 horas": 6,
            "Últimas 24 horas": 24,
            "Última semana": 168
        }
        
        hours = time_mapping[time_range]
        
        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30 segundos)", value=True)
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()
        
        # Métricas principales
        st.subheader("📈 Métricas Principales")
        
        # Obtener datos
        events_df = self.get_realtime_events(hours)
        transaction_summary = self.get_transaction_summary(hours)
        
        if not events_df.empty:
            # Calcular métricas
            total_events = len(events_df)
            total_transactions = len(events_df[events_df['event_type'] == 'transaction'])
            total_revenue = events_df[events_df['event_type'] == 'transaction']['amount'].sum()
            unique_customers = events_df['customer_id'].nunique()
            
            # Mostrar métricas en columnas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Eventos", f"{total_events:,}")
            
            with col2:
                st.metric("💳 Transacciones", f"{total_transactions:,}")
            
            with col3:
                st.metric("💰 Ingresos Totales", f"${total_revenue:,.2f}")
            
            with col4:
                st.metric("👥 Clientes Únicos", f"{unique_customers:,}")
        
        st.markdown("---")
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Ingresos en Tiempo Real")
            if not transaction_summary.empty:
                revenue_chart = self.create_revenue_chart(transaction_summary)
                st.plotly_chart(revenue_chart, use_container_width=True)
            else:
                st.info("No hay datos de transacciones disponibles")
        
        with col2:
            st.subheader("📈 Volumen de Transacciones")
            if not transaction_summary.empty:
                volume_chart = self.create_transaction_volume_chart(transaction_summary)
                st.plotly_chart(volume_chart, use_container_width=True)
            else:
                st.info("No hay datos de transacciones disponibles")
        
        # Análisis de comportamiento
        st.subheader("👥 Análisis de Comportamiento")
        behavior_df = self.get_behavior_analysis(hours)
        
        if not behavior_df.empty:
            behavior_chart = self.create_behavior_heatmap(behavior_df)
            st.plotly_chart(behavior_chart, use_container_width=True)
        else:
            st.info("No hay datos de comportamiento disponibles")
        
        # Análisis por categoría
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🛍️ Ingresos por Categoría")
            category_df = self.get_category_analysis(hours)
            if not category_df.empty:
                category_chart = self.create_category_revenue_chart(category_df)
                st.plotly_chart(category_chart, use_container_width=True)
            else:
                st.info("No hay datos de categorías disponibles")
        
        with col2:
            st.subheader("🔍 Tendencias de Búsqueda")
            search_df = self.get_search_analytics(hours)
            if not search_df.empty:
                search_chart = self.create_search_trends_chart(search_df)
                st.plotly_chart(search_chart, use_container_width=True)
            else:
                st.info("No hay datos de búsquedas disponibles")
        
        # Análisis de abandono de carrito
        st.subheader("🛒 Análisis de Abandono de Carrito")
        cart_df = self.get_cart_abandonment_analysis(hours)
        if not cart_df.empty:
            cart_chart = self.create_cart_abandonment_chart(cart_df)
            st.plotly_chart(cart_chart, use_container_width=True)
        else:
            st.info("No hay datos de abandono de carrito disponibles")
        
        # Top clientes
        st.subheader("🏆 Top Clientes")
        top_customers_df = self.get_top_customers(10)
        if not top_customers_df.empty:
            st.dataframe(
                top_customers_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos de clientes disponibles")
        
        # Eventos recientes
        st.subheader("📋 Eventos Recientes")
        if not events_df.empty:
            recent_events = events_df.head(20)
            st.dataframe(
                recent_events,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay eventos recientes disponibles")

def main():
    dashboard = InstaShopAnalyticsDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
