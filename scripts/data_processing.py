### data_processing.py ###
"""
data_processing.py
------------------
Módulo para la carga, limpieza y transformación de datos del proyecto de F1.

Funciones principales:
- cargar_datos(): Carga el dataset de carreras de F1 desde un archivo CSV.
- filtrar_datos_por_año(): Filtra los datos por un año específico.
- limpiar_datos(): Realiza limpieza de datos y conversión a valores numéricos.
- categorizar_temperatura(): Clasifica las temperaturas en tres categorías.

Este archivo es utilizado por `app.py` para preparar los datos antes de la visualización.
"""

import pandas as pd

def cargar_datos(filepath="data/clean/f1_final_dataset.csv"):
    """
    Carga el dataset limpio de F1 desde un archivo CSV.

    Parámetros:
        filepath (str): Ruta del archivo CSV con los datos limpios.

    Retorna:
        pd.DataFrame: DataFrame con los datos cargados.
    """
    return pd.read_csv(filepath)

def filtrar_datos_por_año(df, año):
    """
    Filtra los datos de carreras para un año específico.

    Parámetros:
        df (pd.DataFrame): DataFrame con los datos de carreras.
        año (int): Año a filtrar.

    Retorna:
        pd.DataFrame: DataFrame con los datos filtrados por año.
    """
    return df[df["year"] == año]

def limpiar_datos(df):
    """
    Limpia los datos, convierte columnas a valores numéricos y elimina valores nulos.

    Parámetros:
        df (pd.DataFrame): DataFrame con los datos sin limpiar.

    Retorna:
        pd.DataFrame: DataFrame limpio y procesado.
    """
    df = df.dropna(subset=["AirTemp", "fastestLapSpeed", "points", "grid", "positionOrder"])
    df["AirTemp"] = pd.to_numeric(df["AirTemp"], errors="coerce")
    df["fastestLapSpeed"] = pd.to_numeric(df["fastestLapSpeed"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce")
    df["grid"] = pd.to_numeric(df["grid"], errors="coerce")
    df["positionOrder"] = pd.to_numeric(df["positionOrder"], errors="coerce")
    return df.dropna()

def categorizar_temperatura(df):
    """
    Clasifica las temperaturas en tres categorías: Frío, Templado y Caluroso.

    Parámetros:
        df (pd.DataFrame): DataFrame con la columna 'AirTemp'.

    Retorna:
        pd.DataFrame: DataFrame con la nueva columna 'Temp_Categoria'.
    """
    df["Temp_Categoria"] = pd.cut(
        df["AirTemp"],
        bins=[-float("inf"), 15, 25, float("inf")],
        labels=["Frío (<15°C)", "Templado (15-25°C)", "Caluroso (>25°C)"]
    )
    return df
