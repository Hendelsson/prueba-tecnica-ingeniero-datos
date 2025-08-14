# Ejercicio 1: Dataset de Números de Teléfono - Solución Conceptual

## Problema
Diseñar un proceso automatizado con CI/CD para crear, validar y mantener un dataset confiable de números telefónicos de clientes.

## Arquitectura del Pipeline

### 1. Fuentes de Datos
- **CRM Principal**: Base de datos transaccional
- **Sistema de Ventas**: Números de nuevos clientes  
- **Plataforma Web**: Actualizaciones de perfil
- **Call Center**: Verificaciones manuales

### 2. Pipeline ETL

```
[Fuentes] → [Extracción] → [Transformación] → [Validación] → [Carga] → [Dataset Final]
    ↓           ↓              ↓               ↓            ↓
   APIs   Azure Data Factory  Synapse Spark  Great Expectations  Synapse DW
```

**Herramientas:**
- **Orquestación**: Azure Data Factory
- **Procesamiento**: Azure Synapse Analytics + Python
- **Storage**: Azure Data Lake Gen2 (staging) + Azure Synapse (producción)
- **Validación**: Great Expectations + Azure Monitor

## Esquema del Dataset

**Tabla Principal: `customer_phone_numbers`**

| Campo | Tipo | Ejemplo | Validación |
|-------|------|---------|------------|
| `customer_id` | STRING | "CUST_12345" | NOT NULL, FK |
| `phone_number` | STRING | "+573001234567" | Formato E.164 |
| `phone_type` | STRING | "mobile" | mobile/landline/voip |
| `country_code` | STRING | "CO" | ISO 3166-1 |
| `carrier` | STRING | "Claro" | Lista válida |
| `is_primary` | BOOLEAN | true | Uno por cliente |
| `is_verified` | BOOLEAN | true | - |
| `verification_date` | TIMESTAMP | "2024-01-15T10:30:00Z" | - |
| `source_system` | STRING | "crm" | crm/web/sales |
| `data_quality_score` | FLOAT | 0.95 | 0.0 - 1.0 |
| `updated_at` | TIMESTAMP | "2024-01-15T14:22:00Z" | - |
| `is_active` | BOOLEAN | true | - |

## Validación y Calidad de Datos

### Reglas de Validación
1. **Máximo 3 números por cliente**
2. **Un número principal obligatorio**
3. **Coherencia geográfica** (código país vs. perfil cliente)
4. **Números no verificados >90 días → inactivos**

### Métricas de Calidad
| Métrica | Target | Cálculo |
|---------|--------|---------|
| Completitud | >95% | Registros con teléfono / Total |
| Validez | >98% | Números formato válido / Total |
| Unicidad | >99% | Números únicos / Total |
| Actualidad | >90% | Actualizados últimos 6 meses / Total |

## CI/CD Pipeline

### Estructura del Repo
```
phone-dataset-pipeline/
├── azure-pipelines.yml         # CI/CD con Azure DevOps
├── arm-templates/              # Azure Resource Manager
│   ├── data-factory.json
│   ├── synapse-workspace.json
│   └── storage-account.json
├── src/
│   ├── adf-pipelines/          # Azure Data Factory JSON
│   ├── synapse-notebooks/      # Spark notebooks
│   └── validation/             # Great Expectations
├── tests/
├── config/
│   ├── data_quality.yaml
│   └── adf_config.json
└── bicep/                      # Infrastructure as Code (Bicep)
```

### CI Pipeline (Azure DevOps)
```yaml
# azure-pipelines.yml
trigger:
- main
- develop

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Test
  jobs:
  - job: DataValidation
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.9'
    - script: |
        pip install -r requirements.txt
        pytest tests/unit/
      displayName: 'Unit Tests'
    - task: AzureCLI@2
      inputs:
        azureSubscription: 'data-pipeline-service-connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az synapse spark job submit \
            --name phone-validation-test \
            --workspace-name synapse-workspace \
            --spark-pool-name spark-pool
      displayName: 'Data Quality Tests'
```

### CD Pipeline - Entornos
- **Dev**: Deploy automático desde `develop` con Azure DevOps
- **Staging**: Deploy manual con aprobación via Azure DevOps  
- **Prod**: Deploy manual + doble aprobación + Azure Policy compliance

## Proceso de Transformación

### 1. Extracción (Diaria a las 2 AM)
```python
# Azure Data Factory Pipeline
def extract_phone_data():
    # Conectores nativos de ADF
    crm_data = extract_from_sql_server("CRM_DB")
    sales_data = extract_from_rest_api("SALES_API") 
    web_data = extract_from_adls("web_events")
    return merge_sources([crm_data, sales_data, web_data])
```

