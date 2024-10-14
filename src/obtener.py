import os
import re
import pandas as pd

def extraer_datos(ruta_archivo):
    """Extrae los datos relevantes de un archivo de resultados de simulación."""
    datos = {}
    with open(ruta_archivo, 'r') as f:
        for linea in f:
            # Expresiones regulares para cada tipo de dato
            match_agentes = re.match(r"Agentes que (.+?): (\d+)", linea)
            match_viajes = re.match(r"Viajes Completados: (\d+)", linea)
            match_destinos = re.match(r"Destinos Completados: (\d+)", linea)
            match_ruta = re.match(r"Ruta (\w+): (\d+) guaguas salieron", linea)
            match_transportados = re.match(r"Ruta (\w+): (\d+) personas fueron transportadas", linea)
            match_llenado = re.match(r"Ruta (\w+): Promedio de llenado: ([\d.]+)%", linea)
            match_tiempo_promedio = re.match(r"Tiempo Promedio de viaje: ([\d.]+)", linea)
            
            if match_agentes:
                datos[match_agentes.group(1)] = int(match_agentes.group(2))
            elif match_viajes:
                datos["Viajes Completados"] = int(match_viajes.group(1))
            elif match_destinos:
                datos["Destinos Completados"] = int(match_destinos.group(1))
            elif match_ruta:
                datos[f"Guaguas Ruta {match_ruta.group(1)}"] = int(match_ruta.group(2))
            elif match_transportados:
                 datos[f"Transportados Ruta {match_transportados.group(1)}"] = int(match_transportados.group(2))
            elif match_llenado:
                datos[f"Llenado Ruta {match_llenado.group(1)}"] = float(match_llenado.group(2))
            elif match_tiempo_promedio:
                datos["Tiempo Promedio de viaje"] = float(match_tiempo_promedio.group(1))
    return datos


def crear_tabla(carpeta_raiz="out"):
    """Crea una tabla con los datos de todas las simulaciones."""
    datos_simulaciones = []
    for root, dirs, files in os.walk(carpeta_raiz):
        for file in files:
            if file == "datos.txt":
                ruta_archivo = os.path.join(root, file)
                datos = extraer_datos(ruta_archivo)
                # Agregar información sobre la simulación (num_agentes, bus_capacity, ruta_inexistente)
                nombre_carpeta = os.path.basename(root)
                parts = nombre_carpeta.split("_")
                datos["num_agentes"] = int(parts[1])
                datos["bus_capacity"] = int(parts[3])
                if "sin" in parts:
                    datos["ruta_inexistente"] = parts[-1]
                else:
                    datos["ruta_inexistente"] = "Ninguna"
                datos_simulaciones.append(datos)


    df = pd.DataFrame(datos_simulaciones)
    return df


if __name__ == "__main__":
    df_resultados = crear_tabla()
    print(df_resultados)
    # Guardar la tabla en un archivo CSV
    df_resultados.to_csv("resultados_simulaciones.csv", index=False)