"""

Este script descarga todos los archivos PDF del SMN y los convierte en
un solo archivo CSV en formato de series de tiempo.

Fuente: https://smn.conagua.gob.mx/es/climatologia/temperaturas-y-lluvias/resumenes-mensuales-de-temperaturas-y-lluvias

"""

import os

import pandas as pd
import requests
import tabula


# En los archivos PDF cada columna tiene el nombre del mes.
# Este diccionario nos ayuda a asignarle su número.
MESES = {
    "Ene": "01",
    "Feb": "02",
    "Mar": "03",
    "Abr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Ago": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dic": "12",
}

# Este diccionario nos ayuda a asignarle
# la clave a cada entidad.
ENTIDADES = {
    0: "Nacional",
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas",
}

ENTIDADES_INVERTIDO = {v: k for k, v in ENTIDADES.items()}


def descargar():
    """
    Descarga todos los archivos PDF del sitio web del SMN.
    """

    # Crea la carpeta 'pdf' si no existe.
    os.makedirs("./pdf", exist_ok=True)

    # Hay 4 tipos de archivos: 3 para temperatura y uno para precipitación.
    tipos = ["TMED", "TMAX", "TMIN", "PREC"]

    # Definimos la URL base, la cual tiene dos parámetros: tipo y año.
    url_base = "https://smn.conagua.gob.mx/tools/DATA/Climatolog%C3%ADa/Pron%C3%B3stico%20clim%C3%A1tico/Temperatura%20y%20Lluvia/{}/{}.pdf"

    # Iteramos sobre cada año y tipo.
    for i in range(1985, 2026):
        for tipo in tipos:
            # Preparamos la URL final con los parámetros de la iteración.
            url_final = url_base.format(tipo, i)

            # Descargamos el PDF y lo guardamos en su carpeta.
            with requests.get(url_final) as response:
                open(f"./pdf/{i}_{tipo}.pdf", "wb").write(response.content)
                print("Descargado:", i, tipo)


def convertir():
    """
    Convierte todos los archivos PDF en archivos CSV.
    La librería tabula-py requiere tener instalado el entorno de ejecución de Java.
    Este se puede descargar desde: https://www.java.com/en/download/manual.jsp
    """

    # Crea la carpeta 'csv' si no existe.
    os.makedirs("./csv", exist_ok=True)

    # Iteramos sobre cada archivo PDF en la carpeta 'pdf'.
    for archivo in os.listdir("./pdf"):
        # Cargamos el archivo PDF y seleccionamos la primera (única) hoja.
        tabla = tabula.read_pdf(f"./pdf/{archivo}", pages="all")[0]

        # Guardamos la tabla procesada en la carpeta 'csv'.
        tabla.to_csv(
            f"./csv/{archivo.replace('.pdf', '.csv')}", encoding="utf-8", index=False
        )
        print("Convertido:", archivo)


def combinar():
    """
    Une todos los archivos CSV en uno solo y le da formato de series de tiempo.
    """

    # Esta lista almacenará los DataFrames anuales.
    dfs = list()

    # En lugar de iterar por archivo, iteraremos por año.
    for i in range(1985, 2026):
        # Cargamos el archivo de temperatura media.
        df1 = pd.read_csv(f"./csv/{i}_TMED.csv", index_col=0)

        # Seleccionamos todas las columnas (meses) excepto la última (total).
        # Los totales anuales se calcularán bajo demanda.
        df1 = df1.iloc[:, :-1].transpose()

        # El índice (que antes eran las columnas) será convertido a formato de fecha.
        df1.index = df1.index.map(lambda x: f"{i}-{MESES[x]}-01")

        # Le damos el mismo tratamiento al PDF de temperatura mínima,
        # máxima y precipitación.

        df2 = pd.read_csv(f"./csv/{i}_TMIN.csv", index_col=0)
        df2 = df2.iloc[:, :-1].transpose()
        df2.index = df2.index.map(lambda x: f"{i}-{MESES[x]}-01")

        df3 = pd.read_csv(f"./csv/{i}_TMAX.csv", index_col=0)
        df3 = df3.iloc[:, :-1].transpose()
        df3.index = df3.index.map(lambda x: f"{i}-{MESES[x]}-01")

        df4 = pd.read_csv(f"./csv/{i}_PREC.csv", index_col=0)
        df4 = df4.iloc[:, :-1].transpose()
        df4.index = df4.index.map(lambda x: f"{i}-{MESES[x]}-01")

        # Vamos a iterar sobre cada entidad.
        # El orden de las entidades no es el mismo en cada PDF.
        # Pero este algoritmo no es afectado por eso.
        for ent in ENTIDADES.values():
            # De cada DataFrame vamos a seleccionar la columna
            # de la entidad en la iteración.
            temp_df1 = df1[ent].to_frame("TMED")
            temp_df2 = df2[ent].to_frame("TMIN")
            temp_df3 = df3[ent].to_frame("TMAX")
            temp_df4 = df4[ent].to_frame("PREC")

            # Unimos los 4 DataFrames anteriormente creados.
            año_df = pd.concat([temp_df1, temp_df2, temp_df3, temp_df4], axis=1)

            # Agregamos una columna con el nombre de la entidad.
            año_df["ENTIDAD"] = ent

            # Este DataFrame anual estatal lo agregamos a la lista de DataFrames.
            dfs.append(año_df)

    # Unimos todos los DataFrames de la lista que declaramos al inicio.
    final = pd.concat(dfs)

    # Reseteamos el índice, ya que la columna de la fecha
    # la vamos a necesitar para ordenar el DataFrame.
    final.reset_index(inplace=True)

    # Agregamos la clave de cada entidad.
    final["CVE_ENT"] = final["ENTIDAD"].map(ENTIDADES_INVERTIDO)

    # Renombramos las columnas.
    final.rename(
        columns={
            "index": "PERIODO",
            "TMED": "MEDIA",
            "TMIN": "MINIMA",
            "TMAX": "MAXIMA",
            "PREC": "PRECIPITACION",
        },
        inplace=True,
    )

    # Ordenamos las columnas.
    final = final[
        ["PERIODO", "CVE_ENT", "ENTIDAD", "MINIMA", "MEDIA", "MAXIMA", "PRECIPITACION"]
    ]

    # Ordenamos el DataFrame usando todas las columnas.
    final.sort_values(list(final.columns), inplace=True)

    # Quitamos los valores nulos, ya que son de meses que aún no ocurren.
    final = final.dropna(axis=0)

    # Guardamos nuestro DataFrame.
    final.to_csv("./data.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    descargar()
    convertir()
    combinar()
