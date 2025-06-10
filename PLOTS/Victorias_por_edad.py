"""import kagglehub
import pandas as pd
import os
import matplotlib.pyplot as plt
import joypy


path = kagglehub.dataset_download("sumitrodatta/nba-aba-baa-stats")


archivo_advanced = "Advanced.csv"
archivo_players = "Player Season Info.csv"
archivo_teams = "Team Summaries.csv"


file_path_advanced = os.path.join(path, archivo_advanced)
file_path_players = os.path.join(path, archivo_players)
file_path_teams = os.path.join(path, archivo_teams)


df_adv = pd.read_csv(file_path_advanced)
df_players = pd.read_csv(file_path_players)
df_teams = pd.read_csv(file_path_teams)
print(df_adv.columns)
print(df_players.columns)
print(df_teams.columns)
latest_season = df_players['season'].max()
df_players_latest = df_players[df_players['season'] == latest_season]
df_adv_latest = df_adv[df_adv['season'] == latest_season]
df_teams_latest = df_teams[df_teams['season'] == latest_season]


df_teams_latest['win_pct'] = df_teams_latest['w'] / (df_teams_latest['w'] + df_teams_latest['l'])


df_merged = pd.merge(
    df_players_latest,
    df_teams_latest[['abbreviation', 'win_pct']],
    left_on='tm',
    right_on='abbreviation',
    how='left'
)


df_merged['age_group'] = pd.cut(df_merged['age'], bins=range(18, 46, 3))

# Graficar ridgeline plot
joypy.joyplot(
    data=df_merged,
    by='age_group',
    column='win_pct',
    kind='kde',
    overlap=0.6,
    figsize=(12,8),
    colormap=plt.cm.coolwarm,
    title="Distribución del porcentaje de victorias del equipo según rango de edad de jugadores"
)

plt.xlabel("Porcentaje de victorias del equipo")
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
archivo_players = "Player Season Info.csv"
archivo_teams = "Team Summaries.csv"

# Leer datos
df_players = pd.read_csv(os.path.join(path, archivo_players))
df_teams = pd.read_csv(os.path.join(path, archivo_teams))

# Última temporada
latest_season = df_players['season'].max()
df_players_latest = df_players[df_players['season'] == latest_season]
df_teams_latest = df_teams[df_teams['season'] == latest_season]

# Calcular porcentaje victorias equipos
df_teams_latest['win_pct'] = df_teams_latest['w'] / (df_teams_latest['w'] + df_teams_latest['l'])

# Mapeo abreviaturas a ciudades
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

df_teams_latest['city'] = df_teams_latest['abbreviation'].map(team_city_map)

# Coordenadas fijas para cada ciudad
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

df_teams_latest['latitude'] = df_teams_latest['city'].map(lambda c: city_coords.get(c, (None, None))[0])
df_teams_latest['longitude'] = df_teams_latest['city'].map(lambda c: city_coords.get(c, (None, None))[1])

# Merge jugadores con equipos para obtener porcentaje victorias y coordenadas
df_merged = pd.merge(
    df_players_latest,
    df_teams_latest[['abbreviation', 'win_pct', 'latitude', 'longitude']],
    left_on='tm',
    right_on='abbreviation',
    how='left'
)

# Crear grupos de edad de 3 en 3 años
#df_merged['age_group'] = pd.cut(df_merged['age'], bins=range(18, 46, 3))

# Elegir el grupo de edad que quieres visualizar, por ejemplo 24-27 años
#group_to_show = pd.Interval(left=24, right=27, closed='right')

# Filtrar jugadores entre 20 y 35 años directamente
df_group = df_merged[df_merged['age'].between(20, 35)]


# Agrupar por equipo para obtener promedio de victorias para ese grupo
df_grouped = df_group.groupby(['abbreviation', 'latitude', 'longitude']).agg(
    mean_win_pct=('win_pct', 'mean'),
    count_players=('player', 'count')
).reset_index()

# Crear mapa base
m = folium.Map(location=[39.5, -98.35], zoom_start=4)

# Crear colormap para el porcentaje de victorias
colormap = cm.LinearColormap(['lightgreen', 'green', 'darkgreen'], 
                             vmin=df_grouped['mean_win_pct'].min(), 
                             vmax=df_grouped['mean_win_pct'].max())
colormap.caption = 'Porcentaje promedio de victorias (grupo edad 20-35)'

# Añadir círculos al mapa con popup informativo
for _, row in df_grouped.iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        color = colormap(row['mean_win_pct'])
        radius = 5 + 20 * row['mean_win_pct']  # Tamaño proporcional al porcentaje de victorias
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=(
                f"Equipo: {row['abbreviation']}<br>"
                f"Porcentaje promedio de victorias: {row['mean_win_pct']:.2%}<br>"
                f"Número de jugadores en rango edad: {row['count_players']}"
            ),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1
        ).add_to(m)

# Agregar la leyenda
colormap.add_to(m)

# Guardar el mapa a archivo
m.save("nba_victorias_por_edad_mapa.html")
print("Mapa generado y guardado como nba_victorias_por_edad_mapa.html")
