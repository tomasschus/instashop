from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="InstaShop Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_db_config():
    return {
        'instashop': {'host': 'localhost', 'port': 5432, 'dbname': 'instashop', 'user': 'insta', 'password': 'insta123'},
        'crm': {'host': 'localhost', 'port': 5433, 'dbname': 'crm_db', 'user': 'crm', 'password': 'crm123'},
        'erp': {'host': 'localhost', 'port': 5434, 'dbname': 'erp_db', 'user': 'erp', 'password': 'erp123'},
        'dwh': {'host': 'localhost', 'port': 5436, 'dbname': 'dwh_db', 'user': 'dwh', 'password': 'dwh123'}
    }

def get_connection(db_key):
    config = get_db_config()[db_key]
    return psycopg2.connect(**config)

@st.cache_data(ttl=60)
def load_sales_data():
    conn = get_connection("instashop")
    
    query = """
    SELECT 
        t.transaction_date,
        t.total_amount,
        t.payment_method,
        t.status,
        c.business_name,
        c.subscription_plan,
        p.name as product_name,
        p.category,
        td.quantity,
        td.unit_price
    FROM transaction t
    JOIN customer c ON t.customer_id = c.customer_id
    JOIN transactiondetail td ON t.transaction_id = td.transaction_id
    JOIN product p ON td.product_id = p.product_id
    WHERE t.status = 'completed'
    ORDER BY t.transaction_date DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def load_customer_metrics():
    conn = get_connection("instashop")
    
    query = """
    SELECT 
        c.customer_id,
        c.business_name,
        c.subscription_plan,
        COUNT(t.transaction_id) as total_transactions,
        SUM(t.total_amount) as total_revenue,
        AVG(t.total_amount) as avg_order_value
    FROM customer c
    LEFT JOIN transaction t ON c.customer_id = t.customer_id
    WHERE t.status = 'completed' OR t.status IS NULL
    GROUP BY c.customer_id, c.business_name, c.subscription_plan
    ORDER BY total_revenue DESC NULLS LAST
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def load_inventory_data():
    conn = get_connection("erp")
    
    query = """
    SELECT 
        s.product_id,
        s.available_quantity,
        s.reorder_point,
        s.warehouse_location,
        CASE 
            WHEN s.available_quantity <= s.reorder_point THEN 'Crítico'
            WHEN s.available_quantity <= s.reorder_point * 1.5 THEN 'Bajo'
            ELSE 'Óptimo'
        END as stock_status
    FROM stock s
    ORDER BY s.available_quantity ASC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def main():
    st.title("🛒 InstaShop Analytics Dashboard")
    st.markdown("**Inteligencia de Negocio para el Comercio Electrónico**")
    
    st.sidebar.header("🎛️ Controles")
    
    date_range = st.sidebar.date_input(
        "Rango de fechas",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    with st.spinner("Cargando datos..."):
        sales_df = load_sales_data()
        customer_metrics = load_customer_metrics()
        inventory_df = load_inventory_data()
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        sales_df = sales_df[
            (pd.to_datetime(sales_df['transaction_date']).dt.date >= start_date) &
            (pd.to_datetime(sales_df['transaction_date']).dt.date <= end_date)
        ]
    
    st.header("📊 KPIs Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = sales_df['total_amount'].sum()
        st.metric("💰 Revenue Total", f"${total_revenue:,.2f}")
    
    with col2:
        total_transactions = len(sales_df)
        st.metric("🛍️ Transacciones", f"{total_transactions:,}")
    
    with col3:
        avg_order_value = sales_df['total_amount'].mean()
        st.metric("📈 AOV", f"${avg_order_value:.2f}")
    
    with col4:
        active_customers = customer_metrics[customer_metrics['total_revenue'] > 0].shape[0]
        st.metric("👥 Customers Activos", f"{active_customers:,}")
    
    st.header("📈 Análisis de Ventas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        daily_sales = sales_df.groupby(
            pd.to_datetime(sales_df['transaction_date']).dt.date
        )['total_amount'].sum().reset_index()
        
        fig = px.line(
            daily_sales, 
            x='transaction_date', 
            y='total_amount',
            title="Ventas Diarias",
            labels={'total_amount': 'Revenue ($)', 'transaction_date': 'Fecha'}
        )
        st.plotly_chart(fig, use_container_width=True, key="daily_sales_chart")
    
    with col2:
        category_sales = sales_df.groupby('category')['total_amount'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=category_sales.values,
            y=category_sales.index,
            orientation='h',
            title="Top 10 Categorías por Revenue",
            labels={'x': 'Revenue ($)', 'y': 'Categoría'}
        )
        st.plotly_chart(fig, use_container_width=True, key="category_sales_chart")
    
    st.header("👥 Análisis de Customers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        plan_metrics = customer_metrics.groupby('subscription_plan').agg({
            'total_revenue': 'sum',
            'customer_id': 'count'
        }).reset_index()
        
        fig = px.pie(
            plan_metrics,
            values='customer_id',
            names='subscription_plan',
            title="Distribución de Customers por Plan"
        )
        st.plotly_chart(fig, use_container_width=True, key="customer_plan_chart")
    
    with col2:
        top_customers = customer_metrics.head(10)
        
        fig = px.bar(
            top_customers,
            x='total_revenue',
            y='business_name',
            orientation='h',
            title="Top 10 Customers por Revenue",
            labels={'total_revenue': 'Revenue ($)', 'business_name': 'Customer'}
        )
        st.plotly_chart(fig, use_container_width=True, key="top_customers_chart")
    
    st.header("📦 Análisis de Inventario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stock_status_counts = inventory_df['stock_status'].value_counts()
        
        fig = px.pie(
            values=stock_status_counts.values,
            names=stock_status_counts.index,
            title="Estado del Stock",
            color_discrete_map={
                'Crítico': '#ff4444',
                'Bajo': '#ffaa44', 
                'Óptimo': '#44ff44'
            }
        )
        st.plotly_chart(fig, use_container_width=True, key="stock_status_chart")
    
    with col2:
        critical_stock = inventory_df[inventory_df['stock_status'] == 'Crítico'].head(10)
        
        if not critical_stock.empty:
            fig = px.bar(
                critical_stock,
                x='available_quantity',
                y='product_id',
                orientation='h',
                title="Productos con Stock Crítico",
                labels={'available_quantity': 'Cantidad Disponible', 'product_id': 'Product ID'}
            )
            st.plotly_chart(fig, use_container_width=True, key="critical_stock_chart")
        else:
            st.success("🎉 No hay productos con stock crítico")
    
    st.header("📋 Datos Detallados")
    
    tab1, tab2, tab3 = st.tabs(["Ventas Recientes", "Métricas de Customers", "Estado de Inventario"])
    
    with tab1:
        st.subheader("Últimas Transacciones")
        recent_sales = sales_df.head(20)[['transaction_date', 'business_name', 'product_name', 'total_amount', 'payment_method']]
        st.dataframe(recent_sales, use_container_width=True)
    
    with tab2:
        st.subheader("Métricas por Customer")
        st.dataframe(customer_metrics, use_container_width=True)
    
    with tab3:
        st.subheader("Estado del Inventario")
        st.dataframe(inventory_df, use_container_width=True)

if __name__ == "__main__":
    main()
