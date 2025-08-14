# prueba-tecnica-ingeniero-datos

## Ejercicio 3: Identificación de Rachas en Niveles de Deuda
## ⚙️ Instrucciones de Ejecución

Para ejecutar este proyecto, siga los pasos detallados a continuación:

### 1. Descarga del proyecto
- Descargue la carpeta **`Ejercicio 3`**, que contiene los scripts SQL y los archivos CSV requeridos.

### 2. Configuración de rutas en el script
- Abra el script **`crear y cargar tablas.sql`**.
- Localice las siguientes líneas:
  - **Línea 15:** corresponde a la ruta del archivo **`historia.csv`**.
  - **Línea 25:** corresponde a la ruta del archivo **`retiros.csv`**.
- Reemplace dichas rutas por la ubicación real donde se encuentran los archivos CSV dentro de su entorno local.

> **Nota:** Ambos archivos (`historia.csv` y `retiros.csv`) se encuentran incluidos en la carpeta **`Ejercicio 3`**.

### 3. Ejecución de los scripts en orden
Ejecute los scripts en el siguiente orden para asegurar la correcta creación y carga de los datos:

1. **`crear base de datos.sql`**  
   Crea la base de datos donde se almacenará la información.

2. **`crear y cargar tablas.sql`**  
   Crea las tablas `historia` y `retiros` e inserta los datos desde los archivos CSV.

3. **`query principal.sql`**  
   Ejecuta la consulta que implementa la lógica solicitada en el ejercicio, generando el resultado final.

---

Al finalizar estos pasos, obtendrá la salida esperada con la identificación del cliente, la longitud de la racha, la fecha final y el nivel correspondiente.


---

## 📌 Objetivo

Este proyecto resuelve un problema de análisis de rachas consecutivas de clientes según sus niveles de deuda, utilizando datos históricos cargados en **MySQL**.
Tiene como objetivo determinar, para cada cliente, la racha más larga de meses consecutivos dentro de un mismo nivel de deuda, bajo las siguientes reglas:

1. **Clasificación por niveles de deuda:**
   - **N0:** Saldo ≥ 0 y < 300,000
   - **N1:** Saldo ≥ 300,000 y < 1,000,000
   - **N2:** Saldo ≥ 1,000,000 y < 3,000,000
   - **N3:** Saldo ≥ 3,000,000 y < 5,000,000
   - **N4:** Saldo ≥ 5,000,000

2. **Tratamiento de datos faltantes:**
   - Si un cliente no tiene registro en un mes después de su primera aparición, se asume **saldo = 0 (N0)**.
   - Si el cliente tiene una **fecha de retiro**, no se consideran meses posteriores a esa fecha.

3. **Restricciones adicionales:**
   - Se analiza la información **hasta una fecha específica (`fecha_base`)**.
   - Solo se seleccionan rachas con **al menos `n` meses consecutivos**.
   - Si un cliente tiene varias rachas que cumplen, se escoge:
     - La **más larga**.
     - En caso de empate, la que **termina más cerca de la `fecha_base`**.

---

## 🔍 Enfoque de la Solución

El desarrollo se realizó en varias etapas:

### **1. Normalización de la línea de tiempo**
Se generó una lista continua de meses entre la primera fecha registrada y la fecha_base. Esto permite evaluar incluso los meses donde un cliente no tuvo movimientos.

### **2. Completar datos faltantes**
Cada cliente se combinó con la lista completa de meses:
- Si no había saldo en un mes, se asignó **N0**.
- Se excluyeron los meses posteriores a la fecha de retiro (si existía).

### **3. Clasificación por nivel**
Cada registro se clasificó en uno de los cinco niveles según el saldo.

### **4. Identificación de rachas consecutivas**
- Ordenar los meses por cliente y nivel.
- Agrupar secuencias consecutivas con el mismo nivel.
- Calcular la longitud de cada secuencia.

### **5. Filtrado y selección final**
- Se conservaron solo las rachas con tamaño mayor o igual a `n`.
- Para cada cliente, se eligió la más larga; en caso de empate, la más reciente.

---

