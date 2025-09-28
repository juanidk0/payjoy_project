import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine, text
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# ---------------------------
# Configuración de página
st.set_page_config(layout="wide")
st.title("Dashboard de Encuestas - Datos Reales")

# Autorefresh opcional cada 60 segundos
REFRESH_INTERVAL_SECONDS = 60
if st_autorefresh is not None:
    st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="dashboard_autorefresh")
else:
    st.warning("`streamlit-autorefresh` no está instalado; la recarga automática está deshabilitada.")

# ---------------------------
# Conexión a la base de datos
DB_USER = st.secrets['DB_USER']
DB_PASS = st.secrets['DB_PASS']
DB_HOST = st.secrets['DB_HOST']
DB_PORT = st.secrets['DB_PORT']
DB_NAME = "defaultdb"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Cargar datos de la tabla reviews
df = pd.read_sql("SELECT * FROM reviews", engine)

# ---------------------------
# Mapeo de tiendas si es numérico
tienda_map = {1: "Norte", 2: "Sur", 3: "Centro"}
df['tienda_nombre'] = df['tienda'].map(tienda_map)

# Asegurarnos que 'fecha' sea datetime
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')


def obtener_top_categorias(df_origen: pd.DataFrame, sentimiento: str, columnas: list[str], top_n: int = 5) -> pd.DataFrame:
    df_sentimiento = df_origen[df_origen['sentimiento'] == sentimiento]
    if df_sentimiento.empty:
        return pd.DataFrame(columns=["categoria", "conteo"])

    categorias = pd.concat(
        [df_sentimiento[col] for col in columnas if col in df_sentimiento.columns],
        ignore_index=True
    )
    if categorias.empty:
        return pd.DataFrame(columns=["categoria", "conteo"])

    categorias = categorias.dropna().astype(str).str.strip()
    categorias = categorias[categorias != ""]

    if categorias.empty:
        return pd.DataFrame(columns=["categoria", "conteo"])

    top = categorias.value_counts().reset_index()
    top.columns = ["categoria", "conteo"]
    top["conteo"] = top["conteo"].astype(int)
    return top.head(top_n)

# ---------------------------
# Sidebar: filtros
st.sidebar.header("Filtros")
zonas = df['tienda_nombre'].dropna().unique().tolist()
sentimientos = df['sentimiento'].dropna().unique().tolist()

tienda_filter = st.sidebar.multiselect("Selecciona Zona/Tienda", options=zonas, default=zonas)
sent_filter = st.sidebar.multiselect("Selecciona Sentimiento", options=sentimientos, default=sentimientos)
calif_filter = st.sidebar.slider("Filtrar por Calificación", min_value=1, max_value=5, value=(1,5))

fecha_col = df['fecha'].dropna()
if not fecha_col.empty:
    fecha_min_default = fecha_col.min().date()
    fecha_max_default = fecha_col.max().date()
else:
    today = pd.Timestamp.today().date()
    fecha_min_default = today
    fecha_max_default = today

fecha_seleccion = st.sidebar.date_input("Rango de fechas", value=(fecha_min_default, fecha_max_default))
if isinstance(fecha_seleccion, (list, tuple)) and len(fecha_seleccion) == 2:
    fecha_min, fecha_max = fecha_seleccion
else:
    fecha_min = fecha_seleccion
    fecha_max = fecha_seleccion
estado_filter = st.sidebar.radio("Filtrar por estado", options=["Todos", "Pendientes", "Resueltos"], index=0)
staff_filter = st.sidebar.selectbox("Filtrar por menciona_staff", options=["Todos", "Sí", "No"], index=0)

# ---------------------------
# Filtrado dinámico
df_filtrado = df[
    (df["tienda_nombre"].isin(tienda_filter)) &
    (df["sentimiento"].isin(sent_filter)) &
    (df["experiencia"].between(calif_filter[0], calif_filter[1])) &
    (df["fecha"].dt.date >= fecha_min) &
    (df["fecha"].dt.date <= fecha_max)
]

