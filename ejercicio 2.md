# Ejercicio 2: Sistema de KPIs y Veeduría de Calidad de Datos

## Problema
Crear un mecanismo/herramienta para hacer veeduría de la calidad de datos y trazabilidad del dataset de números telefónicos, proporcionando KPIs accionables para equipos de negocio.

## Arquitectura de la Solución

### Componentes del Sistema
```
[Dataset Teléfonos] → [Data Quality Engine] → [Metrics Store] → [Dashboard KPIs]
        ↓                      ↓                    ↓              ↓
   Azure Synapse        Great Expectations    Azure SQL DB    Power BI
        ↓                      ↓                    ↓              ↓
   [Data Lineage] → [Audit & Monitoring] → [Alert System] → [Self-Service]
        ↓                      ↓                    ↓              ↓
   Azure Purview        Azure Monitor        Logic Apps    Power BI Service
```

## Data Quality Engine

### 1. Dimensiones de Calidad Medidas

| Dimensión | Definición | Métrica Clave | Frecuencia |
|-----------|------------|---------------|------------|
| **Completitud** | % de registros con todos los campos requeridos | `complete_records / total_records` | Diaria |
| **Validez** | % de datos que cumplen reglas de negocio | `valid_records / total_records` | Diaria |
| **Consistencia** | % de datos coherentes entre sistemas | `consistent_records / total_records` | Diaria |
| **Unicidad** | % de registros únicos sin duplicados | `unique_records / total_records` | Diaria |
| **Actualidad** | % de datos actualizados en período definido | `recent_records / total_records` | Semanal |
| **Precisión** | % de datos verificados como correctos | `verified_records / total_records` | Mensual |

### 2. Reglas de Calidad Implementadas

```python
# Azure Synapse Stored Procedures para Quality Checks
def data_quality_rules():
    return {
        "completeness_checks": [
            "customer_id IS NOT NULL",
            "phone_number IS NOT NULL", 
            "country_code IS NOT NULL"
        ],
        "validity_checks": [
            "phone_number LIKE '+%'",
            "LEN(phone_number) BETWEEN 8 AND 15",
            "country_code IN (SELECT code FROM valid_countries)"
        ],
        "consistency_checks": [
            "carrier IS NOT NULL WHEN phone_type = 'mobile'",
            "is_primary = 1 COUNT <= 1 PER customer_id"
        ],
        "business_rules": [
            "verification_date <= GETDATE()",
            "COUNT(phone_number) <= 3 PER customer_id"
        ]
    }
```

## KPIs para Equipos de Negocio

### 1. KPIs Operacionales

#### Dashboard de Salud del Dataset
| KPI | Fórmula | Target | Vista |
|-----|---------|---------|--------|
| **Completitud General** | `(Registros Completos / Total) × 100` | >95% | Gauge Chart |
| **Tasa de Verificación** | `(Números Verificados / Total) × 100` | >80% | Line Chart |
| **Duplicados Detectados** | `Count(Duplicados)` | <100/día | Card |
| **Tiempo de Actualización** | `AVG(current_time - updated_at)` | <24h | KPI Card |
| **Cobertura Geográfica** | `COUNT(DISTINCT country_code)` | Tracking | Map Visual |

#### Dashboard de Fuentes de Datos
| KPI | Descripción | Visualización |
|-----|-------------|---------------|
| **Contribución por Fuente** | `Records per Source / Total` | Donut Chart |
| **Calidad por Fuente** | `Quality Score per Source` | Stacked Bar |
| **Latencia de Ingesta** | `Processing Time per Source` | Column Chart |
| **Errores por Fuente** | `Error Count per Source` | Clustered Column |

### 2. KPIs de Negocio

#### Dashboard Ejecutivo
```sql
-- KPIs calculados en Azure Synapse
WITH phone_metrics AS (
  SELECT 
    COUNT(*) as total_customers_with_phone,
    COUNT(CASE WHEN phone_type = 'mobile' THEN 1 END) as mobile_customers,
    COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_customers,
    COUNT(DISTINCT country_code) as countries_covered,
    AVG(data_quality_score) as avg_quality_score
  FROM customer_phone_numbers 
  WHERE is_active = 1
)
SELECT * FROM phone_metrics;
```

| KPI | Propósito de Negocio | Meta |
|-----|---------------------|------|
| **Penetración Móvil** | `Clientes con Móvil / Total Clientes` | >85% |
| **Efectividad de Campañas** | `Números Verificados / Números Totales` | >75% |
| **Cobertura Internacional** | `Países Únicos` | Tracking |
| **Score de Contactabilidad** | `AVG(Quality Score × Verification Status)` | >0.8 |
| **Tasa de Abandono** | `Números Inactivos Últimos 90 días` | <5% |

