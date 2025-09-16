# ⚡ InstaShop Nico Scripts - Inicio Rápido

## 🚀 Configuración en 2 Pasos

### 1. Activar Entorno Virtual
```bash
source venv/bin/activate
```

### 2. Ejecutar Scripts
```bash
cd nico-scripts
python setup_and_run.py
```

### 3. Ver Dashboards
- **Monitor en tiempo real**: http://localhost:8503
- **Dashboard original**: http://localhost:8501
- **Spark Analytics**: http://localhost:8502

## 🎯 Opciones Disponibles

### Generador de Datos Realistas
```bash
python realistic_data_generator.py
```

### Simulador de Comportamiento Avanzado
```bash
python advanced_behavior_simulator.py
```

### Monitor en Tiempo Real
```bash
python realtime_monitor.py
```

### Configuración Completa
```bash
python setup_and_run.py
```

## 🔧 Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.8+ instalado
- Acceso a internet para descargar dependencias

## 📊 Datos Generados

- **Transacciones**: Con productos realistas y precios dinámicos
- **Eventos de comportamiento**: Búsquedas, vistas, carrito
- **Sesiones de clientes**: Con análisis de conversión
- **Métricas en tiempo real**: Ingresos, conversión, actividad

## 🎯 Características Principales

- **Patrones realistas**: Horarios de actividad, estacionalidad
- **Perfiles de clientes**: High Value, Regular, Bargain Hunter
- **Pricing dinámico**: Precios que cambian según demanda
- **Dashboard interactivo**: Métricas en tiempo real
- **Análisis avanzado**: Conversión, abandono, comportamiento

## 🚨 Troubleshooting

### Error de Docker
```bash
docker-compose up -d
```

### Error de dependencias
```bash
source venv/bin/activate
pip install -r requirements.txt
pip install numpy pandas plotly streamlit
```

### Error de conexión a BD
```bash
docker-compose ps
docker-compose logs postgres
```

## 📞 Soporte

Para problemas o dudas:
1. Revisa los logs en `nico-scripts/*.log`
2. Verifica que Docker esté ejecutándose
3. Asegúrate de que el entorno virtual esté activado
4. Consulta el README.md completo para más detalles

---

**🚀 ¡Disfruta generando datos realistas!**
