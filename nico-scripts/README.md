# 🚀 Nico Scripts - InstaShop Data Generation Suite

Esta carpeta contiene scripts avanzados para generar datos realistas en tiempo real para el proyecto InstaShop.

## ⚡ Inicio Rápido

### 🚀 Configuración Manual
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar cualquier script
python realistic_data_generator.py
```

### 🎯 Configuración Completa
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar configuración completa
python setup_and_run.py
```

## 📁 Archivos Incluidos

### 🎯 Scripts Principales

1. **`realistic_data_generator.py`** - Generador de datos realistas básico
2. **`advanced_behavior_simulator.py`** - Simulador avanzado de comportamiento de usuarios
3. **`realtime_monitor.py`** - Monitor en tiempo real de métricas y estadísticas
4. **`setup_and_run.py`** - Configuración completa y menú interactivo

### 📊 Características

## 🎯 Realistic Data Generator

**Propósito**: Genera datos de transacciones y eventos de comportamiento en tiempo real con patrones realistas.

### ✨ Características Principales

- **Patrones de comportamiento realistas**:
  - Actividad por hora del día (picos en horas laborales y nocturnas)
  - Patrones semanales (más actividad en fin de semana)
  - Estacionalidad (Black Friday, Navidad, etc.)

- **Perfiles de clientes**:
  - **High Value** (15%): Clientes premium con compras grandes
  - **Regular** (60%): Clientes promedio con compras moderadas
  - **Bargain Hunter** (25%): Clientes que buscan ofertas

- **Catálogo de productos realista**:
  - 5 categorías con productos específicos
  - Precios dinámicos con variación estacional
  - Inventario con puntos de reorden

- **Eventos generados**:
  - Transacciones completas con detalles
  - Eventos de comportamiento (búsquedas, vistas de productos)
  - Abandono de carrito
  - Interacciones de CRM

### 🚀 Cómo Usar

```bash
# Opción 1: Script de inicio automático (recomendado)
cd nico-scripts
./start.sh

# Opción 2: Manual
# Activar entorno virtual
source venv/bin/activate

# Ejecutar generador básico
python nico-scripts/realistic_data_generator.py
```

## 🧠 Advanced Behavior Simulator

**Propósito**: Simulador sofisticado que modela el journey completo del cliente con patrones de comportamiento complejos.

### ✨ Características Avanzadas

- **Segmentación de clientes**:
  - **Explorer** (20%): Navega mucho, baja conversión
  - **Buyer** (35%): Compra directa, alta conversión
  - **Researcher** (25%): Investiga mucho antes de comprar
  - **Window Shopper** (20%): Solo navega, muy baja conversión

- **Tendencias del mercado dinámicas**:
  - Demanda variable por categoría
  - Precios dinámicos basados en competencia
  - Factores estacionales automáticos

- **Journey del cliente completo**:
  - Sesiones con múltiples interacciones
  - Probabilidad de conversión basada en comportamiento
  - Análisis de abandono de carrito
  - Métricas de sesión en tiempo real

- **Pricing dinámico**:
  - Precios que cambian según demanda
  - Competencia simulada
  - Factores estacionales

### 🚀 Cómo Usar

```bash
# Opción 1: Script de inicio automático
cd nico-scripts
./start.sh

# Opción 2: Manual
source venv/bin/activate
python nico-scripts/advanced_behavior_simulator.py
```

## 📊 Real-time Monitor

**Propósito**: Dashboard en tiempo real para monitorear todas las métricas y estadísticas del sistema.

### ✨ Características del Monitor

- **Métricas en tiempo real**:
  - Transacciones por hora
  - Ingresos y AOV
  - Sesiones y conversiones
  - Eventos de comportamiento

- **Visualizaciones interactivas**:
  - Gráficos de torta por categoría
  - Top productos trending
  - Actividad temporal
  - Stream de eventos en vivo

- **KPIs importantes**:
  - Tasa de conversión
  - Tasa de abandono de carrito
  - Tasa de rebote
  - Duración promedio de sesión

### 🚀 Cómo Usar

```bash
# Opción 1: Script de inicio automático
cd nico-scripts
./start.sh

# Opción 2: Manual
source venv/bin/activate
python nico-scripts/realtime_monitor.py
```

El dashboard estará disponible en: **http://localhost:8503**

## 🛠️ Configuración Requerida

### Prerrequisitos

1. **Docker Compose ejecutándose**:
   ```bash
   docker-compose up -d
   ```

2. **Entorno virtual Python**:
   ```bash
   # Crear entorno virtual
   python3 -m venv venv
   
   # Activar entorno virtual
   source venv/bin/activate
   
   # Instalar dependencias
   pip install -r requirements.txt
   pip install numpy plotly streamlit
   ```

3. **Datos iniciales** (opcional):
   ```bash
   python fake-data.py
   ```

### 🔧 Configuración de Base de Datos

Los scripts asumen las siguientes configuraciones:

- **PostgreSQL Main**: `localhost:5432` (instashop)
- **PostgreSQL DWH**: `localhost:5436` (dwh_db)
- **PostgreSQL CRM**: `localhost:5433` (crm_db)

