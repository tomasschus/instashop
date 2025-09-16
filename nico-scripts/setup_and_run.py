#!/usr/bin/env python3
"""
🚀 InstaShop Setup and Run Script
Script de configuración y ejecución para todos los generadores de datos
"""

import os
import sys
import subprocess
import time
import psycopg2
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstaShopSetup:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scripts_dir = os.path.join(self.project_root, 'nico-scripts')
        
    def check_docker_status(self):
        """Verificar que Docker esté ejecutándose"""
        try:
            result = subprocess.run(['docker', 'compose', 'ps'], 
                                 capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                logger.info("✅ Docker Compose está ejecutándose")
                return True
            else:
                logger.error("❌ Docker Compose no está ejecutándose")
                return False
        except FileNotFoundError:
            logger.error("❌ Docker no está instalado")
            return False

    def check_database_connections(self):
        """Verificar conexiones a las bases de datos"""
        databases = [
            {'name': 'instashop', 'host': 'localhost', 'port': 5432, 'user': 'insta', 'password': 'insta123'},
            {'name': 'dwh_db', 'host': 'localhost', 'port': 5436, 'user': 'dwh', 'password': 'dwh123'},
            {'name': 'crm_db', 'host': 'localhost', 'port': 5433, 'user': 'crm', 'password': 'crm123'}
        ]
        
        all_connected = True
        for db in databases:
            try:
                conn = psycopg2.connect(
                    host=db['host'],
                    port=db['port'],
                    dbname=db['name'],
                    user=db['user'],
                    password=db['password']
                )
                conn.close()
                logger.info(f"✅ Conectado a {db['name']}")
            except Exception as e:
                logger.error(f"❌ Error conectando a {db['name']}: {e}")
                all_connected = False
        
        return all_connected

    def check_virtual_environment(self):
        """Verificar y activar entorno virtual"""
        venv_path = os.path.join(self.project_root, 'venv')
        
        if not os.path.exists(venv_path):
            logger.warning("⚠️ Entorno virtual no encontrado")
            logger.info("💡 Creando entorno virtual...")
            try:
                subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
                logger.info("✅ Entorno virtual creado")
            except subprocess.CalledProcessError:
                logger.error("❌ Error creando entorno virtual")
                return False
        
        # Verificar si estamos en el entorno virtual
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("✅ Entorno virtual activado")
            return True
        else:
            logger.warning("⚠️ Entorno virtual no activado")
            logger.info("💡 Activa el entorno virtual:")
            logger.info(f"   source {venv_path}/bin/activate")
            logger.info("   o ejecuta: python -m venv venv && source venv/bin/activate")
            return False

    def check_python_dependencies(self):
        """Verificar dependencias de Python"""
        required_packages = [
            'psycopg2-binary',
            'faker',
            'numpy',
            'pandas',
            'plotly',
            'streamlit'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✅ {package} instalado")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"⚠️ {package} no instalado")
        
        if missing_packages:
            logger.error(f"❌ Paquetes faltantes: {', '.join(missing_packages)}")
            logger.info("💡 Ejecuta: pip install " + " ".join(missing_packages))
            return False
        
        return True

    def setup_database_tables(self):
        """Configurar tablas necesarias en las bases de datos"""
        logger.info("🔧 Configurando tablas de base de datos...")
        
        # Tabla para eventos en tiempo real en DWH
        try:
            conn = psycopg2.connect(
                host='localhost', port=5436, dbname='dwh_db', 
                user='dwh', password='dwh123'
            )
            cursor = conn.cursor()
            
            # Crear tabla de eventos en tiempo real
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS realtime_events (
                    event_id BIGSERIAL PRIMARY KEY,
                    customer_id BIGINT,
                    event_type VARCHAR(50),
                    event_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Crear tabla de sesiones de clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_sessions (
                    session_id VARCHAR(100) PRIMARY KEY,
                    customer_id BIGINT,
                    session_data JSONB,
                    outcome VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("✅ Tablas de DWH configuradas")
            
        except Exception as e:
            logger.error(f"❌ Error configurando tablas DWH: {e}")
            return False
        
        return True

    def run_data_generator(self, duration_minutes=30):
        """Ejecutar generador de datos realistas"""
        logger.info(f"🚀 Ejecutando generador de datos por {duration_minutes} minutos...")
        
        script_path = os.path.join(self.scripts_dir, 'realistic_data_generator.py')
        
        try:
            # Ejecutar script con duración específica
            process = subprocess.Popen([
                sys.executable, script_path
            ], stdin=subprocess.PIPE, text=True)
            
            # Enviar duración como input
            process.stdin.write(f"{duration_minutes}\n")
            process.stdin.close()
            
            logger.info("✅ Generador de datos iniciado")
            return process
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando generador: {e}")
            return None

    def run_behavior_simulator(self, duration_minutes=30):
        """Ejecutar simulador de comportamiento avanzado"""
        logger.info(f"🧠 Ejecutando simulador de comportamiento por {duration_minutes} minutos...")
        
        script_path = os.path.join(self.scripts_dir, 'advanced_behavior_simulator.py')
        
        try:
            process = subprocess.Popen([
                sys.executable, script_path
            ], stdin=subprocess.PIPE, text=True)
            
            process.stdin.write(f"{duration_minutes}\n")
            process.stdin.close()
            
            logger.info("✅ Simulador de comportamiento iniciado")
            return process
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando simulador: {e}")
            return None

    def run_realtime_monitor(self):
        """Ejecutar monitor en tiempo real"""
        logger.info("📊 Iniciando monitor en tiempo real...")
        
        script_path = os.path.join(self.scripts_dir, 'realtime_monitor.py')
        
        try:
            process = subprocess.Popen([
                sys.executable, script_path
            ])
            
            logger.info("✅ Monitor en tiempo real iniciado")
            logger.info("🌐 Dashboard disponible en: http://localhost:8503")
            return process
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando monitor: {e}")
            return None

    def show_menu(self):
        """Mostrar menú principal"""
        print("\n" + "="*60)
        print("🚀 INSTASHOP DATA GENERATION SUITE")
        print("="*60)
        print("1. 🔧 Verificar configuración del sistema")
        print("2. 🎯 Ejecutar generador de datos realistas")
        print("3. 🧠 Ejecutar simulador de comportamiento avanzado")
        print("4. 📊 Ejecutar monitor en tiempo real")
        print("5. 🚀 Ejecutar pipeline completo (generador + simulador + monitor)")
        print("6. 📈 Ver estadísticas del sistema")
        print("7. 🧹 Limpiar datos de prueba")
        print("8. ❌ Salir")
        print("="*60)

    def show_system_stats(self):
        """Mostrar estadísticas del sistema"""
        print("\n📈 ESTADÍSTICAS DEL SISTEMA")
        print("-" * 40)
        
        try:
            # Estadísticas de transacciones
            conn = psycopg2.connect(
                host='localhost', port=5432, dbname='instashop', 
                user='insta', password='insta123'
            )
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM transaction")
            total_transactions = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(total_amount) FROM transaction WHERE status = 'completed'")
            total_revenue = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM transaction")
            unique_customers = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"🛒 Total de transacciones: {total_transactions:,}")
            print(f"💰 Ingresos totales: ${total_revenue:,.2f}")
            print(f"👥 Clientes únicos: {unique_customers:,}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
        
        try:
            # Estadísticas de eventos en tiempo real
            conn = psycopg2.connect(
                host='localhost', port=5436, dbname='dwh_db', 
                user='dwh', password='dwh123'
            )
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM realtime_events")
            total_events = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM realtime_events WHERE timestamp >= NOW() - INTERVAL '1 hour'")
            recent_events = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"📊 Total de eventos: {total_events:,}")
            print(f"⏰ Eventos (última hora): {recent_events:,}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de eventos: {e}")

    def cleanup_test_data(self):
        """Limpiar datos de prueba"""
        print("\n🧹 LIMPIANDO DATOS DE PRUEBA")
        print("-" * 40)
        
        confirm = input("¿Estás seguro de que quieres limpiar todos los datos de prueba? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Operación cancelada")
            return
        
        try:
            # Limpiar eventos en tiempo real
            conn = psycopg2.connect(
                host='localhost', port=5436, dbname='dwh_db', 
                user='dwh', password='dwh123'
            )
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM realtime_events")
            cursor.execute("DELETE FROM customer_sessions")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Datos de prueba limpiados")
            
        except Exception as e:
            print(f"❌ Error limpiando datos: {e}")

    def run_complete_pipeline(self, duration_minutes=30):
        """Ejecutar pipeline completo"""
        logger.info("🚀 Ejecutando pipeline completo...")
        
        processes = []
        
        try:
            # Iniciar generador de datos
            gen_process = self.run_data_generator(duration_minutes)
            if gen_process:
                processes.append(('Generador de Datos', gen_process))
            
            time.sleep(5)  # Esperar un poco antes del siguiente
            
            # Iniciar simulador de comportamiento
            sim_process = self.run_behavior_simulator(duration_minutes)
            if sim_process:
                processes.append(('Simulador de Comportamiento', sim_process))
            
            time.sleep(5)
            
            # Iniciar monitor
            mon_process = self.run_realtime_monitor()
            if mon_process:
                processes.append(('Monitor en Tiempo Real', mon_process))
            
            logger.info("✅ Pipeline completo iniciado")
            logger.info("🌐 Dashboard disponible en: http://localhost:8503")
            
            # Esperar a que terminen los procesos
            for name, process in processes:
                logger.info(f"⏳ Esperando a que termine {name}...")
                process.wait()
            
        except KeyboardInterrupt:
            logger.info("⏹️ Deteniendo pipeline...")
            for name, process in processes:
                logger.info(f"🛑 Deteniendo {name}...")
                process.terminate()
                process.wait()

    def main(self):
        """Función principal"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\nSelecciona una opción (1-8): ").strip()
                
                if choice == "1":
                    print("\n🔧 VERIFICANDO CONFIGURACIÓN DEL SISTEMA")
                    print("-" * 50)
                    
                    docker_ok = self.check_docker_status()
                    venv_ok = self.check_virtual_environment()
                    db_ok = self.check_database_connections()
                    deps_ok = self.check_python_dependencies()
                    
                    if docker_ok and venv_ok and db_ok and deps_ok:
                        print("\n✅ Sistema configurado correctamente")
                        self.setup_database_tables()
                    else:
                        print("\n❌ Hay problemas con la configuración")
                        print("💡 Revisa los errores anteriores y corrige antes de continuar")
                
                elif choice == "2":
                    duration = int(input("¿Cuántos minutos ejecutar? (default: 30): ") or "30")
                    self.run_data_generator(duration)
                
                elif choice == "3":
                    duration = int(input("¿Cuántos minutos ejecutar? (default: 30): ") or "30")
                    self.run_behavior_simulator(duration)
                
                elif choice == "4":
                    self.run_realtime_monitor()
                
                elif choice == "5":
                    duration = int(input("¿Cuántos minutos ejecutar? (default: 30): ") or "30")
                    self.run_complete_pipeline(duration)
                
                elif choice == "6":
                    self.show_system_stats()
                
                elif choice == "7":
                    self.cleanup_test_data()
                
                elif choice == "8":
                    print("\n👋 ¡Hasta luego!")
                    break
                
                else:
                    print("❌ Opción inválida")
                
                input("\nPresiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Presiona Enter para continuar...")

if __name__ == "__main__":
    setup = InstaShopSetup()
    setup.main()
