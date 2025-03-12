import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

DATA_PATH = "data/clean/f1_final_dataset.csv"

# --- Cargar datos ---
def load_data():
    """Carga el dataset de F1."""
    df = pd.read_csv(DATA_PATH)
    return df

# --- Función para eliminar valores atípicos ---
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

# --- Función para filtrar datos ---
def filter_data(df, year=None, driver=None, team=None):
    """Filtra el dataset por año, piloto y equipo."""
    if year:
        df = df[df["year"] == year]
    if driver and driver != "Todos":
        df = df[df["driver_surname"] == driver]
    if team and team != "Todos":
        df = df[df["constructor_name"] == team]
    return df

# --- Función para generar estadísticas descriptivas ---
def get_statistics(df):
    """Retorna estadísticas descriptivas del dataset."""
    return df.describe()

# --- Función para generar gráficos de distribución ---
def plot_distributions(df):
    """Genera gráficos de boxplot para analizar distribución de variables climáticas y puntos."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    sns.boxplot(data=df, x='airtemp', ax=axes[0, 0])
    axes[0, 0].set_title("Distribución de la Temperatura del Aire")

    sns.boxplot(data=df, x='humidity', ax=axes[0, 1])
    axes[0, 1].set_title("Distribución de la Humedad")

    sns.boxplot(data=df, x='pressure', ax=axes[0, 2])
    axes[0, 2].set_title("Distribución de la Presión Atmosférica")

    sns.boxplot(data=df, x='tracktemp', ax=axes[1, 0])
    axes[1, 0].set_title("Distribución de la Temperatura de la Pista")

    sns.boxplot(data=df, x='windspeed', ax=axes[1, 1])
    axes[1, 1].set_title("Distribución de la Velocidad del Viento")

    sns.boxplot(data=df, x='points', ax=axes[1, 2])
    axes[1, 2].set_title("Distribución de los Puntos")

    plt.tight_layout()
    plt.show()

# --- Procesamiento principal ---
if __name__ == "__main__":
    df = load_data()

    # Eliminar valores atípicos
    columns_to_clean = ['airtemp', 'humidity', 'pressure', 'tracktemp', 'windspeed']
    df_clean = remove_outliers(df, columns_to_clean)

    # Guardar dataset limpio
    df_clean.to_csv("data/clean/f1_cleaned_final.csv", index=False)
    print("✅ Datos limpios guardados en 'data/clean/f1_cleaned_final.csv'")

    # Mostrar estadísticas
    print("\n🔹 Estadísticas descriptivas:")
    print(get_statistics(df_clean))

    # Mostrar gráficos
    plot_distributions(df_clean)
