import pandas as pd

# --- 📥 Cargar datasets ---
print("🔄 Cargando datasets...")
f1_races = pd.read_csv("data/raw/races.csv")
f1_results = pd.read_csv("data/raw/results.csv")
f1_weather = pd.read_csv("data/raw/weather.csv")
drivers_df = pd.read_csv("data/raw/drivers.csv")
constructors_df = pd.read_csv("data/raw/constructors.csv")
circuits_df = pd.read_csv("data/raw/circuits.csv")

print("✅ Datasets cargados correctamente.")

# 🔹 Verificar nombres de columnas en f1_weather
print("📊 Columnas en el dataset de clima:", f1_weather.columns)

# 🔹 Renombrar columnas para asegurarnos de que coincidan con el resto del análisis
f1_weather.columns = f1_weather.columns.str.lower().str.replace(" ", "_")
f1_results.columns = f1_results.columns.str.lower().str.replace(" ", "_")
drivers_df.columns = drivers_df.columns.str.lower().str.replace(" ", "_")
constructors_df.columns = constructors_df.columns.str.lower().str.replace(" ", "_")
circuits_df.columns = circuits_df.columns.str.lower().str.replace(" ", "_")
f1_races.columns = f1_races.columns.str.lower().str.replace(" ", "_")

# 🔹 Verificar si 'year' y 'round_number' existen en f1_weather
expected_columns = ['year', 'round_number']
missing_columns = [col for col in expected_columns if col not in f1_weather.columns]

if missing_columns:
    print(f"⚠️ Error: Faltan las siguientes columnas en f1_weather: {missing_columns}")
    print("Verificá los nombres de las columnas disponibles:", f1_weather.columns)
    exit()  # Detener ejecución si faltan columnas esenciales

# 🔹 Filtrar solo las carreras entre 2018 y 2023
print("🔄 Filtrando carreras entre 2018 y 2023...")
f1_races = f1_races[(f1_races['year'] >= 2018) & (f1_races['year'] <= 2023)]
print(f"✅ Carreras filtradas: {len(f1_races)} carreras en el rango 2018-2023.")

# 🔹 Unir f1_results con f1_races para obtener 'year' y 'round'
f1_results = f1_results.merge(f1_races[['raceid', 'year', 'round']], on='raceid', how='inner')

# 🔹 Corregir la columna 'rainfall': Si en algún momento de la carrera llovió, marcarla como mojada
print("🔄 Procesando datos climáticos...")
f1_weather_grouped = f1_weather.groupby(['year', 'round_number']).agg({
    'airtemp': 'mean',
    'humidity': 'mean',
    'pressure': 'mean',
    'rainfall': lambda x: x.any(),  # Si en algún momento de la carrera llovió, marcar toda la carrera como True
    'tracktemp': 'mean',
    'winddirection': 'mean',
    'windspeed': 'mean'
}).reset_index()
print("✅ Datos climáticos procesados.")

# 🔹 Fusionar datasets en base a year y round
print("🔄 Fusionando datos de carreras con clima...")
fact_results = f1_results.merge(
    f1_weather_grouped, 
    left_on=['year', 'round'], 
    right_on=['year', 'round_number'], 
    how='inner'
)
print(f"✅ Datos fusionados: {len(fact_results)} registros.")

# 🔹 Agregar información de pilotos y constructores
print("🔄 Agregando nombres de pilotos y constructores...")
fact_results = fact_results.merge(drivers_df[['driverid', 'surname', 'forename', 'nationality']], on='driverid', how='left')
fact_results = fact_results.merge(constructors_df[['constructorid', 'name']], on='constructorid', how='left')

# 🔹 Renombrar columnas para mayor claridad
fact_results.rename(columns={'surname': 'driver_surname', 'forename': 'driver_forename', 'name': 'constructor_name'}, inplace=True)

# 🔹 Eliminar columnas innecesarias
columns_to_drop = ['raceid', 'round_number']
fact_results = fact_results.drop(columns=[col for col in columns_to_drop if col in fact_results.columns])

# 🔹 Guardar tablas separadas
print("💾 Guardando datasets finales...")
fact_results.to_csv("data/clean/fact_results.csv", index=False)
drivers_df.to_csv("data/clean/dim_drivers.csv", index=False)
constructors_df.to_csv("data/clean/dim_teams.csv", index=False)
f1_races.to_csv("data/clean/dim_races.csv", index=False)
circuits_df.to_csv("data/clean/dim_circuits.csv", index=False)

print("✅ Datos limpiados y guardados correctamente.")