if estado_filter == "Pendientes":
    df_filtrado = df_filtrado[df_filtrado["resuelto"]==False]
elif estado_filter == "Resueltos":
    df_filtrado = df_filtrado[df_filtrado["resuelto"]==True]

if staff_filter == "Sí":
    df_filtrado = df_filtrado[df_filtrado["menciona_staff"]==True]
elif staff_filter == "No":
    df_filtrado = df_filtrado[df_filtrado["menciona_staff"]==False]

# ---------------------------
# Vista General
st.header("Vista General")
col1, col2, col3 = st.columns(3)
with col1:
    if not df_filtrado.empty:
        nps = df_filtrado['experiencia'].apply(lambda x: 1 if x >= 4 else (-1 if x <= 2 else 0)).mean() * 100
        st.metric("NPS estimado", f"{nps:.1f}%")
    else:
        st.metric("NPS estimado", "N/A")
with col2:
    st.metric("Satisfacción promedio", f"{df_filtrado['experiencia'].mean():.2f}/5" if not df_filtrado.empty else "N/A")
with col3:
    st.metric("Total de reviews", len(df_filtrado))

# ---------------------------
# Gráfico de tendencia
st.subheader("Tendencia de satisfacción (últimos 30 días)")
if not df_filtrado.empty:
    df_trend = df_filtrado.groupby('fecha')['experiencia'].mean().reset_index()
    trend_chart = alt.Chart(df_trend).mark_line(point=True).encode(
        x='fecha:T',
        y='experiencia:Q'
    )
    st.altair_chart(trend_chart, use_container_width=True)
else:
    st.info("No hay datos para mostrar la tendencia.")

# ---------------------------
# Distribución de calificaciones
st.subheader("Distribución de calificaciones")
if not df_filtrado.empty:
    dist_chart = alt.Chart(df_filtrado).mark_bar().encode(
        x='experiencia:O',
        y='count()',
        color='experiencia:O'
    )
    st.altair_chart(dist_chart, use_container_width=True)
else:
    st.info("No hay datos para mostrar la distribución de calificaciones.")

# ---------------------------
# Reviews por tienda
st.subheader("Reviews por zona")
if not df_filtrado.empty:
    tienda_counts = df_filtrado.groupby('tienda_nombre')['comentario_original'].count().reset_index().rename(columns={"comentario_original":"Total Reviews"})
    st.dataframe(tienda_counts)
else:
    st.info("No hay datos para mostrar por tienda.")

# ---------------------------
# Análisis Detallado
st.header("Análisis Detallado")

