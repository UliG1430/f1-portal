import streamlit as st
import pandas as pd
import plotly.express as px
from scripts.data_processing import load_data, filter_data

# ==============================
# 🎨 **CONFIGURACIÓN DE LA PÁGINA**
# ==============================
st.set_page_config(page_title="F1 Dashboard", layout="wide")

# ==============================
# 📥 **CARGAR LOS DATOS**
# ==============================
fact_results, dim_drivers, dim_teams, dim_circuits = load_data()  # ✅ Ahora incluye dim_circuits
df = fact_results  # Solo tomamos la tabla de hechos

# 📌 Filtrar solo carreras principales (excluir Qualys y Sprint Races si existen en la base de datos)
if "eventType" in df.columns:
    df = df[df["eventType"] == "Race"]
elif "statusId" in df.columns:
    df = df[df["statusId"] != "Qualifying"]  # Ajustar según la estructura del dataset

# ==============================
# 📌 **SIDEBAR: FILTROS**
# ==============================
st.sidebar.header("📌 Filtros de Carrera")
selected_year = st.sidebar.selectbox("📅 Seleccionar Año", sorted(df["year"].unique(), reverse=True))
selected_team = st.sidebar.selectbox("🛠️ Seleccionar Equipo", ["Todos"] + sorted(df["constructor_name"].unique()))

# Aplicar filtros correctamente
df_filtered = filter_data(fact_results, year=selected_year, team=selected_team)

# ==============================
# 🏁 **TÍTULO PRINCIPAL**
# ==============================
st.title(f"🏎️ Análisis de Fórmula 1 - Temporada {selected_year}")
st.markdown("📊 Este dashboard analiza el rendimiento de los pilotos y equipos en diferentes condiciones climáticas.")

# ==============================
# 📌 **SECCIÓN 1: ANÁLISIS GENERALES**
# ==============================

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

# ==============================
# 🌧️ **SECCIÓN 2: ANÁLISIS DE RENDIMIENTO EN LLUVIA**
# ==============================

## 📊 **3. Ranking de Pilotos con Mayor Diferencia de Rendimiento en Lluvia**
st.subheader("🌧️ Pilotos con Mayor Diferencia de Rendimiento en Lluvia")
st.markdown("🔹 **Este gráfico muestra qué pilotos tienen una mayor diferencia de rendimiento entre seco y mojado.**")

# Calcular promedio de puntos en lluvia y en seco por piloto
df_rain = df_filtered[df_filtered["rainfall"] == True].groupby("driver_surname")["points"].mean().reset_index()
df_dry = df_filtered[df_filtered["rainfall"] == False].groupby("driver_surname")["points"].mean().reset_index()

# Fusionar datasets y calcular CDRL (Coeficiente de Diferencia de Rendimiento en Lluvia)
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


## 📊 **6. Análisis de la Posición de Salida vs Resultado Final**
st.subheader("🏁 ¿Qué Tan Importante es la Posición de Salida?")
st.markdown("🔹 **Este gráfico muestra cómo la posición de salida afecta el resultado final de los pilotos.**")
st.markdown("💡 **Conclusión esperada:** Los pilotos que salen adelante suelen terminar más adelante, pero en algunas carreras hay remontadas espectaculares.")

# Calcular diferencia entre posición de salida y posición final
df_filtered["pos_dif"] = df_filtered["grid"] - df_filtered["positionorder"]

# Agrupar por posición de salida y calcular promedio de posiciones ganadas o perdidas
df_grid_analysis = df_filtered.groupby("grid")["pos_dif"].mean().reset_index()

# Crear gráfico de líneas para ver tendencias
fig = px.line(df_grid_analysis, x="grid", y="pos_dif",
              labels={"grid": "Posición de Salida", "pos_dif": "Posiciones Ganadas (+) o Perdidas (-)"},
              title="📊 Impacto de la Posición de Salida en el Resultado Final")

st.plotly_chart(fig, use_container_width=True)

## 📊 **7. ¿Cómo Afecta la Lluvia la Posición de Salida?**
st.subheader("🌧️ ¿La Lluvia Cambia el Impacto de la Parrilla de Salida?")
st.markdown("🔹 **Comparamos carreras secas y mojadas para ver si la lluvia facilita remontadas.**")

# Separar datos en lluvia y seco
df_rain = df_filtered[df_filtered["rainfall"] == True].groupby("grid")["pos_dif"].mean().reset_index()
df_dry = df_filtered[df_filtered["rainfall"] == False].groupby("grid")["pos_dif"].mean().reset_index()