### 3. KPIs Técnicos para Data Engineers

#### Dashboard de Data Pipeline
| Métrica | Descripción | Alerta |
|---------|-------------|---------|
| **Pipeline Success Rate** | `Pipelines Exitosos / Total Pipelines` | <95% |
| **Data Freshness** | `Tiempo desde última actualización` | >4h |
| **Processing Throughput** | `Registros procesados / minuto` | <1000/min |
| **Error Rate** | `Registros fallidos / Total procesados` | >2% |
| **Cost per Record** | `Costo Azure / Registros procesados` | Tracking |

## Trazabilidad del Dato (Data Lineage)

### 1. Azure Purview Integration

```json
{
  "data_lineage": {
    "source_systems": [
      {
        "name": "CRM_Database",
        "type": "SQL_Server",
        "tables": ["customers", "contacts"],
        "update_frequency": "real_time"
      },
      {
        "name": "Sales_API",
        "type": "REST_API", 
        "endpoints": ["/customers", "/orders"],
        "update_frequency": "hourly"
      }
    ],
    "transformation_steps": [
      {
        "step": "normalization",
        "tool": "Azure_Synapse_Spark",
        "notebook": "phone_normalization.ipynb"
      },
      {
        "step": "validation",
        "tool": "Great_Expectations",
        "suite": "phone_validation_suite"
      }
    ],
    "destination": {
      "name": "customer_phone_numbers",
      "type": "Azure_Synapse_DW",
      "schema": "dbo"
    }
  }
}
```

### 2. Audit Trail Automático

```sql
-- Tabla de Auditoría automática
CREATE TABLE data_lineage_audit (
    audit_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    record_id NVARCHAR(50),
    source_system NVARCHAR(50),
    transformation_applied NVARCHAR(100),
    quality_score_before DECIMAL(3,2),
    quality_score_after DECIMAL(3,2),
    processed_timestamp DATETIME2 DEFAULT GETDATE(),
    processed_by NVARCHAR(50)
);
```

## Herramientas de Self-Service para Negocio

### 1. Power BI Self-Service Dashboard

#### Estructura del Dashboard
```
📊 Dashboard Principal
├── 📈 Resumen Ejecutivo
│   ├── KPIs principales (cards)
│   ├── Tendencias (line charts)  
│   └── Alertas críticas
├── 🔍 Análisis Detallado
│   ├── Drill-down por dimensiones
│   ├── Filtros interactivos
│   └── Comparativos temporales
├── 📋 Calidad de Datos
│   ├── Scores por dimensión
│   ├── Reglas fallidas
│   └── Tendencias de mejora
└── 🌍 Vista Geográfica
    ├── Distribución por países
    ├── Calidad por región
    └── Cobertura de campañas
```

#### Funcionalidades Self-Service
- **Filtros Dinámicos**: Por fecha, región, fuente, calidad
- **Drill-Down**: De KPIs agregados a registros individuales
- **Alertas Personalizadas**: Configurables por usuario
- **Exportación**: PDF, Excel, PowerPoint
- **Suscripciones**: Reportes automáticos por email

### 2. Portal de Data Quality

```html
<!-- Mockup del Portal Web -->
<div class="data-quality-portal">
  <header>
    <h1>📞 Phone Data Quality Portal</h1>
    <div class="health-indicator">
      <span class="status-green">🟢 Dataset Health: 94%</span>
    </div>
  </header>
  
  <section class="kpi-cards">
    <div class="kpi-card completeness">
      <h3>Completitud</h3>
      <div class="metric">96.2%</div>
      <div class="trend">↗️ +1.2% vs yesterday</div>
    </div>
    <!-- More KPI cards... -->
  </section>
  
  <section class="interactive-charts">
    <!-- Power BI Embedded components -->
  </section>
</div>
```

## Sistema de Alertas y Monitoreo

### 1. Alertas Automáticas (Azure Logic Apps)

```json
{
  "alert_rules": [
    {
      "name": "Data_Quality_Degradation",
      "condition": "overall_quality_score < 0.90",
      "frequency": "15_minutes",
      "recipients": ["data-team@company.com"],
      "severity": "high"
    },
    {
      "name": "Pipeline_Failure", 
      "condition": "pipeline_status = 'failed'",
      "frequency": "immediate",
      "recipients": ["data-engineers@company.com", "on-call"],
      "severity": "critical"
    },
    {
      "name": "Anomaly_Detection",
      "condition": "record_volume > 1.5 * avg_daily_volume",
      "frequency": "hourly",
      "recipients": ["business-analysts@company.com"],
      "severity": "medium"
    }
  ]
}
```