# Nube de palabras comentarios
st.subheader("Nube de palabras de comentarios")
if not df_filtrado.empty and df_filtrado['comentario_original'].notna().any():
    comentarios_text = " ".join(df_filtrado['comentario_original'].astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(comentarios_text)
    fig, ax = plt.subplots(figsize=(10,4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
else:
    st.info("No hay comentarios para generar la nube de palabras.")


# Comparativa entre tiendas
st.subheader("Comparativa entre tiendas (promedio de experiencia)")
if not df_filtrado.empty:
    df_comp = df_filtrado.groupby('tienda_nombre')['experiencia'].mean().reset_index()
    comp_chart = alt.Chart(df_comp).mark_bar().encode(
        x='tienda_nombre',
        y='experiencia',
        color='tienda_nombre'
    )
    st.altair_chart(comp_chart, use_container_width=True)
else:
    st.info("No hay datos para mostrar comparativa entre tiendas.")

# Temas más mencionados
st.subheader("Temas más mencionados (positivos y negativos)")
if not df_filtrado.empty:
    columnas_categorias = ["categoria_principal", "categoria_2", "categoria_3"]
    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("**Positivos**")
        top_pos = obtener_top_categorias(df_filtrado, "Positivo", columnas_categorias)
        if not top_pos.empty:
            max_pos = int(top_pos['conteo'].max())
            axis_values_pos = list(range(0, max_pos + 1)) or [0]
            chart_pos = alt.Chart(top_pos).mark_bar(color="#2ecc71").encode(
                y=alt.Y('categoria:N', sort='-x', title='Categoría'),
                x=alt.X(
                    'conteo:Q',
                    title='Menciones',
                    axis=alt.Axis(values=axis_values_pos, format='d', tickMinStep=1)
                )
            )
            st.altair_chart(chart_pos.properties(height=220), use_container_width=True)
            st.dataframe(top_pos)
        else:
            st.info("No hay temas positivos en el rango seleccionado.")

    with col_neg:
        st.markdown("**Negativos**")
        top_neg = obtener_top_categorias(df_filtrado, "Negativo", columnas_categorias)
        if not top_neg.empty:
            max_neg = int(top_neg['conteo'].max())
            axis_values_neg = list(range(0, max_neg + 1)) or [0]
            chart_neg = alt.Chart(top_neg).mark_bar(color="#e74c3c").encode(
                y=alt.Y('categoria:N', sort='-x', title='Categoría'),
                x=alt.X(
                    'conteo:Q',
                    title='Menciones',
                    axis=alt.Axis(values=axis_values_neg, format='d', tickMinStep=1)
                )
            )
            st.altair_chart(chart_neg.properties(height=220), use_container_width=True)
            st.dataframe(top_neg)
        else:
            st.info("No hay temas negativos en el rango seleccionado.")
else:
    st.info("No hay datos para analizar los temas mencionados.")

# Timeline interactivo
st.subheader("Timeline de reviews")
if not df_filtrado.empty:
    df_daily = df_filtrado.groupby(["fecha","tienda_nombre"])["experiencia"].mean().reset_index()
    points = alt.Chart(df_filtrado).mark_circle(size=80).encode(
        x="fecha:T",
        y="experiencia:Q",
        color="tienda_nombre:N",
        tooltip=["tienda_nombre","comentario_original","experiencia","sentimiento","menciona_staff","sugerencias"]
    )
    lines = alt.Chart(df_daily).mark_line().encode(
        x="fecha:T",
        y="experiencia:Q",
        color="tienda_nombre:N"
    )
    timeline_chart = (points + lines).interactive()
    st.altair_chart(timeline_chart, use_container_width=True)
else:
    st.info("No hay datos para mostrar timeline de reviews.")

# ---------------------------
# Alertas y Acciones
st.header("Alertas y Acciones")
st.subheader("Reviews pendientes o que requieren seguimiento")
if not df_filtrado.empty:
    for i, row in df_filtrado.iterrows():
        if not row['resuelto']:
            bg_color = "#fee6e6"
            border_color = "#f3b3b3"
            text_color = "#2b2b2b"
            staff_text = "Sí" if row['menciona_staff'] else "No"
            st.markdown(f"""
            <div style='background-color:{bg_color}; color:{text_color}; padding:10px; margin-bottom:5px; border-radius:5px; border:1px solid {border_color};'>
            <strong>{row['tienda_nombre']}</strong> - {row['comentario_original']}<br>
            Experiencia: {row['experiencia']} | Sentimiento: {row['sentimiento']} | 
            Menciona staff: {staff_text} | Resuelto: {row['resuelto']}
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Marcar como Resuelto {i}"):
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE reviews SET resuelto = true WHERE id = :id"),
                            {"id": row["id"]}
                        )
                    df.loc[row.name, 'resuelto'] = True
                    st.rerun()
                except Exception as exc:
                    st.error(f"No se pudo actualizar el estado en la base de datos: {exc}")
else:
    st.info("No hay alertas pendientes.")

# ---------------------------
# Exportar datos
st.subheader("Exportar datos")
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

if not df_filtrado.empty:
    excel_data = to_excel(df_filtrado)
    st.download_button(label='📥 Descargar Excel', data=excel_data, file_name='reviews.xlsx')
else:
    st.info("No hay datos para exportar.")
