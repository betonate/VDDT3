import kagglehub
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