### 2. Canales de Notificación
- **Email**: Reportes diarios y alertas críticas
- **Teams**: Notificaciones en tiempo real
- **SMS**: Solo para alertas críticas (pipeline failures)
- **Dashboard**: Indicadores visuales en tiempo real

## Implementación Técnica

### 1. Stack Tecnológico

| Componente | Herramienta | Propósito |
|------------|-------------|-----------|
| **Data Quality Engine** | Great Expectations + Azure Synapse | Validación y métricas |
| **Metrics Storage** | Azure SQL Database | Almacén de KPIs históricos |
| **Dashboards** | Power BI Premium | Visualización self-service |
| **Data Lineage** | Azure Purview | Trazabilidad y governance |
| **Alerting** | Azure Monitor + Logic Apps | Notificaciones automáticas |
| **API Layer** | Azure API Management | Acceso programático a métricas |
| **Scheduling** | Azure Data Factory | Ejecución de quality checks |

### 2. Arquitectura de Datos

```sql
-- Schema para métricas de calidad
CREATE SCHEMA data_quality;

-- Tabla principal de métricas
CREATE TABLE data_quality.daily_metrics (
    metric_date DATE,
    metric_name NVARCHAR(50),
    metric_value DECIMAL(10,4),
    target_value DECIMAL(10,4),
    dimension_name NVARCHAR(50),
    dimension_value NVARCHAR(100),
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Vista para KPIs de negocio
CREATE VIEW data_quality.business_kpis AS
SELECT 
    metric_date,
    SUM(CASE WHEN metric_name = 'completeness' THEN metric_value END) as completeness_pct,
    SUM(CASE WHEN metric_name = 'validity' THEN metric_value END) as validity_pct,
    AVG(CASE WHEN metric_name = 'quality_score' THEN metric_value END) as avg_quality_score
FROM data_quality.daily_metrics
GROUP BY metric_date;
```

## Casos de Uso por Stakeholder

### 1. Chief Data Officer (CDO)
**Dashboard**: Vista ejecutiva
**KPIs clave**:
- ROI de iniciativas de calidad de datos
- Compliance con regulaciones
- Madurez de data governance

### 2. Marketing Manager
**Dashboard**: Efectividad de campañas
**KPIs clave**:
- Tasa de contactabilidad por canal
- Cobertura geográfica
- Efectividad por tipo de teléfono

### 3. Data Engineer
**Dashboard**: Salud técnica del pipeline  
**KPIs clave**:
- Performance del pipeline
- Costos de procesamiento
- Alertas técnicas

### 4. Customer Service Manager
**Dashboard**: Calidad de contacto
**KPIs clave**:
- Números verificados vs. no verificados
- Tasa de éxito de llamadas
- Actualidad de información

## Roadmap de Implementación

### Fase 1 (Semanas 1-2): Fundación
- ✅ Setup de Great Expectations con Azure Synapse
- ✅ Creación de schema de métricas
- ✅ Dashboard básico en Power BI

### Fase 2 (Semanas 3-4): KPIs Core
- ✅ Implementación de 6 dimensiones de calidad
- ✅ Automatización de cálculo de métricas
- ✅ Sistema básico de alertas

### Fase 3 (Semanas 5-6): Self-Service
- ✅ Portal web para usuarios de negocio
- ✅ Dashboards interactivos avanzados
- ✅ Azure Purview para data lineage

### Fase 4 (Semanas 7-8): Optimización
- ✅ Machine Learning para anomaly detection
- ✅ Alertas inteligentes
- ✅ Métricas predictivas

## ROI y Beneficios

### Beneficios Cuantificables
- **Reducción de campañas fallidas**: 30% menos números inválidos
- **Mejora en customer satisfaction**: +15% en encuestas post-contacto  
- **Ahorro en costos de limpieza**: -40% tiempo manual de validación
- **Compliance**: 100% cumplimiento con regulaciones de datos

### Beneficios Intangibles
- Mayor confianza en los datos
- Decisiones más rápidas y precisas
- Cultura data-driven en la organización
- Proactividad vs. reactividad en calidad

## Costos Estimados

| Componente | Costo Mensual (USD) |
|------------|---------------------|
| Power BI Premium | $20/usuario (~$400 para 20 usuarios) |
| Azure Synapse Analytics | $200 (queries de quality checks) |
| Azure SQL Database | $100 (metrics storage) |
| Azure Purview | $150 (data lineage) |
| Azure Monitor + Logic Apps | $50 (alerting) |
| **Total** | **~$900/mes** |

**ROI estimado**: 300% en el primer año considerando ahorro en campañas y mejora en customer experience.

---

Esta solución proporciona visibilidad completa sobre la calidad del dataset de teléfonos, empodera a los equipos de negocio con self-service analytics, y establece un framework escalable para governance de datos.