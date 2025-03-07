import pandas as pd

# --- Cargar datasets --- #
races_df = pd.read_csv("data/raw/races.csv")
results_df = pd.read_csv("data/raw/results.csv")
weather_df = pd.read_csv("data/raw/weather.csv")
circuits_df = pd.read_csv("data/raw/circuits.csv")
drivers_df = pd.read_csv("data/raw/drivers.csv")
constructors_df = pd.read_csv("data/raw/constructors.csv")

# --- Filtrar datos de 2018 a 2023 --- #
races_df = races_df[(races_df["year"] >= 2018) & (races_df["year"] <= 2023)]
results_df = results_df[results_df["raceId"].isin(races_df["raceId"])]

# --- Seleccionar columnas clave --- #
races_df = races_df[["raceId", "year", "round", "circuitId", "name", "date"]]
results_df = results_df[["resultId", "raceId", "driverId", "constructorId", "grid", "position", "positionOrder", "points", "laps", "fastestLapTime", "fastestLapSpeed"]]
circuits_df = circuits_df[["circuitId", "name", "location", "country", "lat", "lng", "alt"]]
drivers_df = drivers_df[["driverId", "forename", "surname", "dob", "nationality"]]
constructors_df = constructors_df[["constructorId", "name", "nationality"]]

# --- Limpiar y transformar datos --- #
print(weather_df.columns)  # Lista todas las columnas del CSV

# Renombrar columnas en weather_df para que coincidan con races_df
weather_df.rename(columns={"Year": "year", "Round Number": "round"}, inplace=True)

# Unir los datos de clima con las carreras usando "year" y "round"
races_weather_df = races_df.merge(weather_df, on=["year", "round"], how="left")

# --- Unir datasets --- #
results_expanded_df = results_df.merge(drivers_df, on="driverId", how="left").merge(constructors_df, on="constructorId", how="left")
final_df = results_expanded_df.merge(races_weather_df, on="raceId", how="left").merge(circuits_df, on="circuitId", how="left")

# --- Guardar datasets limpios en la carpeta correspondiente --- #
races_df.to_csv("data/clean/races_cleaned.csv", index=False)
results_expanded_df.to_csv("data/clean/results_cleaned.csv", index=False)
races_weather_df.to_csv("data/clean/races_weather_cleaned.csv", index=False)
final_df.to_csv("data/clean/f1_final_dataset.csv", index=False)

print("Archivos limpios y combinados guardados correctamente en data/clean/")
