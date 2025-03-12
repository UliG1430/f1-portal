import pandas as pd

# --- Cargar datasets --- #
f1_races = pd.read_csv("data/raw/races.csv")
f1_results = pd.read_csv("data/raw/results.csv")
f1_weather = pd.read_csv("data/raw/weather.csv")
circuits_df = pd.read_csv("data/raw/circuits.csv")
drivers_df = pd.read_csv("data/raw/drivers.csv")
constructors_df = pd.read_csv("data/raw/constructors.csv")

# Filtrar solo las carreras entre 2018 y 2023
f1_races = f1_races[(f1_races['year'] >= 2018) & (f1_races['year'] <= 2023)]

# Unir f1_results con f1_races para obtener Year y Round Number
f1_results = f1_results.merge(f1_races[['raceId', 'year', 'round']], on='raceId', how='inner')

# Eliminar duplicados en el dataset de clima
f1_weather = f1_weather.drop_duplicates()

# Convertir nombres de columnas a minúsculas y estandarizar
f1_weather.columns = f1_weather.columns.str.lower().str.replace(" ", "_")
f1_results.columns = f1_results.columns.str.lower().str.replace(" ", "_")
drivers_df.columns = drivers_df.columns.str.lower().str.replace(" ", "_")
constructors_df.columns = constructors_df.columns.str.lower().str.replace(" ", "_")

# --- 🔹 Corregir Lluvia: Si en algún momento de la carrera llovió, marcar toda la carrera como mojada ---
f1_weather_grouped = f1_weather.groupby(['year', 'round_number']).agg({
    'airtemp': 'mean',
    'humidity': 'mean',
    'pressure': 'mean',
    'rainfall': lambda x: x.any(),  # Si en algún momento de la carrera llovió, marcar toda la carrera como True
    'tracktemp': 'mean',
    'winddirection': 'mean',
    'windspeed': 'mean'
}).reset_index()

# Fusionar datasets en base a year y round
f1_merged = f1_results.merge(
    f1_weather_grouped, 
    left_on=['year', 'round'], 
    right_on=['year', 'round_number'], 
    how='inner'
)

# --- Unir con datos de pilotos y constructores ---
# Agregar nombres de pilotos
f1_merged = f1_merged.merge(
    drivers_df[['driverid', 'surname', 'forename', 'nationality']], 
    on='driverid', 
    how='left'
)

# Agregar nombres de constructores
f1_merged = f1_merged.merge(
    constructors_df[['constructorid', 'name']], 
    on='constructorid', 
    how='left'
)

# Renombrar columnas para mayor claridad
f1_merged.rename(columns={'surname': 'driver_surname', 'forename': 'driver_forename', 'name': 'constructor_name'}, inplace=True)

# Verificar qué columnas existen antes de eliminarlas
columns_to_drop = [col for col in ['raceid', 'round_number', 'time_y'] if col in f1_merged.columns]
f1_merged = f1_merged.drop(columns=columns_to_drop)

# Guardar el dataset limpio en la carpeta data/clean/
output_path = "data/clean/f1_final_dataset.csv"
f1_merged.to_csv(output_path, index=False)
print(f"✅ Dataset final con nombres de pilotos y constructores guardado en {output_path}")

# Mostrar primeras filas para verificar la fusión
print("Datos fusionados de Clima y Resultados de F1:")
print(f1_merged.head())

# Explorar estructura final de los datos
print("\nEstructura del dataset final:")
print(f1_merged.info())
