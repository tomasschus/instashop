#!/usr/bin/env python3
"""
📊 Dashboard Streamlit + Spark + Redis - Métricas en Tiempo Real
Lee métricas de Redis generadas por Spark Streaming
"""

import streamlit as st
import redis
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import time
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurar página
st.set_page_config(
    layout="wide", 
    page_title="InstaShop Real-time Spark Metrics",
    page_icon="⚡"
)

# Conectar a Redis
@st.cache_resource
def get_redis_connection():
    try:
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        # Test connection
        client.ping()
        return client
    except Exception as e:
        st.error(f"❌ Error conectando a Redis: {e}")
        return None

# Conectar al Data Warehouse
@st.cache_resource
def get_dwh_connection():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5436,
            database='dwh_db',
            user='dwh',
            password='dwh123'
        )
        return conn
    except Exception as e:
        st.error(f"❌ Error conectando al DWH: {e}")
        return None

def get_transaction_metrics(redis_client):
    """Obtener métricas de transacciones de Redis (CDC Spark)"""
    try:
        # Intentar primero las métricas CDC Spark
        cdc_data = redis_client.get("cdc_spark_metrics:transactions")
        if cdc_data:
            return json.loads(cdc_data)
        
        # Fallback a métricas legacy
        legacy_data = redis_client.get("metrics:transactions")
        if legacy_data:
            return json.loads(legacy_data)
        
        st.warning("⚠️ No hay datos de transacciones en Redis")
        return None
    except Exception as e:
        st.error(f"❌ Error obteniendo métricas de transacciones: {e}")
        return None

def get_behavior_metrics(redis_client):
    """Obtener métricas de comportamiento de Redis"""
    try:
        # Buscar todos los keys de comportamiento
        behavior_keys = redis_client.keys("metrics:behavior:*")
        metrics = {}
        
        for key in behavior_keys:
            event_type = key.replace("metrics:behavior:", "")
            data = redis_client.get(key)
            if data:
                metrics[event_type] = json.loads(data)
        
        return metrics
    except Exception as e:
        st.error(f"❌ Error obteniendo métricas de comportamiento: {e}")
        return {}

def get_product_metrics(redis_client):
    """Obtener métricas de productos de Redis (CDC Spark)"""
    try:
        # Intentar primero las métricas CDC Spark
        cdc_data = redis_client.get("cdc_spark_metrics:products")
        if cdc_data:
            return {"cdc_products": json.loads(cdc_data)}
        
        # Fallback a métricas legacy
        product_keys = redis_client.keys("metrics:products:*")
        metrics = {}
        
        for key in product_keys:
            category = key.replace("metrics:products:", "")
            data = redis_client.get(key)
            if data:
                metrics[category] = json.loads(data)
        
        return metrics
    except Exception as e:
        st.error(f"❌ Error obteniendo métricas de productos: {e}")
        return {}

def get_dwh_historical_data(dwh_conn, hours=24):
    """Obtener datos históricos del DWH"""
    try:
        cursor = dwh_conn.cursor(cursor_factory=RealDictCursor)
        
        # Consulta para obtener datos históricos de las últimas N horas
        query = """
        SELECT 
            DATE_TRUNC('hour', timestamp) as hour,
            COUNT(*) as total_events,
            COUNT(CASE WHEN event_type = 'transaction' THEN 1 END) as transactions,
            COUNT(CASE WHEN event_type = 'user_behavior' THEN 1 END) as behavior_events,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM realtime_events 
        WHERE timestamp >= NOW() - INTERVAL '%s hours'
        GROUP BY DATE_TRUNC('hour', timestamp)
        ORDER BY hour DESC
        LIMIT 24
        """
        
        cursor.execute(query, (hours,))
        results = cursor.fetchall()
        cursor.close()
        
        return results
    except Exception as e:
        st.error(f"❌ Error obteniendo datos históricos del DWH: {e}")
        return []

def get_dwh_summary_stats(dwh_conn):
    """Obtener estadísticas resumen del DWH"""
    try:
        cursor = dwh_conn.cursor(cursor_factory=RealDictCursor)
        
        # Estadísticas generales
        query = """
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN event_type = 'transaction' THEN 1 END) as total_transactions,
            COUNT(CASE WHEN event_type = 'user_behavior' THEN 1 END) as total_behavior,
            COUNT(DISTINCT customer_id) as total_customers,
            COUNT(DISTINCT DATE(timestamp)) as active_days,
            MIN(timestamp) as first_event,
            MAX(timestamp) as last_event
        FROM realtime_events
        """
        
        cursor.execute(query)
        stats = cursor.fetchone()
        cursor.close()
        
        return stats
    except Exception as e:
        st.error(f"❌ Error obteniendo estadísticas del DWH: {e}")
        return None

