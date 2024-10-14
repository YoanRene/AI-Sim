import json
import os
from simulation import start_simulation

def generar_config(num_agentes, bus_capacity, ruta_inexistente=None):
    config = {
        "bus_capacity": bus_capacity,
        "simulation_time": 1440,
        "num_agents": num_agentes,
        "distribution_file": "data/distribucion_trabajo.csv",
        "houses_file": "data/distribucion_poblacion.json",
        "output_interval": 60,
        "return_probability": 0.8,
        "departure_intervals": {
            "intervals": [[0, 180], [180, 300], [300, 540], [540, 660], [660, 900], [900, 1440]],
            "weights": [0.6, 0.15, 0.05, 0.1, 0.05, 0.05]
        },
        "bus_frequencies": {
            "P1": [10, 20],
            "P2": [5, 15],
            "P7": [15, 30],
            "P9": [12, 24],
            "P10": [8, 16],
            "P12": [20, 40],
            "P13": [25, 50],
            "P16": [15, 30],
            "P3": [10, 20],
            "P11": [7, 14],
            "P4": [18, 36],
            "P5": [20, 40],
            "P14": [22, 44],
            "P6": [15, 30],
            "P8": [12, 24],
            "PC": [9, 18],
            "P15": [11, 22]
        }
    }
    if ruta_inexistente:
        config["bus_frequencies"][ruta_inexistente] = [1440, 1440]  # No hay guaguas de esta ruta
    return config

def ejecutar_simulaciones():
    num_agentes_values = [500, 1000, 5000]
    bus_capacity_values = [2, 5, 10, 20]
    rutas = ["P1", "P2", "P7", "P9", "P10", "P12", "P13", "P16", "P3", "P11", "P4", "P5", "P14", "P6", "P8", "PC", "P15"]

    for num_agentes in num_agentes_values:
        for bus_capacity in bus_capacity_values:
            # Crear carpeta para la simulación actual
            nombre_carpeta = f"out/sim_{num_agentes}_agentes_{bus_capacity}_capacidad"
            os.makedirs(nombre_carpeta, exist_ok=True)

            # Simulación con todas las rutas
            config = generar_config(num_agentes, bus_capacity)
            ruta_config = os.path.join(nombre_carpeta, "config.json")
            with open(ruta_config, "w") as f:
                json.dump(config, f, indent=4)
            start_simulation(ruta_config, output_dir=nombre_carpeta)


        # Simulaciones con una ruta inexistente
        for ruta in rutas:
            config = generar_config(num_agentes, bus_capacity, ruta)
            nombre_carpeta_ruta = f"out/sim_{num_agentes}_agentes_{bus_capacity}_capacidad_sin_{ruta}"
            os.makedirs(nombre_carpeta_ruta, exist_ok=True)
            ruta_config = os.path.join(nombre_carpeta_ruta, "config.json")
            with open(ruta_config, "w") as f:
                json.dump(config, f, indent=4)
            start_simulation(ruta_config, output_dir=nombre_carpeta_ruta)

if __name__ == "__main__":
    ejecutar_simulaciones()