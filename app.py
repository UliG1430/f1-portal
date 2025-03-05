import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="F1 Data Dashboard", layout="wide")

# Cargar el dataset
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/clean/f1_final_dataset.csv")
    return df

df = cargar_datos()

# Título de la app
st.title("📊 Dashboard de F1 con Datos Climáticos")

# Filtros
st.sidebar.header("Filtros")
año_seleccionado = st.sidebar.selectbox("Seleccioná un año", sorted(df["year"].unique(), reverse=True))
df_filtrado = df[df["year"] == año_seleccionado]

# Mostrar datos filtrados
st.subheader(f"Datos del año {año_seleccionado}")
st.dataframe(df_filtrado.head())

st.write("Valores únicos en AirTemp antes de la limpieza:", df_filtrado["AirTemp"].unique())

# Verificar y limpiar datos antes del gráfico
df_filtrado = df_filtrado.dropna(subset=["AirTemp", "fastestLapSpeed"])  # Eliminar filas con valores nulos
df_filtrado["AirTemp"] = pd.to_numeric(df_filtrado["AirTemp"], errors="coerce")  # Convertir a número
df_filtrado["fastestLapSpeed"] = pd.to_numeric(df_filtrado["fastestLapSpeed"], errors="coerce")  # Convertir a número
df_filtrado = df_filtrado.dropna(subset=["AirTemp", "fastestLapSpeed"])  # Volver a eliminar NaN después de la conversión

# Categorizar temperaturas
df_filtrado["Temp_Categoria"] = pd.cut(
    df_filtrado["AirTemp"],
    bins=[-float("inf"), 15, 25, float("inf")],
    labels=["Frío (<15°C)", "Templado (15-25°C)", "Caluroso (>25°C)"]
)

# Asegurar que Temp_Categoria no contenga NaN
df_filtrado["Temp_Categoria"] = df_filtrado["Temp_Categoria"].astype(str).fillna("Desconocido")

# Verificar datos antes de graficar
st.write("Valores únicos en Temp_Categoria después de reemplazar NaN:", df_filtrado["Temp_Categoria"].unique())
st.write("Descripción de fastestLapSpeed:", df_filtrado["fastestLapSpeed"].describe())

# Mejorar gráfico: Relación entre temperatura y velocidad de vuelta más rápida
fig1, ax1 = plt.subplots(figsize=(12, 6))

# Boxplot con colores mejorados
sns.boxplot(data=df_filtrado, x="Temp_Categoria", y="fastestLapSpeed", palette="coolwarm", ax=ax1, width=0.6)

# Swarmplot para distribuir mejor los puntos y hacerlos más visibles
sns.swarmplot(data=df_filtrado, x="Temp_Categoria", y="fastestLapSpeed", color="black", alpha=0.5, size=3, ax=ax1)

# Mejorar etiquetas y títulos
ax1.set_title("Velocidad de Vuelta más Rápida según la Temperatura del Aire", fontsize=14, fontweight="bold")
ax1.set_xlabel("Temperatura del Aire", fontsize=12)
ax1.set_ylabel("Velocidad de Vuelta Más Rápida (km/h)", fontsize=12)

# Mejorar la cuadrícula
ax1.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig1)


# Gráfico: Puntos obtenidos por piloto
fig2 = px.bar(df_filtrado.groupby("surname")["points"].sum().reset_index(),
              x="surname", y="points", title="Puntos Totales por Piloto",
              labels={"surname": "Piloto", "points": "Puntos"},
              color="points", color_continuous_scale="Blues")
st.plotly_chart(fig2)

# Gráfico: Distribución de temperaturas y humedad
fig3, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df_filtrado["AirTemp"], bins=15, kde=True, color="skyblue", ax=ax)
ax.set_title("Distribución de Temperatura en las Carreras", fontsize=14)
ax.set_xlabel("Temperatura del Aire (°C)", fontsize=12)
ax.set_ylabel("Cantidad de Carreras", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.6)
st.pyplot(fig3)