# Unir datos y agregar una columna de condición climática
df_rain["condition"] = "Lluvia"
df_dry["condition"] = "Seco"
df_weather_comparison = pd.concat([df_rain, df_dry])

# Crear gráfico de comparación
fig = px.line(df_weather_comparison, x="grid", y="pos_dif", color="condition",
              labels={"grid": "Posición de Salida", "pos_dif": "Posiciones Ganadas/Pérdidas", "condition": "Condición"},
              title="📊 Comparación: Impacto de la Lluvia en las Remontadas")

st.plotly_chart(fig, use_container_width=True)

## 📊 **8. ¿Desde Qué Posiciones Salen los Ganadores?**
st.subheader("🏆 ¿Desde Qué Posiciones Salen los Ganadores?")
st.markdown("🔹 **Este gráfico muestra desde qué posición de largada ganan más carreras los pilotos.**")

# Filtrar solo carreras ganadas (positionorder = 1)
df_winners = df_filtered[df_filtered["positionorder"] == 1].groupby("grid")["positionorder"].count().reset_index()
df_winners.rename(columns={"positionorder": "wins"}, inplace=True)

# Crear gráfico de barras
fig = px.bar(df_winners, x="grid", y="wins",
             labels={"grid": "Posición de Salida", "wins": "Carreras Ganadas"},
             title="📊 Distribución de Ganadores por Posición de Salida",
             color="wins", color_continuous_scale="Blues")

st.plotly_chart(fig, use_container_width=True)




# ===============================================
# 📅 **SECCIÓN 3: ANÁLISIS EVOLUTIVO A LO LARGO DE LOS AÑOS**
# ===============================================
st.markdown("---")  # Línea separadora para distinguir secciones
st.header("📊 Evolución del Rendimiento en la Fórmula 1")

st.markdown("🔹 Esta sección muestra la evolución del rendimiento a lo largo de los años.")
st.markdown("🔸 **Importante:** Esta sección **no se ve afectada** por los filtros laterales de Año y Equipo.")

# 📌 Usar todos los datos SIN FILTRAR para ver tendencias globales
df_evolution = df.copy()  # Hacemos una copia para evitar el SettingWithCopyWarning

# 🔹 Agregar columna de diferencia de posiciones
df_evolution["pos_dif"] = df_evolution["grid"] - df_evolution["positionorder"]

# 📊 **Evolución del Rendimiento de los Pilotos**
st.subheader("📈 Evolución del Rendimiento de los Pilotos a lo Largo de los Años")

df_pilots_evolution = df_evolution.groupby(["year", "driver_surname"])["points"].sum().reset_index()

fig_pilots = px.line(df_pilots_evolution, x="year", y="points", color="driver_surname",
                     labels={"year": "Año", "points": "Puntos Totales", "driver_surname": "Piloto"},
                     title="📊 Evolución del Rendimiento de los Pilotos",
                     markers=True)

st.plotly_chart(fig_pilots, use_container_width=True, key="grafico_pilotos")


# 📊 **Evolución del Rendimiento de los Equipos en Lluvia**
st.subheader("📈 ¿Qué Equipos han Mejorado en Lluvia con los Años?")

df_teams_evolution = df_evolution[df_evolution["rainfall"] == True].groupby(["year", "constructor_name"])["points"].mean().reset_index()

fig_teams = px.scatter(df_teams_evolution, x="year", y="points", color="constructor_name",
                       labels={"year": "Año", "points": "Puntos Promedio en Lluvia", "constructor_name": "Equipo"},
                       title="🌧️ Evolución del Rendimiento en Lluvia por Equipo")

st.plotly_chart(fig_teams, use_container_width=True, key="grafico_equipos_lluvia")


# 📊 **Promedio de Diferencia de Posiciones por Año y Grid**
st.subheader("📉 Evolución de la Diferencia de Posiciones Según la Posición de Largada")

# Verificar si la columna existe antes de agrupar
if "pos_dif" in df_evolution.columns:
    df_grid_year = df_evolution.groupby(["year", "grid"])["pos_dif"].mean().reset_index()

    fig_grid = px.line(df_grid_year, x="year", y="pos_dif", color="grid",
                       labels={"year": "Año", "pos_dif": "Diferencia de Posiciones", "grid": "Posición de Largada"},
                       title="📉 Promedio de Diferencia de Posiciones por Año y Posición de Largada")

    st.plotly_chart(fig_grid, use_container_width=True, key="grafico_grid")
else:
    st.warning("⚠ No se pudo calcular la diferencia de posiciones porque la columna `pos_dif` no existe en los datos.")


# 📊 **Evolución del Rendimiento de los Equipos en Lluvia**
st.subheader("📈 ¿Qué Equipos han Mejorado en Lluvia con los Años?")