## ✅ Resultado Final
Para cada cliente, se obtiene:
- **identificacion:** ID del cliente.
- **racha:** Número de meses consecutivos en el mismo nivel.
- **fecha_fin:** Último mes de la racha.
- **nivel:** Nivel de deuda durante la racha.

---

## 🛠️ Tecnologías Utilizadas
- **Base de datos:** MySQL 8.0


# Ejercicio 4: Procesador de Imágenes HTML a Base64

Una solución completa en Python para convertir automáticamente imágenes locales en archivos HTML a formato Base64, utilizando únicamente librerías built-in y aplicando principios de código limpio.

## 📋 Descripción

Este proyecto procesa archivos HTML de forma recursiva, identifica todas las imágenes locales (tags `<img>`) y las convierte a formato Base64, generando nuevos archivos HTML sin modificar los originales. Es ideal para crear versiones autocontenidas de páginas web que no dependan de archivos de imagen externos.

## 🏗️ Arquitectura

### Diseño Orientado a Objetos

La solución implementa tres clases principales siguiendo los principios SOLID:

- **`FileManager`**: Responsable de la búsqueda y gestión de archivos HTML
- **`ImageProcessor`**: Maneja la conversión de imágenes a Base64
- **`HTMLProcessor`**: Orquesta el procesamiento completo de archivos HTML

### Principios Aplicados

- ✅ **Single Responsibility**: Cada clase tiene una responsabilidad específica
- ✅ **Open/Closed**: Fácil extensión para nuevos formatos de imagen
- ✅ **Dependency Inversion**: Las clases dependen de abstracciones
- ✅ **Clean Code**: Nombres descriptivos, funciones pequeñas, documentación clara

## 🚀 Características

- **Procesamiento recursivo** de directorios y subdirectorios
- **Soporte múltiples formatos**: JPG, PNG, GIF, BMP, WebP, SVG
- **Preservación de archivos originales**
- **Manejo robusto de errores** con reportes detallados
- **Detección automática** de imágenes ya en Base64 y URLs remotas
- **Solo librerías built-in** - Sin dependencias externas

## 📁 Estructura del Proyecto

```
html_processor/
│
├── src/
│   ├── __init__.py          # Inicialización del módulo
│   ├── file_manager.py      # Gestión de archivos
│   ├── image_processor.py   # Conversión Base64
│   └── html_processor.py    # Procesador principal
│
├── tests/
│   └── sample_files/        # Archivos de prueba
│       ├── test1.html
│       ├── test2.html
│       └── images/
│
├── output/                  # Archivos procesados
└──  main.py                  # Punto de entrada
 
```

## 🛠️ Instalación y Uso

### Prerequisitos

- Python 3.6 o superior (solo librerías standard)

### Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <repository-url>
   cd html_processor
   ```

2. **Crear estructura de carpetas** (si es necesario)
   ```bash
   mkdir -p tests/sample_files/images output
   ```

### Uso Básico

1. **Configurar rutas en `main.py`:**
   ```python
   paths_to_process = [
       "ruta/a/directorio",    # Procesará todos los HTML del directorio
       "archivo.html",         # Procesará archivo específico
       "otro/directorio"       # Múltiples rutas soportadas
   ]
   ```

2. **Ejecutar el procesador:**
   ```bash
   python main.py
   ```


## 🎯 Funcionalidades Técnicas

### Conversión Base64

- **Detección automática de tipo MIME** basada en extensión
- **Resolución de rutas relativas** al archivo HTML
- **Validación de archivos** antes del procesamiento
- **Generación de data URLs** completas: `data:image/jpeg;base64,{data}`

### Procesamiento HTML

- **Regex robusto** para encontrar tags `<img>`
- **Preservación de atributos** originales del tag
- **Reemplazo preciso** solo del atributo `src`
- **Detección inteligente** de imágenes ya procesadas

### Manejo de Errores

- **Validación de rutas** antes del procesamiento
- **Manejo de archivos faltantes** con mensajes descriptivos
- **Continuación del procesamiento** ante errores individuales
- **Reporte detallado** de éxitos y fallos




