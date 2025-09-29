# Dashboard de Análisis de Reviews - PayJoy

Dashboard interactivo construido con [Streamlit](https://streamlit.io/) para analizar reviews y feedback de clientes de PayJoy. El sistema se conecta a una base de datos PostgreSQL para visualizar métricas, tendencias y gestionar casos pendientes en tiempo real.

## 🗃️ Estructura de Datos

### Tabla `reviews` (PostgreSQL)

El dashboard se conecta a una base de datos PostgreSQL y lee de la tabla `reviews` que contiene las siguientes columnas:

| Columna              | Tipo sugerido       | Descripción                                                                 |
|----------------------|---------------------|------------------------------------------------------------------------------|
| `id`                 | `INTEGER`           | Identificador único de la review.                                           |
| `tienda`             | `INTEGER`           | Id numérico de la tienda (1=Norte, 2=Sur, 3=Centro).                       |
| `comentario_original`| `TEXT`              | Comentario textual que dejó la persona encuestada.                          |
| `experiencia`        | `INTEGER` (1 a 5)   | Calificación numérica de la experiencia.                                    |
| `sentimiento`        | `TEXT`              | Sentimiento detectado (`Positivo`, `Negativo`, etc.).                       |
| `categoria_principal`| `TEXT`              | Categoría principal asignada al comentario.                                 |
| `categoria_2`        | `TEXT`              | Categoría secundaria (opcional).                                            |
| `categoria_3`        | `TEXT`              | Categoría terciaria (opcional).                                             |
| `menciona_staff`     | `BOOLEAN`           | Indica si se menciona al staff.                                             |
| `sugerencias`        | `TEXT`              | Texto libre con sugerencias adicionales.                                    |
| `contacto`           | `TEXT`              | Dato de contacto compartido (opcional).                                     |
| `fecha`              | `TIMESTAMP`         | Fecha y hora en la que se registró la review.                               |
| `resuelto`           | `BOOLEAN`           | Estado de seguimiento del caso.                                             |

## 📊 Funcionalidades del Dashboard

### 1. **Conexión y carga de datos**
   - Conexión segura a PostgreSQL usando credenciales en `st.secrets`
   - Lectura completa de la tabla `reviews` con SQLAlchemy
   - Mapeo automático de IDs de tienda a nombres legibles (1=Norte, 2=Sur, 3=Centro)
   - Conversión automática de la columna `fecha` a tipo datetime

### 2. **Panel de filtros interactivos**
   - Zona/Tienda (multiselección).
   - Sentimiento (multiselección).
  - Rango de calificación usando un `slider` (1 a 5).
  - Rango de fechas con un selector que trabaja por fecha (ignora la hora).
  - Estado (`Todos`, `Pendientes`, `Resueltos`).
  - Indicador `menciona_staff` (`Todos`, `Sí`, `No`).

   Los filtros se aplican de forma combinada para construir el dataset filtrado.

### 3. **Visualizaciones y análisis**

   - **Vista general**: muestra el NPS estimado, satisfacción promedio y total de reviews.
   - **Tendencia de satisfacción**: línea temporal con el promedio de `experiencia` por fecha.
   - **Distribución de calificaciones**: histograma por puntaje.
   - **Reviews por zona**: tabla con el recuento de comentarios por tienda.
   - **Nube de palabras**: nube generada a partir de `comentario_original` (y otra para `sugerencias` si existieran valores).
   - **Comparativa entre tiendas**: barras con el promedio de experiencia por tienda.
   - **Temas más mencionados**: barras y tablas separadas para sentimientos positivos y negativos. Se toman las columnas `categoria_principal`, `categoria_2` y `categoria_3`, se normalizan y se cuentan ocurrencias.
   - **Timeline interactivo**: scatter + líneas para explorar cada comentario en el tiempo.
   - **Alertas y acciones**: lista las reviews con `resuelto = False`. Cada tarjeta muestra datos clave y cuenta con un botón **"Marcar como Resuelto"** que:
     1. Ejecuta `UPDATE reviews SET resuelto = true WHERE id = :id` usando SQLAlchemy.
     2. Refresca la vista (`st.rerun()`).
     3. Muestra un error si la operación falla.
   - **Exportar datos**: botón para descargar el DataFrame filtrado en formato Excel.

## 🚀 Configuración y Ejecución

### Prerrequisitos
- Python 3.8+
- Base de datos PostgreSQL con tabla `reviews`
- Credenciales de base de datos configuradas

### Instalación

1. Crea y activa un entorno virtual (recomendado):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Instala dependencias:

```powershell
pip install -r requirements.txt
```

3. Configura las credenciales de base de datos en `.streamlit/secrets.toml`:

```toml
DB_USER = "tu_usuario"
DB_PASS = "tu_contraseña"
DB_HOST = "tu_host"
DB_PORT = "5432"
```

4. Ejecuta el dashboard:

```powershell
streamlit run dashboard_demo.py
```

El servidor quedará disponible en <http://localhost:8501> (o el puerto que indique Streamlit).

## ⚙️ Configuración Avanzada

### Variables de configuración:
- **`REFRESH_INTERVAL_SECONDS`**: Intervalo de auto-refresh en segundos (default: 60)
- **`tienda_map`**: Mapeo de IDs numéricos a nombres de tiendas
- **Credenciales**: Almacenadas de forma segura en `st.secrets`

### Personalización:
- **Mapeo de tiendas**: Modifica el diccionario `tienda_map` en el código para ajustar nombres
- **Filtros adicionales**: Agrega nuevos filtros siguiendo la estructura existente
- **Visualizaciones**: Personaliza gráficos usando Altair y Matplotlib
- **Autorefresh**: Ajusta o deshabilita modificando `REFRESH_INTERVAL_SECONDS`

### Funciones principales:
- **`obtener_top_categorias()`**: Extrae las categorías más mencionadas por sentimiento
- **Conexión DB**: Manejo seguro de conexiones PostgreSQL con SQLAlchemy
- **Filtrado dinámico**: Sistema de filtros que se aplican en tiempo real

## 🔧 Características técnicas

- **Framework**: Streamlit para interfaz web
- **Base de datos**: PostgreSQL con SQLAlchemy ORM
- **Visualizaciones**: Altair (gráficos interactivos) y Matplotlib (nubes de palabras)
- **Auto-refresh**: Actualización automática cada 60 segundos (opcional)
- **Export**: Descarga de datos filtrados en formato Excel
- **Responsivo**: Layout adaptativo para diferentes tamaños de pantalla
