import geopandas as gpd
import pandas as pd
import folium
from folium import Choropleth, LayerControl, Marker, FeatureGroup

# Cargar el GeoJSON de La Habana
geojson_path = "data/lha.geojson"  # Asegúrate de tener el archivo GeoJSON
gdf = gpd.read_file(geojson_path)

# Crear un DataFrame con los valores para diferentes horas del día
data = {
    "municipio": ["Playa", "Plaza de la Revolución", "Centro Habana", "La Habana Vieja", "Regla", "Marianao",
                  "Habana del Este", "Guanabacoa", "San Miguel del Padrón", "Arroyo Naranjo", 
                  "Diez de Octubre", "Cerro", "Boyeros", "La Lisa", "Cotorro"],
    "8am": [10, 12, 8, 5, 3, 10, 11, 8, 12, 15, 11, 6, 16, 8, 4],
    "12pm": [15, 14, 10, 6, 4, 12, 13, 10, 14, 18, 13, 7, 19, 10, 5],
    "4pm": [19, 14, 13, 7, 4, 13, 15, 12, 15, 19, 14, 9, 21, 12, 7],
    "8pm": [12, 10, 8, 5, 3, 9, 10, 8, 11, 14, 10, 6, 17, 9, 4]
}

df = pd.DataFrame(data)

# Unir el DataFrame con el GeoDataFrame del GeoJSON basado en el nombre del municipio
gdf = gdf.merge(df, left_on="municipality", right_on="municipio", how="left")

# Crear el mapa base centrado en La Habana
mapa = folium.Map(location=[23.1136, -82.3666], zoom_start=11)

folium.TileLayer('openstreetmap').add_to(mapa)

# Función para agregar una capa choropleth para una hora específica
def agregar_capa(mapa, hora, color):
    Choropleth(
        geo_data=gdf,
        name=hora,
        data=gdf,
        columns=["municipio", hora],
        key_on="feature.properties.municipality",  # Asegúrate de que coincida con tu GeoJSON
        fill_color=color,
        fill_opacity=0.7,
        line_opacity=1,
        legend_name=f"Intensidad del valor por municipio ({hora})",
        control=True,
        show=False,
        overlay=False
    ).add_to(mapa)

# Agregar capas para diferentes horas
agregar_capa(mapa, "8am", "YlOrRd")
agregar_capa(mapa, "12pm", "YlOrRd")
agregar_capa(mapa, "4pm", "YlOrRd")
agregar_capa(mapa, "8pm", "YlOrRd")

# Leer el archivo CSV de paradas
df_paradas = pd.read_csv("data/listaparadas.csv")

# Leer el archivo CSV de rutas
df_rutas = pd.read_csv("data/paradasruta.csv")

# Función para agregar las paradas como marcadores en una capa
def agregar_paradas(mapa, df_paradas):
    paradas_fg = FeatureGroup(name="Paradas", overlay=True, show=True)
    for index, row in df_paradas.iterrows():
        Marker(
            location=[row['Y'], row['X']],
            popup=row['nombre'],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(paradas_fg)
    paradas_fg.add_to(mapa)

# Función para agregar las rutas como líneas en el mapa
def agregar_rutas(mapa, df_rutas, df_paradas):
    color_rutas = {
        1: '#FF0000',  # red
        2: '#008000',  # green
        3: '#0000FF',  # blue
        10: '#808080',  # gray
        11: '#FFA500',  # orange
        302: '#90EE90',  # lightgreen
        303: '#FF00FF',  # magenta
        313: '#A9A9A9',  # darkgray
        314: '#00FFFF',  # cyan
        461: '#008080',  # teal (hexadecimal)
        295: '#00008B',  # darkblue
        298: '#8B0000',  # darkred
        300: '#006400',  # darkgreen
        307: '#FFFF00',  # yellow
        311: '#ADD8E6',  # lightblue
        312: '#800080',  # purple
        455: '#808000'   # olive
    }

    rutas_fg = FeatureGroup(name="Rutas", overlay=True, show=True)

    for idruta in df_rutas['idruta'].unique():
        ruta_paradas = df_rutas[df_rutas['idruta'] == idruta]['codigo']
        
        # Ordenamos las paradas en el orden en que aparecen en la ruta
        coords = df_paradas[df_paradas['codigo'].isin(ruta_paradas)][['Y', 'X', 'codigo']]
        
        # Ordenamos las coordenadas según el orden en 'ruta_paradas'
        coords = coords.set_index('codigo').reindex(ruta_paradas).dropna()[['Y', 'X']].values
        
        # Solo dibujamos la línea si hay al menos dos puntos válidos
        if len(coords) > 1:
            folium.PolyLine(
                coords,
                color=color_rutas.get(idruta, 'black'),
                weight=3,
                opacity=0.8,
                popup=f"Ruta {idruta}"
            ).add_to(rutas_fg)
    rutas_fg.add_to(mapa)

# Imprimir rutas y coordenadas para revisar
for idruta in df_rutas['idruta'].unique():
    ruta_paradas = df_rutas[df_rutas['idruta'] == idruta]['codigo']
    coords = df_paradas[df_paradas['codigo'].isin(ruta_paradas)][['Y', 'X', 'codigo']]
    print(f"Ruta {idruta}: {coords}")

# Agregar paradas y rutas al mapa
agregar_paradas(mapa, df_paradas)
agregar_rutas(mapa, df_rutas, df_paradas)

# Agregar control de capas para alternar entre las horas, rutas y paradas
LayerControl(position='topright').add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save("out/mapa_calor_habana_con_rutas.html")