def create_revenue_chart(metrics):
    """Crear gráfico de ingresos"""
    if not metrics:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = metrics.get('total_revenue', 0),
        title = {"text": "Ingresos Totales (USD)"},
        delta = {"reference": metrics.get('total_revenue', 0) * 0.9},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        title="💰 Ingresos en Tiempo Real",
        height=200
    )
    
    return fig

def create_transaction_chart(metrics):
    """Crear gráfico de transacciones"""
    if not metrics:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = metrics.get('total_transactions', 0),
        title = {"text": "Transacciones"},
        delta = {"reference": metrics.get('total_transactions', 0) * 0.8},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        title="🛒 Transacciones en Tiempo Real",
        height=200
    )
    
    return fig

def create_customers_chart(metrics):
    """Crear gráfico de clientes únicos"""
    if not metrics:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = metrics.get('unique_customers', 0),
        title = {"text": "Clientes Únicos"},
        delta = {"reference": metrics.get('unique_customers', 0) * 0.7},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        title="👥 Clientes Únicos en Tiempo Real",
        height=200
    )
    
    return fig

def create_behavior_chart(behavior_metrics):
    """Crear gráfico de comportamiento"""
    if not behavior_metrics:
        return go.Figure()
    
    event_types = []
    event_counts = []
    
    for event_type, data in behavior_metrics.items():
        event_types.append(event_type.replace('_', ' ').title())
        event_counts.append(data.get('event_count', 0))
    
    fig = go.Figure(data=[
        go.Bar(x=event_types, y=event_counts, marker_color='lightblue')
    ])
    
    fig.update_layout(
        title="📊 Eventos de Comportamiento en Tiempo Real",
        xaxis_title="Tipo de Evento",
        yaxis_title="Cantidad",
        height=400
    )
    
    return fig

