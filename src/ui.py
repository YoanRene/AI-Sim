import geopandas as gpd
import pandas as pd
import folium
from folium import Choropleth, LayerControl, Marker, FeatureGroup

# Cargar el GeoJSON de La Habana
geojson_path = "data/lha.geojson"  # Asegúrate de tener el archivo GeoJSON
gdf = gpd.read_file(geojson_path)

# Cargar los datos del CSV
df_csv = pd.read_csv("out/output.csv")

# Renombrar los municipios para que coincidan con los del GeoJSON
df_csv = df_csv.rename(columns={
    "Revolution Square": "Plaza de la Revolución"
})

# Transponer el DataFrame para que las horas sean columnas y los municipios sean índices
df_csv = df_csv.set_index("Hora").T

# Crear un GeoDataFrame con los municipios de La Habana y unir los datos del CSV
gdf = gdf.merge(df_csv, left_on="municipality", right_index=True, how="left")

min_val = df_csv.min().min()  # Valor mínimo de todas las horas
max_val = df_csv.max().max()  # Valor máximo de todas las horas

# Crear el mapa base centrado en La Habana
mapa = folium.Map(location=[23.1136, -82.3666], zoom_start=11)

folium.TileLayer('openstreetmap').add_to(mapa)

# Función para agregar una capa choropleth para una hora específica
def agregar_capa(mapa, hora, color):
    Choropleth(
        geo_data=gdf,
        name=f"{hora} min",
        data=gdf,
        columns=["municipality", hora],
        key_on="feature.properties.municipality",  # Asegúrate de que coincida con tu GeoJSON
        fill_color=color,
        fill_opacity=0.7,
        line_opacity=1,
        legend_name=None,
         threshold_scale=[min_val, 
                         max_val * 0.2, 
                         max_val * 0.4, 
                         max_val * 0.6, 
                         max_val * 0.8, 
                         max_val],  # Escala uniforme,
        control=True,
        show=False,
        overlay=False
    ).add_to(mapa)

# Agregar capas para las diferentes horas
horas = df_csv.columns  # Usar las horas del CSV como columnas
cc=0
for hora in horas:
    agregar_capa(mapa, hora, "YlOrRd")

# Ocultar la leyenda de Choropleth
mapa.get_root().header.add_child(folium.Element("""
    <style>
        .legend { display: none; }
    </style>
"""))

# Leer el archivo CSV de paradas
df_paradas = pd.read_csv("data/listaparadas.csv")

# Leer el archivo CSV de rutas
df_rutas = pd.read_csv("data/paradasruta.csv")

# Función para agregar las paradas como marcadores en una capa
def agregar_paradas(mapa, df_paradas):
    paradas_fg = FeatureGroup(name="Paradas", overlay=True, show=False)
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

# Crear una función para agregar una leyenda personalizada
def agregar_leyenda(mapa, min_val, max_val):
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 200px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; padding: 10px;">
    <h4 style='margin-top:0;'>Cantidad de Personas</h4>
    <i style="background: #ffffb2; width: 20px; height: 10px; display: inline-block;"></i> {min_val}<br>
    <i style="background: #fed976; width: 20px; height: 10px; display: inline-block;"></i> {int(min_val + (max_val - min_val) * 0.2)}<br>
    <i style="background: #feb24c; width: 20px; height: 10px; display: inline-block;"></i> {int(min_val + (max_val - min_val) * 0.4)}<br>
    <i style="background: #fd8d3c; width: 20px; height: 10px; display: inline-block;"></i> {int(min_val + (max_val - min_val) * 0.6)}<br>
    <i style="background: #f03b20; width: 20px; height: 10px; display: inline-block;"></i> {int(min_val + (max_val - min_val) * 0.8)}<br>
    <i style="background: #bd0026; width: 20px; height: 10px; display: inline-block;"></i> {max_val}
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legend_html))

# Agregar la leyenda personalizada al mapa
agregar_leyenda(mapa, min_val, max_val)

# Agregar control de capas para alternar entre las horas, rutas y paradas
LayerControl(position='topright').add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save("out/mapa_calor_habana_con_rutas.html")
