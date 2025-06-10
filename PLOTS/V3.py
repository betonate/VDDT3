"""import kagglehub
import pandas as pd
import os
import matplotlib.pyplot as plt


path = kagglehub.dataset_download("sumitrodatta/nba-aba-baa-stats")


archivo_advanced = "Advanced.csv"
archivo_players = "Player Season Info.csv"


file_path_advanced = os.path.join(path, archivo_advanced)
file_path_players = os.path.join(path, archivo_players)


df_adv = pd.read_csv(file_path_advanced)


latest_season = df_adv['season'].max()
df_adv_latest = df_adv[df_adv['season'] == latest_season]

# Filtrar datos válidos
df_plot = df_adv_latest.dropna(subset=['age', 'per'])

# Graficar scatter plot simple
plt.figure(figsize=(10,6))
plt.scatter(df_plot['age'], df_plot['per'], alpha=0.7, color='royalblue', edgecolors='w', linewidth=0.5)
plt.xlabel('Edad del jugador')
plt.ylabel('PER (Player Efficiency Rating)')
plt.title('Relación entre Edad y PER de jugadores NBA')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
"""
import kagglehub
import pandas as pd
import os
import folium
import branca.colormap as cm

# Descargar dataset
path = kagglehub.dataset_download("sumitrodatta/nba-aba-baa-stats")

# Archivos
archivo_advanced = "Advanced.csv"
archivo_players = "Player Season Info.csv"

# Leer datos
df_adv = pd.read_csv(os.path.join(path, archivo_advanced))
df_players = pd.read_csv(os.path.join(path, archivo_players))

# Última temporada
latest_season = df_adv['season'].max()

# Filtrar datos para la última temporada y quitar nulos importantes
df_adv_latest = df_adv[(df_adv['season'] == latest_season) & df_adv['age'].notnull() & df_adv['per'].notnull()]
df_players_latest = df_players[df_players['season'] == latest_season]

# Merge para obtener el equipo de cada jugador junto con su PER y edad
df_merged = pd.merge(
    df_adv_latest[['player_id', 'age', 'per']],
    df_players_latest[['player_id', 'tm']],
    on='player_id',
    how='left'
)

# Mapeo abreviaturas a ciudades (como en el ejemplo anterior)
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

city_coords = {
    'Atlanta, GA': (33.7490, -84.3880), 'Boston, MA': (42.3601, -71.0589), 'Brooklyn, NY': (40.6782, -73.9442),
    'Charlotte, NC': (35.2271, -80.8431), 'Chicago, IL': (41.8781, -87.6298), 'Cleveland, OH': (41.4993, -81.6944),
    'Dallas, TX': (32.7767, -96.7970), 'Denver, CO': (39.7392, -104.9903), 'Detroit, MI': (42.3314, -83.0458),
    'San Francisco, CA': (37.7749, -122.4194), 'Houston, TX': (29.7604, -95.3698), 'Indianapolis, IN': (39.7684, -86.1581),
    'Los Angeles, CA': (34.0522, -118.2437), 'Memphis, TN': (35.1495, -90.0490), 'Miami, FL': (25.7617, -80.1918),
    'Milwaukee, WI': (43.0389, -87.9065), 'Minneapolis, MN': (44.9778, -93.2650), 'New Orleans, LA': (29.9511, -90.0715),
    'New York, NY': (40.7128, -74.0060), 'Oklahoma City, OK': (35.4676, -97.5164), 'Orlando, FL': (28.5383, -81.3792),
    'Philadelphia, PA': (39.9526, -75.1652), 'Phoenix, AZ': (33.4484, -112.0740), 'Portland, OR': (45.5051, -122.6750),
    'Sacramento, CA': (38.5816, -121.4944), 'San Antonio, TX': (29.4241, -98.4936), 'Toronto, ON': (43.6532, -79.3832),
    'Salt Lake City, UT': (40.7608, -111.8910), 'Washington, DC': (38.9072, -77.0369),
}

df_merged['city'] = df_merged['tm'].map(team_city_map)
df_merged['latitude'] = df_merged['city'].map(lambda c: city_coords.get(c, (None, None))[0])
df_merged['longitude'] = df_merged['city'].map(lambda c: city_coords.get(c, (None, None))[1])

# Crear grupos de edad (3 años por grupo)
#df_merged['age_group'] = pd.cut(df_merged['age'], bins=range(18, 46, 3))

# Elegir un grupo de edad para visualizar, por ejemplo 24-27 años
#group_to_show = pd.Interval(left=24, right=27, closed='right')
# Filtrar jugadores entre 20 y 35 años
df_group = df_merged[df_merged['age'].between(20, 35)]


# Agrupar por equipo para obtener el PER promedio y cantidad de jugadores
df_grouped = df_group.groupby(['tm', 'city', 'latitude', 'longitude']).agg(
    mean_per=('per', 'mean'),
    count_players=('player_id', 'count')
).reset_index()

# Crear mapa base
m = folium.Map(location=[39.5, -98.35], zoom_start=4)

# Crear colormap para el PER promedio
colormap = cm.LinearColormap(['lightblue', 'blue', 'darkblue'], 
                             vmin=df_grouped['mean_per'].min(), 
                             vmax=df_grouped['mean_per'].max())
colormap.caption = 'PER promedio (jugadores edad 20-35)'

# Añadir círculos al mapa con popup informativo
for _, row in df_grouped.iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        color = colormap(row['mean_per'])
        radius = 5 + 10 * (row['mean_per'] / df_grouped['mean_per'].max())  # tamaño proporcional PER
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=(
                f"Equipo: {row['tm']}<br>"
                f"Ciudad: {row['city']}<br>"
                f"PER promedio: {row['mean_per']:.2f}<br>"
                f"Número de jugadores: {row['count_players']}"
            ),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1
        ).add_to(m)

# Agregar la leyenda
colormap.add_to(m)

# Guardar el mapa en un archivo HTML
m.save("nba_per_por_edad_mapa.html")
print("Mapa generado y guardado como nba_per_por_edad_mapa.html")