def create_product_chart(product_metrics):
    """Crear gráfico de productos por categoría"""
    if not product_metrics:
        return go.Figure()
    
    categories = []
    revenues = []
    sales = []
    
    # Manejar datos CDC (formato lista) vs legacy (formato dict)
    if "cdc_products" in product_metrics:
        # Datos CDC: agregar por categoría
        cdc_data = product_metrics["cdc_products"]
        if cdc_data:
            # Agrupar por categoría desde la lista CDC
            category_totals = {}
            for item in cdc_data:
                cat = item.get('category', 'unknown')
                if cat not in category_totals:
                    category_totals[cat] = {'revenue': 0, 'sales': 0}
                category_totals[cat]['revenue'] += item.get('category_revenue', 0)
                category_totals[cat]['sales'] += item.get('product_sales', 0)
            
            # Convertir a listas para el gráfico
            for cat, totals in category_totals.items():
                categories.append(cat.title())
                revenues.append(totals['revenue'])
                sales.append(totals['sales'])
    else:
        # Datos legacy: usar keys separadas metrics:products:*
        for category, data in product_metrics.items():
            categories.append(category.title())
            revenues.append(data.get('category_revenue', 0))
            sales.append(data.get('product_sales', 0))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories, 
        y=revenues, 
        name='Ingresos por Categoría',
        marker_color='green',
        yaxis='y'
    ))
    fig.add_trace(go.Bar(
        x=categories, 
        y=sales, 
        name='Ventas por Categoría',
        marker_color='blue',
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="🛍️ Ventas por Categoría de Productos",
        xaxis_title="Categoría",
        yaxis=dict(title="Ingresos (USD)", side="left"),
        yaxis2=dict(title="Cantidad de Ventas", side="right", overlaying="y"),
        height=400
    )
    
    return fig

def create_dwh_historical_chart(historical_data):
    """Crear gráfico de datos históricos del DWH"""
    if not historical_data:
        return go.Figure()
    
    # Convertir a DataFrame para facilitar el manejo
    df = pd.DataFrame(historical_data)
    df['hour'] = pd.to_datetime(df['hour'])
    
    fig = go.Figure()
    
    # Gráfico de líneas para eventos por hora
    fig.add_trace(go.Scatter(
        x=df['hour'], 
        y=df['total_events'], 
        mode='lines+markers',
        name='Total Eventos',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['hour'], 
        y=df['transactions'], 
        mode='lines+markers',
        name='Transacciones',
        line=dict(color='green', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['hour'], 
        y=df['behavior_events'], 
        mode='lines+markers',
        name='Eventos de Comportamiento',
        line=dict(color='orange', width=3)
    ))
    
    fig.update_layout(
        title="📈 Actividad Histórica del DWH (Últimas 24 horas)",
        xaxis_title="Hora",
        yaxis_title="Cantidad de Eventos",
        height=400
    )
    
    return fig

def main():
    st.title("⚡ InstaShop Real-time Spark Metrics")
    st.markdown("---")
    
    # Conectar a Redis y DWH
    redis_client = get_redis_connection()
    dwh_conn = get_dwh_connection()
    
    if not redis_client:
        st.error("❌ No se pudo conectar a Redis. Asegúrate de que esté corriendo.")
        return
    
    if not dwh_conn:
        st.error("❌ No se pudo conectar al DWH. Asegúrate de que esté corriendo.")
        return
    
    # Auto-refresh cada 5 segundos
    if st.checkbox("🔄 Auto-refresh (cada 5s)", value=True):
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=5000, key="spark_dashboard_refresher")
    
    # Obtener métricas
    transaction_metrics = get_transaction_metrics(redis_client)
    behavior_metrics = get_behavior_metrics(redis_client)
    product_metrics = get_product_metrics(redis_client)
    
    # Obtener datos del DWH
    dwh_historical_data = get_dwh_historical_data(dwh_conn, hours=24)
    dwh_summary_stats = get_dwh_summary_stats(dwh_conn)
    
    # Mostrar timestamp de última actualización
    if transaction_metrics:
        last_update = transaction_metrics.get('timestamp', 'N/A')
        st.info(f"🕐 Última actualización: {last_update}")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if transaction_metrics:
            st.plotly_chart(create_revenue_chart(transaction_metrics), use_container_width=True)
        else:
            st.info("⏳ Esperando métricas de transacciones...")
    
    with col2:
        if transaction_metrics:
            st.plotly_chart(create_transaction_chart(transaction_metrics), use_container_width=True)
        else:
            st.info("⏳ Esperando métricas de transacciones...")
    
    with col3:
        if transaction_metrics:
            st.plotly_chart(create_customers_chart(transaction_metrics), use_container_width=True)
        else:
            st.info("⏳ Esperando métricas de transacciones...")
    
    # Gráfico de comportamiento
    st.plotly_chart(create_behavior_chart(behavior_metrics), use_container_width=True)
    
    # Gráfico de productos
    st.plotly_chart(create_product_chart(product_metrics), use_container_width=True)
    
    # Sección del Data Warehouse
    st.subheader("🏢 Data Warehouse - Información Histórica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Estadísticas Generales del DWH")
        if dwh_summary_stats:
            st.metric("Total de Eventos", f"{dwh_summary_stats['total_events']:,}")
            st.metric("Total de Transacciones", f"{dwh_summary_stats['total_transactions']:,}")
            st.metric("Total de Comportamiento", f"{dwh_summary_stats['total_behavior']:,}")
            st.metric("Clientes Únicos", f"{dwh_summary_stats['total_customers']:,}")
            st.metric("Días Activos", dwh_summary_stats['active_days'])
            
            if dwh_summary_stats['first_event']:
                st.info(f"🕐 Primer evento: {dwh_summary_stats['first_event'].strftime('%Y-%m-%d %H:%M:%S')}")
            if dwh_summary_stats['last_event']:
                st.info(f"🕐 Último evento: {dwh_summary_stats['last_event'].strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.info("⏳ Esperando datos del DWH...")
    
    with col2:
        st.subheader("📈 Actividad Histórica")
        st.plotly_chart(create_dwh_historical_chart(dwh_historical_data), use_container_width=True)
    
    # Gráfico de evolución temporal
    st.subheader("📈 Evolución Temporal")
    if transaction_metrics:
        # Crear datos de evolución (simulado para demo)
        import pandas as pd
        import numpy as np
        
        # Generar datos de los últimos 10 minutos
        now = datetime.now()
        timestamps = [now - timedelta(minutes=i) for i in range(10, 0, -1)]
        
        # Simular evolución basada en datos actuales
        base_revenue = transaction_metrics.get('total_revenue', 0)
        base_transactions = transaction_metrics.get('transaction_count', 0)
        
        revenue_data = [base_revenue * (0.8 + 0.4 * np.random.random()) for _ in range(10)]
        transaction_data = [base_transactions * (0.8 + 0.4 * np.random.random()) for _ in range(10)]
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'revenue': revenue_data,
            'transactions': transaction_data
        })
        
        # Gráfico de líneas
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['revenue'], 
            mode='lines+markers',
            name='Ingresos',
            line=dict(color='green', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['transactions'], 
            mode='lines+markers',
            name='Transacciones',
            yaxis='y2',
            line=dict(color='blue', width=3)
        ))
        
        fig.update_layout(
            title="📈 Evolución de Ingresos y Transacciones (Últimos 10 minutos)",
            xaxis_title="Tiempo",
            yaxis=dict(title="Ingresos (USD)", side="left"),
            yaxis2=dict(title="Transacciones", side="right", overlaying="y"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⏳ Esperando datos para mostrar evolución temporal...")
    
    # Métricas detalladas
    st.subheader("📋 Métricas Detalladas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("💰 Transacciones")
        if transaction_metrics:
            st.metric("Ingresos Totales", f"${transaction_metrics.get('total_revenue', 0):,.2f}")
            st.metric("Transacciones", transaction_metrics.get('total_transactions', 0))
            st.metric("Valor Promedio", f"${transaction_metrics.get('avg_amount', 0):,.2f}")
            st.metric("Clientes Únicos", transaction_metrics.get('unique_customers', 0))
            st.metric("Transacción Máxima", f"${transaction_metrics.get('max_transaction', 0):,.2f}")
            st.metric("Transacción Mínima", f"${transaction_metrics.get('min_transaction', 0):,.2f}")
        else:
            st.info("⏳ Esperando datos de Spark...")
    
    with col2:
        st.subheader("📊 Comportamiento")
        if behavior_metrics:
            for event_type, data in behavior_metrics.items():
                st.metric(
                    event_type.replace('_', ' ').title(), 
                    data.get('event_count', 0)
                )
        else:
            st.info("⏳ Esperando datos de Spark...")
    
    with col3:
        st.subheader("🛍️ Productos por Categoría")
        if product_metrics:
            # Manejar datos CDC vs legacy
            if "cdc_products" in product_metrics:
                # Datos CDC: mostrar desde la lista
                cdc_data = product_metrics["cdc_products"]
                if cdc_data:
                    for item in cdc_data:
                        category = item.get('category', 'unknown')
                        st.metric(
                            f"{category.title()} - Ventas", 
                            item.get('product_sales', 0)
                        )
                        st.metric(
                            f"{category.title()} - Ingresos", 
                            f"${item.get('category_revenue', 0):,.2f}"
                        )
            else:
                # Datos legacy: usar formato dict
                for category, data in product_metrics.items():
                    st.metric(
                        f"{category.title()} - Ventas", 
                        data.get('product_sales', 0)
                    )
                    st.metric(
                        f"{category.title()} - Ingresos", 
                        f"${data.get('category_revenue', 0):,.2f}"
                    )
                    st.metric(
                        f"{category.title()} - Clientes", 
                        data.get('unique_customers', 0)
                    )
                    st.metric(
                        f"{category.title()} - Productos", 
                        data.get('unique_products', 0)
                    )
        else:
            st.info("⏳ Esperando datos de Spark...")
    
    # Estado del sistema
    st.subheader("🔧 Estado del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if redis_client.ping():
            st.success("✅ Redis: Conectado")
        else:
            st.error("❌ Redis: Desconectado")
    
    with col2:
        if transaction_metrics or product_metrics:
            st.success("✅ Spark: Procesando datos")
        else:
            st.warning("⚠️ Spark: Sin datos recientes")
    
    with col3:
        if behavior_metrics:
            st.success("✅ Kafka: Datos fluyendo")
        else:
            st.warning("⚠️ Kafka: Sin datos recientes")
    
    with col4:
        if dwh_summary_stats:
            st.success("✅ DWH: Datos disponibles")
        else:
            st.warning("⚠️ DWH: Sin datos recientes")
    
    # Botón de refresh manual
    if st.button("🔄 Refresh Manual"):
        st.rerun()

if __name__ == "__main__":
    main()
