"""

Este script nos permite crear visualizaciones para poder entender
las tendencias a largo plazo de la temperatura y precipitación.

"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.nonparametric.smoothers_lowess import lowess


# Este será el texto mostrado en cada anotación de fuente.
FECHA_FUENTE = "agosto 2026"

# Estos serán los colores usados para todas las visualizaciones.
PAPER_COLOR = "#002222"
PLOT_COLOR = "#001414"


# Este diccionario nos ayudará a darle formato a los meses.
MESES_ABREVIADOS = {
    1: "Ene.",
    2: "Feb.",
    3: "Mar.",
    4: "Abr.",
    5: "May.",
    6: "Jun.",
    7: "Jul.",
    8: "Ago.",
    9: "Sep.",
    10: "Oct.",
    11: "Nov.",
    12: "Dic.",
}


MESES_NOMBRES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def temperatura(entidad_id, tipo):
    """
    Genera una gráfica de múltiples líneas mostrando
    la evolución de la temperatura para la entidad especificada.

    Parameters
    ----------
    entidad_id : int
        La clave de la entidad. 0 para cifras a nivel nacional.

    tipo : str
        MINIMA, MEDIA o MAXIMA

    """

    # Estos serán los años que mostraremos.
    # Es recomendable que cada uno tenga un color distinto.
    años = {
        1986: "#90caf9",
        1996: "#8bc34a",
        2006: "#ffd54f",
        2016: "#ffa726",
        2026: "#ef5350",
    }

    # Cargamos el archivo de temperatura y precipitación.
    df = pd.read_csv("./data.csv", parse_dates=["PERIODO"], index_col=0)

    # Seleccionamos los registros de la entidad especificada.
    df = df[df["CVE_ENT"] == entidad_id]

    # Extraemos el nombre de la entidad.
    entidad = df["ENTIDAD"].iloc[0]

    fig = go.Figure()

    # Iteramos sobre cada año especificado.
    for año, color in años.items():
        # Seleccionamos los datos del año especificado.
        temp_df = df[df.index.year == año].copy()
        temp_df.index = temp_df.index.month

        fig.add_trace(
            go.Scatter(
                x=temp_df.index,
                y=temp_df[tipo],
                mode="markers+lines",
                name=año,
                marker_color=color,
                marker_size=24,
                line_width=4,
                line_shape="spline",
            )
        )

    fig.update_xaxes(
        tickvals=list(MESES_ABREVIADOS.keys()),
        ticktext=list(MESES_ABREVIADOS.values()),
        ticks="outside",
        ticklen=10,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        title="Temperatura (°C)",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=20,
    )

    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_title="<b>Año</b>",
        legend_title_side="top center",
        legend_bordercolor="#EEEEEE",
        legend_xanchor="left",
        legend_yanchor="top",
        legend_x=0.01,
        legend_y=0.97,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la temperatura {tipo.lower()} mensual en <b>{entidad.replace('Nacional', 'México')}</b>",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=130,
        margin_r=40,
        margin_b=120,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SMN ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes de registro",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./{tipo.lower()}_{entidad_id}.png")


def tabla_temperatura():
    """
    Genera una tabla con los meses más cálidos y fríos para cada entidad.
    """

    # Cargamos el archivo de temperatura y precipitación.
    df = pd.read_csv("./data.csv", parse_dates=["PERIODO"])

    # Obtenemos el mes con mayor temperatura promedio para cada entidad.
    maximas = df.groupby("CVE_ENT")["MAXIMA"].idxmax()
    maximas = df.loc[maximas]
    maximas["texto"] = maximas.apply(
        lambda x: (
            f"{MESES_ABREVIADOS[x['PERIODO'].month]}, {x['PERIODO'].year} ({x['MAXIMA']} °C)"
        ),
        axis=1,
    )

    # Obtenemos el mes con menor temperatura promedio para cada entidad.
    minimas = df.groupby("CVE_ENT")["MINIMA"].idxmin()
    minimas = df.loc[minimas]
    minimas["texto"] = minimas.apply(
        lambda x: (
            f"{MESES_ABREVIADOS[x['PERIODO'].month]}, {x['PERIODO'].year} ({x['MINIMA']} °C)"
        ),
        axis=1,
    )

    nota = "*En base a promedios mensuales"

    fig = go.Figure()

    # Vamos a crear una tabla con 3 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[150, 220],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Menor temperatura promedio*</b>",
                    "<b>Mayor temperatura promedio*</b>",
                ],
                font_color="#FFFFFF",
                fill_color=["#7b1fa2", "#0277bd", "#dd2c00"],
                line_width=0.75,
                align="center",
                height=39,
            ),
            cells=dict(
                values=[minimas["ENTIDAD"], minimas["texto"], maximas["texto"]],
                line_width=0.75,
                fill_color=PLOT_COLOR,
                height=39,
                align=["left", "center"],
            ),
        )
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=1600,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        margin_t=180,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=40,
        title_text="Las temperaturas más bajas y altas en México<br>por entidad y mes de registro (1985-2026)",
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SMN ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=0.015,
                xanchor="center",
                yanchor="top",
                text=nota,
            ),
            dict(
                x=1.01, y=0.015, xanchor="right", yanchor="top", text="🧁 @lapanquecita"
            ),
        ],
    )

    fig.write_image("./tabla.png")


def mensual(entidad_id, mes_id):
    """
    Genera una gráfica mostrando la evolución de
    temperaturas durante el mes especificado.

    Parameters
    ----------
    entidad_id : int
        La clave de la entidad. 0 para cifras a nivel nacional.

    mes_id : int
        El mes que se desea visualizar.

    """

    # Cargamos el archivo de temperatura y precipitación.
    df = pd.read_csv("./data.csv", parse_dates=["PERIODO"], index_col=0)

    # Seleccionamos los registros de la entidad especificada.
    df = df[df["CVE_ENT"] == entidad_id]

    # Extraemos el nombre de la entidad.
    entidad = df["ENTIDAD"].iloc[0]

    # Filtramos por el mes especificado.
    df = df[df.index.month == mes_id]

    # El índice será el año.
    df.index = df.index.year

    # Esta gráfica estará compuesta de 3 gráficas independientes.
    # Una para las temperaturas máximas, medias y mínimas.
    # Cada una estará acompañada de una línea de tendencia.
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[
            "Temperatura máxima (promedio mensual)",
            "Temperatura media (promedio mensual)",
            "Temperatura mínima (promedio mensual)",
        ],
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MAXIMA"],
            mode="markers",
            marker_color="#e57373",
            marker_size=24,
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=lowess(df["MAXIMA"], df.index, frac=0.25, return_sorted=False),
            mode="lines",
            line_color="#FFFFFF",
            line_width=5,
            name="Tendencia (LOWESS)",
            legend="legend1",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MEDIA"],
            mode="markers",
            marker_color="#ffc107",
            marker_size=24,
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=lowess(df["MEDIA"], df.index, frac=0.25, return_sorted=False),
            mode="lines",
            line_color="#FFFFFF",
            line_width=5,
            name="Tendencia (LOWESS)",
            legend="legend2",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MINIMA"],
            mode="markers",
            marker_color="#64b5f6",
            marker_size=24,
            showlegend=False,
        ),
        row=3,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=lowess(df["MINIMA"], df.index, frac=0.25, return_sorted=False),
            mode="lines",
            line_color="#FFFFFF",
            line_width=5,
            name="Tendencia (LOWESS)",
            legend="legend3",
        ),
        row=3,
        col=1,
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        title="Temperatura (°C)",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=20,
    )

    for item in fig.layout.annotations:
        item["font"]["size"] = 36
        item["y"] += 0.01

    fig.add_annotation(
        x=0.01,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="left",
        yanchor="top",
        text=f"Fuente: SMN ({FECHA_FUENTE})",
    )

    fig.add_annotation(
        x=0.5,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="center",
        yanchor="top",
        text="Año",
    )

    fig.add_annotation(
        x=1.01,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="right",
        yanchor="top",
        text="🧁 @lapanquecita",
    )

    fig.update_layout(
        showlegend=True,
        legend1=dict(
            x=0.02, y=0.98, borderwidth=1.25, bordercolor="#EEEEEE", bgcolor=PLOT_COLOR
        ),
        legend2=dict(
            x=0.02, y=0.62, borderwidth=1.25, bordercolor="#EEEEEE", bgcolor=PLOT_COLOR
        ),
        legend3=dict(
            x=0.02, y=0.26, borderwidth=1.25, bordercolor="#EEEEEE", bgcolor=PLOT_COLOR
        ),
        width=1920,
        height=2400,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de las temperaturas de <b>{MESES_ABREVIADOS[mes_id].lower()}</b> en <b>{entidad.replace('Nacional', 'México')}</b> ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.98,
        margin_t=200,
        margin_l=140,
        margin_r=40,
        margin_b=140,
        title_font_size=42,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PLOT_COLOR,
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./historico_{entidad_id}.png")


def invierno(entidad_id):
    """
    Genera una gráfica mostrando la evolución de
    temperaturas durante el invierno meteorológico.

    Parameters
    ----------
    entidad_id : int
        La clave de la entidad. 0 para cifras a nivel nacional.

    """

    # Cargamos el archivo de temperatura y precipitación.
    df = pd.read_csv("./data.csv", parse_dates=["PERIODO"], index_col=0)

    # Seleccionamos los registros de la entidad especificada.
    df = df[df["CVE_ENT"] == entidad_id]

    # Extraemos el nombre de la entidad.
    entidad = df["ENTIDAD"].iloc[0]

    # Solo seleccionamos enero, febrero y diciembre.
    df = df[df.index.month.isin([12, 1, 2])]

    # El diciembre de cada año corresponde al siguiente invierno.
    # Por ejemplo: diciembre de 2025 pertenece al invierno de 2026.
    # Con la siguiente línea arreglamos ese detalle.
    df["Año"] = df.index.map(lambda x: x.year + 1 if x.month == 12 else x.year)

    # Calculamos el promedio invernal.
    df = df.groupby("Año").mean(numeric_only=True)

    # Esta gráfica estará compuesta de 3 gráficas independientes.
    # Una para las temperaturas máximas, medias y mínimas.
    # Cada una estará acompañada de una línea de tendencia.
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[
            "Temperatura máxima (promedio estacional)",
            "Temperatura media (promedio estacional)",
            "Temperatura mínima (promedio estacional)",
        ],
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MAXIMA"],
            mode="markers",
            marker_color="#e57373",
            marker_size=24,
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=lowess(df["MAXIMA"], df.index, frac=0.25, return_sorted=False),
            mode="lines",
            line_color="#FFFFFF",
            line_width=5,
            name="Tendencia (LOWESS)",
            legend="legend1",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MEDIA"],
            mode="markers",
            marker_color="#ffc107",
            marker_size=24,
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=lowess(df["MEDIA"], df.index, frac=0.25, return_sorted=False),
            mode="lines",
            line_color="#FFFFFF",
            line_width=5,
            name="Tendencia (LOWESS)",
            legend="legend2",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MINIMA"],
            mode="markers",
            marker_color="#64b5f6",
            marker_size=24,
            showlegend=False,
        ),
        row=3,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=lowess(df["MINIMA"], df.index, frac=0.25, return_sorted=False),
            mode="lines",
            line_color="#FFFFFF",
            line_width=5,
            name="Tendencia (LOWESS)",
            legend="legend3",
        ),
        row=3,
        col=1,
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        title="Temperatura (°C)",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=20,
    )

    for item in fig.layout.annotations:
        item["font"]["size"] = 36
        item["y"] += 0.01

    fig.add_annotation(
        x=0.01,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="left",
        yanchor="top",
        text=f"Fuente: SMN ({FECHA_FUENTE})",
    )

    fig.add_annotation(
        x=0.5,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="center",
        yanchor="top",
        text="Temporada invernal (diciembre—febrero)",
    )

    fig.add_annotation(
        x=1.01,
        y=-0.055,
        xref="paper",
        yref="paper",
        xanchor="right",
        yanchor="top",
        text="🧁 @lapanquecita",
    )

    fig.update_layout(
        showlegend=True,
        legend1=dict(
            x=0.02, y=0.98, borderwidth=1.25, bordercolor="#EEEEEE", bgcolor=PLOT_COLOR
        ),
        legend2=dict(
            x=0.02, y=0.62, borderwidth=1.25, bordercolor="#EEEEEE", bgcolor=PLOT_COLOR
        ),
        legend3=dict(
            x=0.02, y=0.26, borderwidth=1.25, bordercolor="#EEEEEE", bgcolor=PLOT_COLOR
        ),
        width=1920,
        height=2400,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de las temperaturas invernales en <b>{entidad.replace('Nacional', 'México')}</b> ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.98,
        margin_t=200,
        margin_l=140,
        margin_r=40,
        margin_b=140,
        title_font_size=42,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PLOT_COLOR,
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./invierno_{entidad_id}.png")


def precipitacion_anual(entidad_id):
    """
    Genera una gráfica de barras mostrando la precipitación
    anual acumulada para la entidad especificada.

    Parameters
    ----------
    entidad_id : int
        La clave de la entidad. 0 para cifras a nivel nacional.

    """

    # Estos serán los años que mostraremos.
    df = pd.read_csv("./data.csv", parse_dates=["PERIODO"], index_col=0)

    # Seleccionamos los registros de la entidad especificada.
    df = df[df["CVE_ENT"] == entidad_id]

    # Extraemos el nombre de la entidad.
    entidad = df["ENTIDAD"].iloc[0]

    # Remuestreamos por año.
    df = df.resample("YS").sum(numeric_only=True)

    # Del índice solo necesitaremos el año.
    df.index = df.index.year

    # Calculamos la mediana histórica.
    mediana = df["PRECIPITACION"].median()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["PRECIPITACION"],
            marker_line_width=0,
            marker_color="#ff3d00",
        )
    )

    # Agregamos la línea de la mediana histórica.
    fig.add_shape(
        x0=1980, x1=2030, y0=mediana, y1=mediana, line_width=4, line_color="#FFFFFF"
    )

    fig.update_xaxes(
        range=[df.index.min() - 0.5, df.index.max() + 0.5],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Precipitación anual acumulada (mm)",
        ticks="outside",
        tickformat="s",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la precipitación anual en <b>{entidad.replace('Nacional', 'México')}</b> ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=160,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=mediana * 1.025,
                xref="paper",
                xanchor="center",
                yanchor="top",
                text=f"<b>Mediana histórica ({mediana:,.1f} mm)</b>",
            ),
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SMN ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./precipitacion_{entidad_id}.png")


def top_lluvia(entidad_id):
    """
    Genera una gráfica de barras mostrando los 20 meses
    con mayor precipitación de la entidad especificada.

    Parameters
    ----------
    entidad_id : int
        La clave de la entidad. 0 para cifras a nivel nacional.

    """

    # Estos serán los años que mostraremos.
    df = pd.read_csv("./data.csv", parse_dates=["PERIODO"], index_col=0)

    # Seleccionamos los registros de la entidad especificada.
    df = df[df["CVE_ENT"] == entidad_id]

    # Extraemos el nombre de la entidad.
    entidad = df["ENTIDAD"].iloc[0]

    # Calculamos las medianas históricas.
    medianas = df.groupby(df.index.month).median(numeric_only=True)

    # Preparamos una tabla con los meses de verano.
    tabla = [
        "<b>Medianas históricas</b>",
        f"Junio: <b>{medianas.loc[6]['PRECIPITACION']:,.1f}</b>",
        f"Julio: <b>{medianas.loc[7]['PRECIPITACION']:,.1f}</b>",
        f"Agosto: <b>{medianas.loc[8]['PRECIPITACION']:,.1f}</b>",
        f"Septiembre: <b>{medianas.loc[9]['PRECIPITACION']:,.1f}</b>",
    ]

    tabla = "<br>".join(tabla)

    # Ordenamos el DataFrame por precipitación y tomamos los 20 registros más altos.
    df.sort_values("PRECIPITACION", inplace=True)
    df = df.tail(20)

    # Le damos formato al índice.
    df.index = df.index.map(lambda x: f"{MESES_ABREVIADOS[x.month]}<br>{x.year}")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["PRECIPITACION"],
            text=df["PRECIPITACION"],
            marker_line_width=0,
            marker_color="#0097a7",
            textposition="outside",
            textfont_color="#FFFFFF",
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
    )

    fig.update_yaxes(
        title="Precipitación acumulada mensual (mm)",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Los 20 meses más lluviosos en <b>{entidad.replace('Nacional', 'México')}</b> entre 1985 y 2026",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=160,
        margin_l=140,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.02,
                y=0.94,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                align="left",
                borderpad=7,
                borderwidth=1,
                bordercolor="#FFFFFF",
                bgcolor="#002222",
                text=tabla,
            ),
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SMN ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./top_precipitacion_{entidad_id}.png")


if __name__ == "__main__":
    temperatura(0, "MEDIA")
    tabla_temperatura()
    invierno(0)
    mensual(9, 4)

    precipitacion_anual(0)
    top_lluvia(0)