### 2. Limpieza y Normalización (Azure Synapse Spark)
```python
# Synapse Spark Notebook
def clean_phone_data(raw_data):
    # Normalizar formato a E.164
    df['phone_clean'] = df['phone'].apply(normalize_to_e164)
    
    # Eliminar duplicados
    df = df.drop_duplicates(['customer_id', 'phone_clean'])
    
    # Enriquecer con Azure Cognitive Services
    df = enrich_with_carrier_info(df)
    
    # Calcular score de calidad
    df['quality_score'] = calculate_quality_score(df)
    
    # Guardar en Azure Data Lake Gen2
    df.write.parquet("abfss://container@storage.dfs.core.windows.net/phone_data/")
    
    return df
```

### 3. Validación con Azure Monitor + Great Expectations
```python
# great_expectations + Azure integration
{
  "expectations": [
    {
      "expectation_type": "expect_column_values_to_match_regex",
      "kwargs": {
        "column": "phone_number",
        "regex": "^\\+[1-9]\\d{1,14}$"
      }
    },
    {
      "expectation_type": "expect_column_values_to_be_unique",
      "kwargs": {"column": "phone_number"}
    }
  ],
  "azure_integration": {
    "log_analytics_workspace": "phone-validation-logs",
    "alert_action_group": "data-quality-alerts"
  }
}
```

## Monitoreo y Alertas

### Dashboard (Azure Monitor + Power BI)
- **Estado del pipeline**: Success/Fail por día (Azure Data Factory monitoring)
- **Métricas de calidad**: Tendencias semanales (Power BI dashboard)
- **Volumen de datos**: Registros procesados (Azure Monitor metrics)
- **Latencia**: Tiempo de procesamiento (Application Insights)

### Alertas (Teams/Email via Azure Monitor)
- Pipeline fallido (Azure Data Factory alerts)
- Calidad de datos < umbral (custom Azure Monitor alerts)
- Anomalías en volumen (+/- 20%) (Azure Anomaly Detector)
- Tiempo de procesamiento > 2 horas (Azure Monitor metrics alerts)

## Seguridad y Compliance

### Protección de Datos
- **Encriptación**: Azure Storage encryption + TDE en Synapse
- **Control de acceso**: Azure AD + RBAC + Azure Key Vault
- **Auditoría**: Azure Activity Log + Azure Sentinel
- **Anonimización**: Azure Confidential Computing para dev/test

### GDPR/LGPD
- **Consentimiento**: Azure Cosmos DB para tracking de permisos
- **Derecho al olvido**: Azure Functions para eliminación automática
- **Portabilidad**: Azure API Management para exportar datos del cliente

## Stack Tecnológico

| Componente | Herramienta | Justificación |
|------------|-------------|---------------|
| Orquestación | Azure Data Factory | Conectores nativos + GUI intuitiva |
| Procesamiento | Azure Synapse Analytics | Spark + SQL serverless integrado |
| Data Warehouse | Azure Synapse DW | Performance + integración nativa |
| Data Lake | Azure Data Lake Gen2 | Hierarchical namespace + ACLs |
| CI/CD | Azure DevOps | Integración completa con Azure |
| IaC | ARM Templates + Bicep | Nativo de Azure + type-safe |
| Monitoreo | Azure Monitor + Power BI | Observabilidad nativa |
| Calidad | Great Expectations + Azure Monitor | Testing automatizado + alertas |

## Plan de Implementación

**Fase 1 (Semana 1-2)**: Setup inicial + Pipeline básico  
**Fase 2 (Semana 3-4)**: Validación + Calidad de datos  
**Fase 3 (Semana 5-6)**: Monitoreo + CI/CD completo  
**Fase 4 (Semana 7-8)**: Deploy producción + Documentación  

## Estimación de Costos (Azure - 1M registros)
- **Storage (Data Lake + Synapse)**: ~$350/mes
- **Compute (Synapse Spark + DW)**: ~$400/mes  
- **Data Factory**: ~$100/mes (pipelines + integration runtime)
- **Monitoreo (Monitor + Power BI)**: ~$120/mes
- **Total**: ~$970/mes

## Riesgos Principales
1. **Calidad de datos fuente** → Validaciones exhaustivas + alertas tempranas
2. **Cambios en sistemas origen** → Monitoreo de esquemas + contratos de datos  
3. **Escalabilidad** → Azure Synapse auto-scaling + serverless SQL
4. **Compliance** → Azure Policy + Azure Purview para data governance

