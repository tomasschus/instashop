#!/usr/bin/env python3
"""
📊 Dashboard Streamlit + Spark + Redis - Métricas en Tiempo Real
Lee métricas de Redis generadas por Spark Streaming
"""

import streamlit as st
import redis
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import time

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
        return redis.Redis(host='localhost', port=6379, decode_responses=True)
    except Exception as e:
        st.error(f"❌ Error conectando a Redis: {e}")
        return None

def get_transaction_metrics(redis_client):
    """Obtener métricas de transacciones de Redis"""
    try:
        data = redis_client.get("metrics:transactions")
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        st.error(f"❌ Error obteniendo métricas de transacciones: {e}")
        return None

def get_behavior_metrics(redis_client):
    """Obtener métricas de comportamiento de Redis"""
    try:
        behavior_types = ['page_view', 'product_view', 'search', 'add_to_cart', 'remove_from_cart']
        metrics = {}
        
        for event_type in behavior_types:
            data = redis_client.get(f"metrics:behavior:{event_type}")
            if data:
                metrics[event_type] = json.loads(data)
        
        return metrics
    except Exception as e:
        st.error(f"❌ Error obteniendo métricas de comportamiento: {e}")
        return {}

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
        value = metrics.get('transaction_count', 0),
        title = {"text": "Transacciones"},
        delta = {"reference": metrics.get('transaction_count', 0) * 0.8},
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

def main():
    st.title("⚡ InstaShop Real-time Spark Metrics")
    st.markdown("---")
    
    # Conectar a Redis
    redis_client = get_redis_connection()
    
    if not redis_client:
        st.error("❌ No se pudo conectar a Redis. Asegúrate de que esté corriendo.")
        return
    
    # Auto-refresh cada 5 segundos
    if st.checkbox("🔄 Auto-refresh (cada 5s)", value=True):
        time.sleep(5)
        st.rerun()
    
    # Obtener métricas
    transaction_metrics = get_transaction_metrics(redis_client)
    behavior_metrics = get_behavior_metrics(redis_client)
    
    # Mostrar timestamp de última actualización
    if transaction_metrics:
        last_update = transaction_metrics.get('timestamp', 'N/A')
        st.info(f"🕐 Última actualización: {last_update}")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(create_revenue_chart(transaction_metrics), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_transaction_chart(transaction_metrics), use_container_width=True)
    
    with col3:
        st.plotly_chart(create_customers_chart(transaction_metrics), use_container_width=True)
    
    # Gráfico de comportamiento
    st.plotly_chart(create_behavior_chart(behavior_metrics), use_container_width=True)
    
    # Métricas detalladas
    st.subheader("📋 Métricas Detalladas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Transacciones")
        if transaction_metrics:
            st.metric("Ingresos Totales", f"${transaction_metrics.get('total_revenue', 0):,.2f}")
            st.metric("Transacciones", transaction_metrics.get('transaction_count', 0))
            st.metric("Valor Promedio", f"${transaction_metrics.get('avg_transaction_value', 0):,.2f}")
            st.metric("Clientes Únicos", transaction_metrics.get('unique_customers', 0))
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
    
    # Estado del sistema
    st.subheader("🔧 Estado del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if redis_client.ping():
            st.success("✅ Redis: Conectado")
        else:
            st.error("❌ Redis: Desconectado")
    
    with col2:
        if transaction_metrics:
            st.success("✅ Spark: Procesando datos")
        else:
            st.warning("⚠️ Spark: Sin datos recientes")
    
    with col3:
        if behavior_metrics:
            st.success("✅ Kafka: Datos fluyendo")
        else:
            st.warning("⚠️ Kafka: Sin datos recientes")
    
    # Botón de refresh manual
    if st.button("🔄 Refresh Manual"):
        st.rerun()

if __name__ == "__main__":
    main()
