import pandas as pd

# --- 📥 Cargar datos ---
def load_data():
    """Carga las tablas de hechos y dimensiones."""
    fact_results = pd.read_csv("data/clean/fact_results.csv")
    dim_drivers = pd.read_csv("data/clean/dim_drivers.csv")
    dim_teams = pd.read_csv("data/clean/dim_teams.csv")
    dim_circuits = pd.read_csv("data/clean/dim_circuits.csv")  # ✅ Agregar esta línea
    return fact_results, dim_drivers, dim_teams, dim_circuits  # ✅ Incluir dim_circuits en el return


# --- 📌 Eliminar valores atípicos ---
def remove_outliers(df, columns):
    """Elimina valores atípicos usando el rango intercuartil (IQR)."""
    for column in columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df

# --- 📌 Función para filtrar datos ---
def filter_data(df, year=None, driver=None, team=None):
    """Filtra los datos por año, piloto o equipo."""
    if year:
        df = df[df["year"] == year]
    if driver and driver != "Todos":
        df = df[df["driver_surname"] == driver]
    if team and team != "Todos":
        df = df[df["constructor_name"] == team]
    return df
