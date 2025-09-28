# Dashboard de Encuestas

Este proyecto expone un tablero interactivo construido con [Streamlit](https://streamlit.io/) para analizar los resultados de encuestas guardadas en una base de datos PostgreSQL. El código principal vive en `dashboard_demo.py` y se conecta a la tabla `reviews` para generar visualizaciones en tiempo real.

## Tabla `reviews`

El tablero espera que la consulta `SELECT * FROM reviews` devuelva las columnas siguientes:

| Columna              | Tipo sugerido       | Descripción                                                                 |
|----------------------|---------------------|------------------------------------------------------------------------------|
| `id`                 | `INTEGER`           | Identificador único de la review.                                           |
| `tienda`             | `INTEGER`           | Id numérico de la tienda (se mapea a Norte/Sur/Centro).                     |
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

## Flujo general del tablero

1. **Carga de datos**
   - Se crea un motor SQLAlchemy con las credenciales definidas en el archivo.
   - Se lee la tabla `reviews` completa y se convierte la columna `fecha` a tipo datetime.
   - Se mapean los valores numéricos de `tienda` a nombres legibles.

2. **Barra lateral de filtros**
   - Zona/Tienda (multiselección).
   - Sentimiento (multiselección).
  - Rango de calificación usando un `slider` (1 a 5).
  - Rango de fechas con un selector que trabaja por fecha (ignora la hora).
  - Estado (`Todos`, `Pendientes`, `Resueltos`).
  - Indicador `menciona_staff` (`Todos`, `Sí`, `No`).

   Los filtros se aplican de forma combinada para construir `df_filtrado`.

3. **Secciones principales**

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

## Ejecución

1. Crea y activa un entorno virtual (opcional pero recomendado):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Instala dependencias:

```powershell
pip install -r requirements.txt
```

3. Ejecuta el tablero:

```powershell
streamlit run dashboard_demo.py
```

El servidor quedará disponible en <http://localhost:8501> (o el puerto que indique Streamlit).

## Personalización

- **Credenciales**: se recomienda mover los valores `DB_USER`, `DB_PASS`, etc. a variables de entorno para evitar exponerlos en el código.
- **Mapeo de tiendas**: ajusta el diccionario `tienda_map` según las tiendas reales.
- **Columnas adicionales**: si la tabla incorpora más variables, puedes agregarlas a los filtros o visualizaciones siguiendo la misma estructura.
- **Temas destacados**: el helper `obtener_top_categorias` recibe una lista de columnas y puede modificarse para incluir nuevas jerarquías o cambiar el `top_n`.
- **Autorefresh**: el tablero usa `streamlit-autorefresh` para recargarse automáticamente cada 60&nbsp;segundos. Ajusta el intervalo modificando `REFRESH_INTERVAL_SECONDS` en `dashboard_demo.py`. Si no deseas este comportamiento, puedes desinstalar la librería o comentar el bloque que llama a `st_autorefresh`.

## Próximos pasos sugeridos

- Añadir autenticación o control de acceso si el tablero se expone públicamente.
- Programar actualizaciones automáticas (por ejemplo via `st.cache_data` o cron jobs) si las encuestas se insertan en tiempo real.
- Incluir métricas adicionales como duración promedio de respuesta, tiempo de resolución o análisis de sentimiento más granular.