## 📈 Patrones de Datos Generados

### 🕐 Patrones Temporales

- **Horas pico**: 8-9am, 12-1pm, 6-8pm, 8-10pm
- **Horas tranquilas**: 2-5am
- **Fin de semana**: +30% actividad
- **Estacionalidad**: Black Friday (+100%), Navidad (+130%)

### 👥 Perfiles de Clientes

| Perfil | Frecuencia | AOV | Comportamiento |
|--------|------------|-----|-----------------|
| High Value | 15% | $200-800 | Compra directa, productos premium |
| Regular | 60% | $50-200 | Navegación moderada, conversión media |
| Bargain Hunter | 25% | $10-80 | Muchas búsquedas, busca ofertas |

### 🛍️ Eventos Generados

1. **Transacciones** (30% de eventos):
   - Productos realistas con precios dinámicos
   - Métodos de pago según perfil
   - Estados: completed (85%), pending (10%), failed (5%)

2. **Comportamiento** (70% de eventos):
   - page_view (40%)
   - product_view (25%)
   - search (15%)
   - add_to_cart (15%)
   - remove_from_cart (5%)

## 🎯 Casos de Uso

### 📊 Para Análisis de Negocio

1. **Ejecutar generador básico** para datos de transacciones
2. **Usar monitor** para ver métricas en tiempo real
3. **Analizar patrones** de comportamiento y conversión

### 🧪 Para Testing de Sistemas

1. **Ejecutar simulador avanzado** para carga realista
2. **Monitorear performance** de bases de datos
3. **Probar escalabilidad** del pipeline Kafka-Spark

### 📈 Para Desarrollo de ML

1. **Generar datos históricos** con patrones realistas
2. **Crear features** basadas en comportamiento
3. **Entrenar modelos** de predicción de conversión

## 🔧 Personalización

### Modificar Patrones de Comportamiento

Edita las siguientes secciones en los scripts:

```python
# En realistic_data_generator.py
self.behavior_patterns = {
    'hourly_activity': {
        8: 0.15,  # Actividad a las 8am
        12: 0.25, # Actividad al mediodía
        # ... más horas
    }
}

# En advanced_behavior_simulator.py
self.behavior_patterns['customer_segments'] = {
    'custom_segment': {
        'frequency': 0.10,
        'conversion_rate': 0.30,
        # ... más configuraciones
    }
}
```

### Agregar Nuevas Categorías de Productos

```python
# En ambos scripts
self.product_catalog['Nueva_Categoria'] = {
    'products': [
        ('Producto 1', 99.99, 'Descripción'),
        ('Producto 2', 149.99, 'Descripción'),
    ],
    'seasonality': {'peak_months': [6, 7], 'low_months': [1, 2]},
    'price_volatility': 0.10
}
```

## 📊 Métricas Disponibles

### 🎯 Métricas de Transacciones
- Total de transacciones por hora
- Ingresos totales y promedio por orden
- Tasa de transacciones completadas vs fallidas
- Distribución por método de pago

### 👥 Métricas de Comportamiento
- Sesiones activas y completadas
- Tasa de conversión por segmento
- Abandono de carrito por categoría
- Duración promedio de sesión

### 🛍️ Métricas de Productos
- Productos más vendidos
- Rendimiento por categoría
- Precios dinámicos en tiempo real
- Rotación de inventario

## 🚨 Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**:
   ```bash
   # Verificar que Docker esté ejecutándose
   docker-compose ps
   
   # Verificar conectividad
   docker-compose exec postgres psql -U insta -d instashop -c "SELECT 1;"
   ```

2. **Scripts no generan datos**:
   ```bash
   # Verificar logs
   tail -f nico-scripts/data_generator.log
   tail -f nico-scripts/behavior_simulator.log
   ```

3. **Monitor no muestra datos**:
   ```bash
   # Verificar que haya datos en DWH
   docker-compose exec dwh_db psql -U dwh -d dwh_db -c "SELECT COUNT(*) FROM realtime_events;"
   ```

### Logs y Debugging

Los scripts generan logs detallados en:
- `nico-scripts/data_generator.log`
- `nico-scripts/behavior_simulator.log`

## 🎯 Próximos Pasos

### Mejoras Planificadas

- [ ] **Machine Learning**: Modelos predictivos de conversión
- [ ] **A/B Testing**: Simulación de tests A/B
- [ ] **Personalización**: Recomendaciones basadas en comportamiento
- [ ] **Alertas**: Notificaciones automáticas de anomalías
- [ ] **Exportación**: Reportes en PDF/Excel

### Integración con Sistemas Externos

- [ ] **APIs REST**: Endpoints para integración
- [ ] **Webhooks**: Notificaciones en tiempo real
- [ ] **Slack/Teams**: Alertas en canales de comunicación
- [ ] **Email**: Reportes automáticos por email

---

**🚀 InstaShop Data Generation Suite** - Generando datos realistas para análisis avanzado

Desarrollado con ❤️ para el proyecto InstaShop
