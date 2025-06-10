"""import kagglehub
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

path = kagglehub.dataset_download("sumitrodatta/nba-aba-baa-stats")
print("Path to dataset files:", path)

archivo_shooting = "Player Shooting.csv"
archivo_players = "Player Season Info.csv"

file_path_shooting = os.path.join(path, archivo_shooting)
file_path_players = os.path.join(path, archivo_players)

df_shooting = pd.read_csv(file_path_shooting)
df_players = pd.read_csv(file_path_players)
print(df_players.columns)



df = df_shooting.merge(df_players, on=["player_id", "season"], suffixes=("_shooting", "_info"))


df = df[df["age_info"].between(18, 45)]
print(df.columns)

df_tiros = df[[
    "player_shooting", 
    "age_info", 
    "fg_percent",  
    "fg_percent_from_x3p_range", 
    "fg_percent_from_x0_3_range"  
]].copy()


df_tiros.rename(columns={
    "player_shooting": "player",
    "age_info": "age",
    "fg_percent": "FG%",
    "fg_percent_from_x3p_range": "3P%",
    "fg_percent_from_x0_3_range": "Rim FG%"
}, inplace=True)


df_melt = df_tiros.melt(
    id_vars=["player", "age"],
    value_vars=["FG%", "3P%", "Rim FG%"],
    var_name="Tipo de Tiro",
    value_name="Porcentaje"
)


df_melt = df_melt.dropna(subset=["Porcentaje"])

# Graficar violin plot
plt.figure(figsize=(12, 6))
sns.violinplot(
    data=df_melt,
    x="Tipo de Tiro",
    y="age",
    inner="quartile",
    palette="Set2"
)

plt.title("Distribución de Edad según Tipo de Tiro (Porcentaje de Acierto)")
plt.xlabel("Tipo de Tiro")
plt.ylabel("Edad del Jugador")

plt.tight_layout()
plt.show()
"""

import kagglehub
import pandas as pd
import os
import folium
import branca.colormap as cm

# Descargar y cargar archivos
path = kagglehub.dataset_download("sumitrodatta/nba-aba-baa-stats")

archivo_shooting = "Player Shooting.csv"
archivo_players = "Player Season Info.csv"

file_path_shooting = os.path.join(path, archivo_shooting)
file_path_players = os.path.join(path, archivo_players)

df_shooting = pd.read_csv(file_path_shooting)
df_players = pd.read_csv(file_path_players)

# Unir datasets por jugador y temporada
df = df_shooting.merge(df_players, on=["player_id", "season"], suffixes=("_shooting", "_info"))

# Filtrar edades razonables
df = df[df["age_info"].between(18, 45)]

# Seleccionar columnas relevantes
df_tiros = df[[
    "player_shooting",
    "tm_info",
    "age_info",
    "fg_percent",
    "fg_percent_from_x3p_range",
    "fg_percent_from_x0_3_range"
]].copy()

# Renombrar columnas para facilidad
df_tiros.rename(columns={
    "player_shooting": "player",
    "age_info": "age",
    "fg_percent": "FG%",
    "fg_percent_from_x3p_range": "3P%",
    "fg_percent_from_x0_3_range": "Rim FG%"
}, inplace=True)

# Agrupar por equipo y calcular promedios de tiros
df_grouped = df_tiros.groupby("tm_info").agg({
    "FG%": "mean",
    "3P%": "mean",
    "Rim FG%": "mean"
}).reset_index()
df_grouped = df_grouped.reset_index().rename(columns={"tm_info": "tm"})

# Mapear equipos a ciudades (agrega más si lo deseas)
team_city_map = {
    'ATL': 'Atlanta, GA', 'BOS': 'Boston, MA', 'BKN': 'Brooklyn, NY',
    'CHA': 'Charlotte, NC', 'CHI': 'Chicago, IL', 'CLE': 'Cleveland, OH',
    'DAL': 'Dallas, TX', 'DEN': 'Denver, CO', 'DET': 'Detroit, MI',
    'GSW': 'San Francisco, CA', 'HOU': 'Houston, TX', 'IND': 'Indianapolis, IN',
    'LAC': 'Los Angeles, CA', 'LAL': 'Los Angeles, CA', 'MEM': 'Memphis, TN',
    'MIA': 'Miami, FL', 'MIL': 'Milwaukee, WI', 'MIN': 'Minneapolis, MN',
    'NOP': 'New Orleans, LA', 'NYK': 'New York, NY', 'OKC': 'Oklahoma City, OK',
    'ORL': 'Orlando, FL', 'PHI': 'Philadelphia, PA', 'PHX': 'Phoenix, AZ',
    'POR': 'Portland, OR', 'SAC': 'Sacramento, CA', 'SAS': 'San Antonio, TX',
    'TOR': 'Toronto, ON', 'UTA': 'Salt Lake City, UT', 'WAS': 'Washington, DC'
}

# Coordenadas aproximadas para cada ciudad
city_coords = {
    'Los Angeles, CA': (34.0522, -118.2437),
    'Boston, MA': (42.3601, -71.0589),
    'New York, NY': (40.7128, -74.0060),
    'Miami, FL': (25.7617, -80.1918),
    'Dallas, TX': (32.7767, -96.7970),
    'San Francisco, CA': (37.7749, -122.4194),
    'Chicago, IL': (41.8781, -87.6298),
    'Philadelphia, PA': (39.9526, -75.1652),
    'Phoenix, AZ': (33.4484, -112.0740),
    'Toronto, ON': (43.651070, -79.347015),
    # Agrega más ciudades si es necesario...
}

# Agregar ciudad y coordenadas al DataFrame
df_grouped["city"] = df_grouped["tm"].map(team_city_map)
df_grouped["coords"] = df_grouped["city"].map(city_coords)
df_grouped = df_grouped.dropna(subset=["coords"])
df_grouped["latitude"] = df_grouped["coords"].apply(lambda x: x[0])
df_grouped["longitude"] = df_grouped["coords"].apply(lambda x: x[1])

# Crear mapa base
m = folium.Map(location=[39.5, -98.35], zoom_start=4)

# Colormap para FG%
colormap = cm.LinearColormap(
    colors=['yellow', 'orange', 'red'],
    vmin=df_grouped["FG%"].min(),
    vmax=df_grouped["FG%"].max(),
    caption="FG% promedio por equipo"
)

# Añadir marcadores al mapa
for _, row in df_grouped.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=10,
        color=colormap(row["FG%"]),
        fill=True,
        fill_color=colormap(row["FG%"]),
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>Equipo:</b> {row['tm']}<br>"
            f"<b>FG%:</b> {row['FG%']:.2f}<br>"
            f"<b>3P%:</b> {row['3P%']:.2f}<br>"
            f"<b>Rim FG%:</b> {row['Rim FG%']:.2f}",
            max_width=250
        )
    ).add_to(m)

# Añadir leyenda de colores
colormap.add_to(m)

# Guardar mapa como archivo HTML
m.save("mapa_porcentajes_tiro.html")
print("Mapa guardado como 'mapa_porcentajes_tiro.html'")
