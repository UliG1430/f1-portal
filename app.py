import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from scripts.data_processing import cargar_datos, filtrar_datos_por_año, limpiar_datos, categorizar_temperatura
from scripts.metrics import calcular_coeficiente_lluvia

# Configuración de la página
st.set_page_config(page_title="F1 Data Dashboard", layout="wide")

# Cargar datos
df = cargar_datos()

# Título de la app
st.title("📊 Dashboard de F1 con Datos Climáticos")

# Filtros
st.sidebar.header("Filtros")
año_seleccionado = st.sidebar.selectbox("Seleccioná un año", sorted(df["year"].unique(), reverse=True))
df_filtrado = filtrar_datos_por_año(df, año_seleccionado)

# Limpiar y categorizar datos
df_filtrado = limpiar_datos(df_filtrado)
df_filtrado = categorizar_temperatura(df_filtrado)

# Mostrar datos filtrados
st.subheader(f"Datos del año {año_seleccionado}")
st.dataframe(df_filtrado.head())

# Calcular coeficiente de rendimiento en lluvia
df_pilotos_lluvia = calcular_coeficiente_lluvia(df_filtrado)

# Mostrar los mejores pilotos en lluvia
st.subheader("🏆 Mejores Pilotos en Condiciones de Lluvia")
st.dataframe(df_pilotos_lluvia)

# Gráfico de mejores pilotos en lluvia
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_pilotos_lluvia.head(10), x="CRL", y="surname", palette="Blues_r", ax=ax)
ax.set_title("Top 10 Pilotos con Mejor Rendimiento en Lluvia", fontsize=14)
ax.set_xlabel("Coeficiente de Rendimiento en Lluvia (CRL)")
ax.set_ylabel("Piloto")
st.pyplot(fig)