df_teams_evolution = df_evolution[df_evolution["rainfall"] == True].groupby(["year", "constructor_name"])["points"].mean().reset_index()

fig = px.scatter(df_teams_evolution, x="year", y="points", color="constructor_name",
                 labels={"year": "Año", "points": "Puntos Promedio en Lluvia", "constructor_name": "Equipo"},
                 title="🌧️ Evolución del Rendimiento en Lluvia por Equipo")

st.plotly_chart(fig, use_container_width=True)

# 📊 **Promedio de Diferencia de Posiciones por Año y Grid**
st.subheader("📉 Evolución de la Diferencia de Posiciones Según la Posición de Largada")

# Verificar si la columna existe antes de agrupar
if "pos_dif" in df_evolution.columns:
    df_grid_year = df_evolution.groupby(["year", "grid"])["pos_dif"].mean().reset_index()

    fig = px.line(df_grid_year, x="year", y="pos_dif", color="grid",
                  labels={"year": "Año", "pos_dif": "Diferencia de Posiciones", "grid": "Posición de Largada"},
                  title="📉 Promedio de Diferencia de Posiciones por Año y Posición de Largada")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠ No se pudo calcular la diferencia de posiciones porque la columna `pos_dif` no existe en los datos.")



## 📊 **9. Evolución del Rendimiento de los Pilotos**
st.subheader("📈 Evolución del Rendimiento de los Pilotos")
st.markdown("🔹 **Este gráfico muestra cómo ha cambiado el rendimiento de los pilotos en cada temporada.**")

df_pilots_evolution = df_evolution.groupby(["year", "driver_surname"])["points"].sum().reset_index()

fig = px.line(df_pilots_evolution, x="year", y="points", color="driver_surname",
              labels={"year": "Año", "points": "Puntos Totales", "driver_surname": "Piloto"},
              title="📊 Evolución del Rendimiento de los Pilotos",
              markers=True)

st.plotly_chart(fig, use_container_width=True)


## 📊 **10. Evolución del Impacto de la Posición de Salida**
st.subheader("🚦 ¿Sigue Siendo Clave la Pole Position?")
st.markdown("🔹 **Este gráfico muestra si los pilotos han perdido o ganado más posiciones a lo largo de los años.**")

df_grid_year = df_evolution.groupby(["year", "grid"])["pos_dif"].mean().reset_index()

fig = px.line(df_grid_year, x="year", y="pos_dif", color="grid",
              labels={"year": "Año", "pos_dif": "Posiciones Ganadas/Pérdidas", "grid": "Posición de Salida"},
              title="📊 Evolución del Impacto de la Posición de Salida",
              markers=True)

st.plotly_chart(fig, use_container_width=True)


## 📊 **11. Evolución del Rendimiento en Lluvia**
st.subheader("🌧️ ¿Han Cambiado los Mejores Pilotos en Lluvia?")
st.markdown("🔹 **Este gráfico muestra la evolución del rendimiento en lluvia de los pilotos a lo largo de los años.**")

df_rain_year = df_evolution[df_filtered["rainfall"] == True].groupby(["year", "driver_surname"])["points"].mean().reset_index()

fig = px.line(df_rain_year, x="year", y="points", color="driver_surname",
              labels={"year": "Año", "points": "Puntos Promedio en Lluvia", "driver_surname": "Piloto"},
              title="📊 Evolución del Rendimiento en Lluvia",
              markers=True)

st.plotly_chart(fig, use_container_width=True)


## 📊 **12. Evolución del Rendimiento de los Equipos en Lluvia**
st.subheader("🌧️ ¿Qué Equipos han Mejorado en Lluvia con los Años?")
st.markdown("🔹 **Este gráfico muestra la evolución del rendimiento de los equipos en lluvia a lo largo de los años.**")

df_team_rain_year = df_evolution[df_filtered["rainfall"] == True].groupby(["year", "constructor_name"])["points"].mean().reset_index()

fig = px.line(df_team_rain_year, x="year", y="points", color="constructor_name",
              labels={"year": "Año", "points": "Puntos Promedio en Lluvia", "constructor_name": "Equipo"},
              title="📊 Evolución del Rendimiento en Lluvia por Equipo",
              markers=True)

st.plotly_chart(fig, use_container_width=True)


# ==============================
# 🔚 **CONCLUSIÓN FINAL**
# ==============================
st.markdown("📊 Datos obtenidos de Kaggle y procesados para análisis interactivo.")
st.markdown("🚀 **¡Gracias por utilizar este dashboard!**")
