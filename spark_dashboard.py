"""
Spark Analytics Dashboard with Streamlit
Real-time analytics dashboard showing Spark analysis results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import time
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="InstaShop Spark Analytics",
    page_icon="🚀",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        port=5436,
        dbname='dwh_db',
        user='dwh',
        password='dwh123'
    )

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_realtime_data():
    """Get real-time data from DWH"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5436,
            dbname='dwh_db',
            user='dwh',
            password='dwh123'
        )
        query = """
        SELECT 
            event_type,
            timestamp,
            customer_id,
            customer_name,
            product_name,
            category,
            amount,
            raw_data
        FROM realtime_events 
        ORDER BY timestamp DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

def get_event_stats():
    """Get event statistics"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5436,
            dbname='dwh_db',
            user='dwh',
            password='dwh123'
        )
        query = """
        SELECT 
            event_type,
            COUNT(*) as count,
            MAX(timestamp) as latest_event,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM realtime_events 
        GROUP BY event_type
        ORDER BY count DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error getting stats: {e}")
        return pd.DataFrame()

def get_transaction_analysis():
    """Get transaction analysis"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5436,
            dbname='dwh_db',
            user='dwh',
            password='dwh123'
        )
        query = """
        SELECT 
            customer_id,
            customer_name,
            COUNT(*) as transaction_count,
            SUM(amount) as total_spent,
            AVG(amount) as avg_transaction,
            MAX(timestamp) as last_transaction
        FROM realtime_events 
        WHERE event_type = 'transaction'
        GROUP BY customer_id, customer_name
        ORDER BY transaction_count DESC
        LIMIT 10
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error getting transaction analysis: {e}")
        return pd.DataFrame()

def get_category_analysis():
    """Get category analysis"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5436,
            dbname='dwh_db',
            user='dwh',
            password='dwh123'
        )
        query = """
        SELECT 
            category,
            COUNT(*) as event_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM realtime_events 
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY event_count DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error getting category analysis: {e}")
        return pd.DataFrame()

def main():
    st.title("🚀 InstaShop Spark Analytics Dashboard")
    st.markdown("---")
    
    # Auto-refresh every 30 seconds
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Get data
    with st.spinner("Loading data..."):
        realtime_data = get_realtime_data()
        event_stats = get_event_stats()
        transaction_analysis = get_transaction_analysis()
        category_analysis = get_category_analysis()
    
    if realtime_data.empty:
        st.error("No data available. Make sure the pipeline is running!")
        return
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Events",
            value=len(realtime_data),
            delta=f"+{len(realtime_data)}"
        )
    
    with col2:
        unique_customers = realtime_data['customer_id'].nunique()
        st.metric(
            label="👥 Unique Customers",
            value=unique_customers,
            delta=f"+{unique_customers}"
        )
    
    with col3:
        total_revenue = realtime_data[realtime_data['event_type'] == 'transaction']['amount'].sum()
        st.metric(
            label="💰 Total Revenue",
            value=f"${total_revenue:,.2f}",
            delta=f"+${total_revenue:,.2f}"
        )
    
    with col4:
        latest_event = realtime_data['timestamp'].max()
        st.metric(
            label="⏰ Latest Event",
            value=latest_event.strftime("%H:%M:%S"),
            delta="Now"
        )
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Events by Type")
        if not event_stats.empty:
            fig = px.pie(
                event_stats, 
                values='count', 
                names='event_type',
                title="Event Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No event statistics available")
    
    with col2:
        st.subheader("🏆 Top Customers")
        if not transaction_analysis.empty:
            fig = px.bar(
                transaction_analysis.head(5),
                x='customer_name',
                y='transaction_count',
                title="Top 5 Customers by Transactions"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transaction data available")
    
    # Category analysis
    st.subheader("🛍️ Category Analysis")
    if not category_analysis.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                category_analysis,
                x='category',
                y='event_count',
                title="Events by Category"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                category_analysis,
                x='category',
                y='total_amount',
                title="Revenue by Category"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available")
    
    # Recent events table
    st.subheader("📋 Recent Events")
    if not realtime_data.empty:
        recent_events = realtime_data.head(20)[
            ['event_type', 'timestamp', 'customer_name', 'product_name', 'category', 'amount']
        ]
        st.dataframe(recent_events, use_container_width=True)
    else:
        st.info("No recent events available")
    
    # Auto-refresh info
    st.markdown("---")
    st.info("🔄 Dashboard auto-refreshes every 30 seconds. Click 'Refresh Data' for immediate update.")
    
    # Pipeline status
    st.subheader("🔧 Pipeline Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Producer → Kafka")
        st.caption("Generating events to Kafka topics")
    
    with col2:
        st.success("✅ Consumer → DWH")
        st.caption("Processing events to Data Warehouse")
    
    with col3:
        st.success("✅ Spark Analytics")
        st.caption("Real-time analysis and insights")

if __name__ == "__main__":
    main()
