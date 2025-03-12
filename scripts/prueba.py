import pandas as pd

df = pd.read_csv("data/clean/f1_final_dataset.csv")

# Contar cuántas carreras tuvieron lluvia
print("\n🔹 Cantidad de carreras en seco vs mojadas:")
print(df["rainfall"].value_counts())

# Ver primeros registros de la columna rainfall
print("\n🔹 Ejemplo de valores en rainfall:")
print(df[["year", "round", "rainfall"]].head())
