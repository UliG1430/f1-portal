### metrics.py ###
"""
metrics.py
----------
Módulo que calcula métricas de desempeño en carreras de F1.

Funciones principales:
- calcular_coeficiente_lluvia(): Calcula el coeficiente de rendimiento en lluvia para cada piloto.

Este archivo es utilizado por `app.py` para generar rankings de desempeño en condiciones climáticas adversas.
"""

import pandas as pd

def calcular_coeficiente_lluvia(df):
    """
    Calcula el coeficiente de rendimiento en lluvia (CRL) por piloto.

    Parámetros:
        df (pd.DataFrame): DataFrame con los datos de carreras de F1, incluyendo clima.

    Retorna:
        pd.DataFrame: DataFrame con pilotos ordenados por mejor rendimiento en lluvia.
    """
    # Filtrar solo carreras donde hubo lluvia
    df_lluvia = df[df["Rainfall"] > 0]

    # Calcular métricas por piloto
    df_pilotos_lluvia = df_lluvia.groupby("surname").agg(
    total_puntos=("points", "sum"),  
    total_carreras=("raceId", "count"),  
    posicion_promedio=("position", "mean"),  
    adelantamientos=("grid", lambda x: (x - df_lluvia["position"]).sum())  
    ).reset_index()


    # Calcular el coeficiente de rendimiento en lluvia (CRL)
    df_pilotos_lluvia["CRL"] = (
        df_pilotos_lluvia["total_puntos"] / df_pilotos_lluvia["total_carreras"]
    ) + (
        df_pilotos_lluvia["adelantamientos"] / df_pilotos_lluvia["total_carreras"]
    ) - (
        df_pilotos_lluvia["posicion_promedio"] / 10
    )

    # Ordenar de mayor a menor CRL
    return df_pilotos_lluvia.sort_values(by="CRL", ascending=False)