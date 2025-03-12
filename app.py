import streamlit as st
import pandas as pd
import plotly.express as px
from scripts.data_processing import load_data, filter_data

# Configuración de la página en Streamlit
st.set_page_config(page_title="F1 Dashboard", layout="wide")

# Cargar los datos limpios
df = load_data()

# 🔍 Filtrar solo carreras principales (excluir Qualys y Sprint Races si existen en la base de datos)
if "eventType" in df.columns:
    df = df[df["eventType"] == "Race"]
elif "statusId" in df.columns:
    df = df[df["statusId"] != "Qualifying"]  # Ajustar según la estructura del dataset

# 📌 Barra lateral con filtros
st.sidebar.header("📌 Filtros de Carrera")
selected_year = st.sidebar.selectbox("📅 Seleccionar Año", sorted(df["year"].unique(), reverse=True))
selected_team = st.sidebar.selectbox("🛠️ Seleccionar Equipo", ["Todos"] + sorted(df["constructor_name"].unique()))

# Aplicar filtros
df_filtered = filter_data(df, year=selected_year, team=selected_team)

# ===============================================
# 🏁 **TÍTULO PRINCIPAL**
# ===============================================
st.title(f"🏎️ Análisis de Fórmula 1 - Temporada {selected_year}")
st.markdown("📊 Este dashboard analiza el rendimiento de los pilotos y equipos en diferentes condiciones climáticas.")

# ===============================================
# 📌 **SECCIÓN 1: Análisis Generales**
# ===============================================

## 📊 **1. Puntos Totales por Piloto**
st.subheader("🏆 Puntos Totales por Piloto en la Temporada")
st.markdown("🔹 **Este gráfico muestra los pilotos con más puntos en la temporada seleccionada, sin importar el clima.**")

df_pilots_total = df_filtered.groupby("driver_surname")["points"].sum().reset_index()
fig = px.bar(df_pilots_total.sort_values("points", ascending=False), 
             x="driver_surname", y="points", color="points",
             labels={"driver_surname": "Piloto", "points": "Puntos Totales"},
             title="🏎️ Ranking de Pilotos en la Temporada",
             color_continuous_scale="Blues")

st.plotly_chart(fig, use_container_width=True)


## 📊 **2. Comparación de Equipos (Constructores)**
st.subheader("🏎️ Comparación de Equipos en la Temporada")
st.markdown("🔹 **Este gráfico muestra el total de puntos acumulados por cada equipo en la temporada seleccionada.**")

df_teams_total = df_filtered.groupby("constructor_name")["points"].sum().reset_index()
fig = px.bar(df_teams_total.sort_values("points", ascending=False), 
             x="constructor_name", y="points", color="points",
             labels={"constructor_name": "Equipo", "points": "Puntos Totales"},
             title="📊 Ranking de Equipos en la Temporada",
             color_continuous_scale="Blues")

st.plotly_chart(fig, use_container_width=True)


# ===============================================
# 🌧️ **SECCIÓN 2: Análisis de Rendimiento en Lluvia**
# ===============================================

## 📊 **3. Ranking de Pilotos en Lluvia (Rain Performance Index - RPI)**
## 📊 **Ranking de Pilotos con Mayor Diferencia de Rendimiento en Lluvia**
st.subheader("🌧️ Pilotos con Mayor Diferencia de Rendimiento en Lluvia")
st.markdown("🔹 **Este gráfico muestra qué pilotos tienen una mayor diferencia de rendimiento entre seco y mojado.**")

# Calcular promedio de puntos en lluvia y en seco por piloto
df_rain = df_filtered[df_filtered["rainfall"] == True].groupby("driver_surname")["points"].mean().reset_index()
df_dry = df_filtered[df_filtered["rainfall"] == False].groupby("driver_surname")["points"].mean().reset_index()

# Fusionar datasets y calcular CDRL
df_rain_dry = df_rain.merge(df_dry, on="driver_surname", suffixes=("_rain", "_dry"))
df_rain_dry["CDRL"] = (df_rain_dry["points_rain"] - df_rain_dry["points_dry"]) / (df_rain_dry["points_dry"] + 1)

# Gráfico de diferencia de rendimiento en lluvia
fig = px.bar(df_rain_dry.sort_values("CDRL", ascending=False), 
             x="driver_surname", y="CDRL", color="CDRL",
             labels={"driver_surname": "Piloto", "CDRL": "Coeficiente de Diferencia de Rendimiento en Lluvia"},
             title="📊 Pilotos con Mayor Diferencia de Rendimiento en Lluvia",
             color_continuous_scale="RdYlBu")

st.plotly_chart(fig, use_container_width=True)


## 📊 **4. Comparación de Puntos en Lluvia vs Seco**
st.subheader("🏆 Comparación de Puntos Promedio en Seco vs Lluvia")
st.markdown("🔹 **Este gráfico muestra la cantidad de puntos promedio que cada piloto gana en seco y en mojado.**")

df_rain_dry_melted = df_rain_dry.melt(id_vars=["driver_surname"], value_vars=["points_rain", "points_dry"],
                                      var_name="Condición", value_name="Puntos Promedio")
df_rain_dry_melted["Condición"] = df_rain_dry_melted["Condición"].map({"points_rain": "Lluvia", "points_dry": "Seco"})

fig = px.bar(df_rain_dry_melted, x="driver_surname", y="Puntos Promedio", color="Condición",
             labels={"driver_surname": "Piloto", "Puntos Promedio": "Puntos Promedio por Carrera"},
             title="📊 Rendimiento de Pilotos en Seco vs Mojado",
             barmode="group",
             color_discrete_map={"Lluvia": "blue", "Seco": "orange"})

st.plotly_chart(fig, use_container_width=True)


## 📊 **5. Equipos con Mejor Rendimiento en Lluvia**
st.subheader("🏎️ Equipos con Mejor Rendimiento en Lluvia")
st.markdown("🔹 **Analizamos qué equipos logran mejores resultados en mojado respecto a seco.**")

df_team_rain = df_filtered[df_filtered["rainfall"] == True].groupby("constructor_name")["points"].mean().reset_index()
df_team_dry = df_filtered[df_filtered["rainfall"] == False].groupby("constructor_name")["points"].mean().reset_index()
df_team_rain_dry = df_team_rain.merge(df_team_dry, on="constructor_name", suffixes=("_rain", "_dry"))
df_team_rain_dry["RPI"] = df_team_rain_dry["points_rain"] / (df_team_rain_dry["points_dry"] + 1)

fig = px.bar(df_team_rain_dry.sort_values("RPI", ascending=False), 
             x="constructor_name", y="RPI", color="RPI",
             labels={"constructor_name": "Equipo", "RPI": "Índice de Rendimiento en Lluvia"},
             title="🌧️ Ranking de Equipos en Lluvia",
             color_continuous_scale="Blues")

st.plotly_chart(fig, use_container_width=True)

# ===============================================
# 🔚 **CONCLUSIÓN FINAL**
# ===============================================
st.markdown("📊 Datos obtenidos de Kaggle y procesados para análisis interactivo.")
