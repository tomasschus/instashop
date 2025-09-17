#!/usr/bin/env python3
"""
🔧 Debezium Setup Script - Automatiza la configuración de conectores Debezium
Despliega conectores PostgreSQL para capturar cambios de datos (CDC)
"""

import requests
import json
import time
import logging
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DebeziumSetup:
    def __init__(self, connect_url="http://localhost:8083"):
        self.connect_url = connect_url
        self.connectors_dir = Path(__file__).parent.parent / "debezium-config"
        self.connectors = [
            "instashop-connector.json",
            "crm-connector.json",
            "erp-connector.json",
            "ecommerce-connector.json"
        ]
        
    def wait_for_connect(self, max_retries=30):
        """Espera a que Debezium Connect esté disponible"""
        logger.info("Esperando que Debezium Connect esté disponible...")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.connect_url}/")
                if response.status_code == 200:
                    info = response.json()
                    logger.info(f"✅ Debezium Connect disponible - Versión: {info.get('version')}")
                    return True
            except requests.exceptions.RequestException:
                pass
                
            logger.info(f"⏳ Intento {attempt + 1}/{max_retries} - Esperando...")
            time.sleep(2)
            
        logger.error("❌ Debezium Connect no está disponible")
        return False

    def get_existing_connectors(self):
        """Obtiene la lista de conectores existentes"""
        try:
            response = requests.get(f"{self.connect_url}/connectors")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error obteniendo conectores: {e}")
            return []

    def delete_connector(self, connector_name):
        """Elimina un conector existente"""
        try:
            response = requests.delete(f"{self.connect_url}/connectors/{connector_name}")
            if response.status_code == 204:
                logger.info(f"🗑️  Conector {connector_name} eliminado")
                return True
            elif response.status_code == 404:
                logger.info(f"ℹ️  Conector {connector_name} no existe")
                return True
            else:
                logger.warning(f"⚠️  No se pudo eliminar {connector_name}: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error eliminando {connector_name}: {e}")
            return False

    def deploy_connector(self, config_file):
        """Despliega un conector desde archivo de configuración"""
        config_path = self.connectors_dir / config_file
        
        if not config_path.exists():
            logger.error(f"❌ Archivo de configuración no encontrado: {config_path}")
            return False
            
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            connector_name = config['name']
            logger.info(f"📤 Desplegando conector: {connector_name}")
            
            # Eliminar conector existente si existe
            self.delete_connector(connector_name)
            time.sleep(2)
            
            # Crear nuevo conector
            response = requests.post(
                f"{self.connect_url}/connectors",
                headers={'Content-Type': 'application/json'},
                json=config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Conector {connector_name} desplegado exitosamente")
                return True
            else:
                logger.error(f"❌ Error desplegando {connector_name}: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error procesando {config_file}: {e}")
            return False

    def check_connector_status(self, connector_name):
        """Verifica el estado de un conector"""
        try:
            response = requests.get(f"{self.connect_url}/connectors/{connector_name}/status")
            if response.status_code == 200:
                status = response.json()
                state = status['connector']['state']
                logger.info(f"📊 {connector_name}: {state}")
                return state == 'RUNNING'
            else:
                logger.warning(f"⚠️  No se pudo verificar {connector_name}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error verificando {connector_name}: {e}")
            return False

    def setup_all_connectors(self):
        """Configura todos los conectores"""
        logger.info("🚀 Iniciando setup de conectores Debezium")
        
        if not self.wait_for_connect():
            return False
            
        success_count = 0
        total_count = len(self.connectors)
        
        for connector_file in self.connectors:
            logger.info(f"\n📋 Procesando: {connector_file}")
            if self.deploy_connector(connector_file):
                success_count += 1
                time.sleep(3)  # Pausa entre despliegues
                
        logger.info(f"\n📈 Resumen: {success_count}/{total_count} conectores desplegados")
        
        # Verificar estados finales
        logger.info("\n🔍 Verificando estados de conectores...")
        time.sleep(5)
        
        for connector_file in self.connectors:
            config_path = self.connectors_dir / connector_file
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    connector_name = config['name']
                    self.check_connector_status(connector_name)
            except:
                pass
                
        return success_count == total_count

def main():
    setup = DebeziumSetup()
    
    if setup.setup_all_connectors():
        logger.info("🎉 ¡Setup de Debezium completado exitosamente!")
        return 0
    else:
        logger.error("💥 Falló el setup de Debezium")
        return 1

if __name__ == "__main__":
    exit(main())
