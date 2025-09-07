"""
ETL Pipeline Local para InstaShop Analytics
Ejecuta desde localhost conectando a contenedores Docker
"""

import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class LocalInstaShopETL:
    def __init__(self):
        """Inicializa conexiones a bases de datos locales"""
        self.connections = {
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
    
    def get_connection(self, db_key):
        """Obtiene conexión a base de datos"""
        config = self.connections[db_key]
        return psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['dbname'],
            user=config['user'],
            password=config['password']
        )
    
    def test_connections(self):
        """Prueba todas las conexiones"""
        print("🔍 Probando conexiones a bases de datos...")
        
        for db_key, config in self.connections.items():
            try:
                conn = self.get_connection(db_key)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                print(f"✅ {db_key}: Conexión exitosa")
            except Exception as e:
                print(f"❌ {db_key}: Error - {str(e)}")
                return False
        
        return True
    
    def extract_sales_data(self):
        """Extrae datos de ventas"""
        print("📊 Extrayendo datos de ventas...")
        
        conn = self.get_connection('instashop')
        
        query = """
        SELECT 
            t.transaction_id,
            t.transaction_date,
            t.total_amount,
            t.payment_method,
            t.status,
            c.customer_id,
            c.business_name,
            c.subscription_plan,
            td.quantity,
            td.unit_price,
            p.product_id,
            p.name as product_name,
            p.category,
            p.price as product_price
        FROM transaction t
        JOIN customer c ON t.customer_id = c.customer_id
        JOIN transactiondetail td ON t.transaction_id = td.transaction_id  
        JOIN product p ON td.product_id = p.product_id
        WHERE t.transaction_date >= CURRENT_DATE - INTERVAL '90 days'
        ORDER BY t.transaction_date DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"✅ {len(df)} registros de ventas extraídos")
        return df
    
    def extract_inventory_data(self):
        """Extrae datos de inventario"""
        print("📦 Extrayendo datos de inventario...")
        
        conn = self.get_connection('erp')
        
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
        
        print(f"✅ {len(df)} productos en inventario extraídos")
        return df
    
    def calculate_kpis(self, sales_df):
        """Calcula KPIs principales"""
        print("📈 Calculando KPIs...")
        
        if sales_df.empty:
            print("⚠️ No hay datos de ventas para calcular KPIs")
            return {}
        
        # KPIs básicos
        total_revenue = sales_df['total_amount'].sum()
        total_transactions = sales_df['transaction_id'].nunique()
        avg_order_value = sales_df['total_amount'].mean()
        unique_customers = sales_df['customer_id'].nunique()
        
        # KPIs por período
        sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'])
        
        # Últimos 30 días
        last_30_days = sales_df[
            sales_df['transaction_date'] >= (datetime.now() - timedelta(days=30))
        ]
        
        revenue_30d = last_30_days['total_amount'].sum() if not last_30_days.empty else 0
        transactions_30d = last_30_days['transaction_id'].nunique() if not last_30_days.empty else 0
        
        kpis = {
            'total_revenue': float(total_revenue),
            'total_transactions': int(total_transactions),
            'avg_order_value': float(avg_order_value),
            'unique_customers': int(unique_customers),
            'revenue_30d': float(revenue_30d),
            'transactions_30d': int(transactions_30d),
            'calculated_at': datetime.now()
        }
        
        print("✅ KPIs calculados")
        return kpis
    
    def create_dwh_tables(self):
        """Crea tablas en DWH si no existen"""
        print("🏗️ Creando tablas en DWH...")
        
        conn = self.get_connection('dwh')
        cursor = conn.cursor()
        
        # Tabla de resumen de ventas
        sales_table_sql = """
        CREATE TABLE IF NOT EXISTS sales_summary (
            transaction_id INT,
            transaction_date DATE,
            total_amount DECIMAL(10,2),
            payment_method VARCHAR(50),
            customer_id INT,
            business_name VARCHAR(255),
            subscription_plan VARCHAR(50),
            product_name VARCHAR(255),
            category VARCHAR(100),
            quantity INT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Tabla de estado de inventario
        inventory_table_sql = """
        CREATE TABLE IF NOT EXISTS inventory_status (
            product_id INT,
            available_quantity INT,
            reorder_point INT,
            stock_status VARCHAR(20),
            warehouse_location VARCHAR(100),
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Tabla de KPIs
        kpis_table_sql = """
        CREATE TABLE IF NOT EXISTS kpis_summary (
            metric_name VARCHAR(50),
            metric_value DECIMAL(15,2),
            metric_date DATE,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(sales_table_sql)
        cursor.execute(inventory_table_sql)
        cursor.execute(kpis_table_sql)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Tablas DWH creadas")
    
    def save_kpis_to_dwh(self, kpis):
        """Guarda KPIs al DWH"""
        if not kpis:
            return
            
        print("💾 Guardando KPIs en DWH...")
        
        conn = self.get_connection('dwh')
        cursor = conn.cursor()
        
        # Limpiar KPIs del día actual
        today = datetime.now().date()
        cursor.execute("DELETE FROM kpis_summary WHERE metric_date = %s", (today,))
        
        # Insertar nuevos KPIs
        for metric_name, value in kpis.items():
            if metric_name != 'calculated_at' and isinstance(value, (int, float)):
                cursor.execute(
                    "INSERT INTO kpis_summary (metric_name, metric_value, metric_date) VALUES (%s, %s, %s)",
                    (metric_name, value, today)
                )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ KPIs guardados en DWH")
    
    def run_etl(self):
        """Ejecuta el proceso ETL completo"""
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO ETL PIPELINE LOCAL - {datetime.now()}")
        print(f"{'='*60}\n")
        
        try:
            # 0. Probar conexiones
            if not self.test_connections():
                print("❌ Error en conexiones a bases de datos")
                return False
            
            # 1. Crear tablas DWH
            self.create_dwh_tables()
            
            # 2. Extraer datos
            sales_df = self.extract_sales_data()
            inventory_df = self.extract_inventory_data()
            
            # 3. Transformar y calcular métricas
            kpis = self.calculate_kpis(sales_df)
            
            # 4. Guardar KPIs al DWH
            self.save_kpis_to_dwh(kpis)
            
            # 5. Mostrar resumen
            print(f"\n{'='*60}")
            print("📊 RESUMEN DEL ETL")
            print(f"{'='*60}")
            
            if kpis:
                print(f"💰 Revenue Total: ${kpis['total_revenue']:,.2f}")
                print(f"🛍️  Transacciones: {kpis['total_transactions']:,}")
                print(f"📈 AOV: ${kpis['avg_order_value']:.2f}")
                print(f"👥 Customers Únicos: {kpis['unique_customers']:,}")
                print(f"💵 Revenue 30d: ${kpis['revenue_30d']:,.2f}")
                print(f"🛒 Transacciones 30d: {kpis['transactions_30d']:,}")
            else:
                print("⚠️ No se pudieron calcular KPIs")
            
            print(f"📦 Productos en inventario: {len(inventory_df)}")
            
            if not inventory_df.empty:
                critical_stock = inventory_df[inventory_df['stock_status'] == 'Crítico']
                print(f"🔴 Productos con stock crítico: {len(critical_stock)}")
            
            print(f"✅ ETL completado exitosamente!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en ETL Pipeline: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Función principal"""
    etl = LocalInstaShopETL()
    etl.run_etl()

if __name__ == "__main__":
    main()
