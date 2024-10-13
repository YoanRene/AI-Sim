import os
import google.generativeai as genai
import json
from simulation import start_simulation
import pandas as pd

def cargar_resultados(ruta_csv):
  """Carga los resultados del archivo CSV y los formatea para el LLM.

  Args:
    ruta_csv: La ruta al archivo CSV con los resultados.

  Returns:
    Un string con los resultados formateados para el LLM.
  """
  df = pd.read_csv(ruta_csv)

  # Convertir el DataFrame a un string con formato tabular
  resultados_formateados = df.to_string(index=False, header=True)

  return resultados_formateados

# from simulation import start_simulation
genai.configure(api_key='AIzaSyCms9w4Pf4MDyfcehjN-c4vYBUj0PNDwP4')

text_input = input("Enter text: ")

model = genai.GenerativeModel("gemini-1.5-flash-latest")
prompt = """Genera un json para crear un archivo de configuracion para una simulación de transporte público. Los valores del json deben estar de acuerdo a los 
requerimientos iniciales entendidos de la siguiente entrada del usuario:
INPUT:"""+text_input+"""
---------
Use this JSON schema:
{
  {
    "bus_capacity": "INT, Representa la capacidad de cada obnibus,
    "simulation_time": "INT, Representa el tiempo de simulación en minutos,
    "num_agents": "INT, Representa el número de agentes,
    "distribution_file": "STRING, Ruta al CSV que define la distribución de agentes en cada municipio,
    "houses_file": "STRING, Ruta al JSON que define la ubicación de las casas,",
    "output_interval": "INT, Representa el intervalo de tiempo en que se guardan los resultados en el archivo CSV,
    "return_probability": "FLOAT, Representa la probabilidad de que un agente regrese a casa (del 0 al 1),
    "departure_intervals": {
      "intervals": [[0, 180], [180, 300], [300, 540], [540, 660], [660, 900], [900, 1440]],
      "weights": [0.6, 0.15, 0.05, 0.1, 0.05, 0.05]
    },
    "bus_frequencies": {
      "P1": Representa el intervalo de salida de la ruta en cuestion
      "P2": Representa el intervalo de salida de la ruta en cuestion
      "P7": Representa el intervalo de salida de la ruta en cuestion
      "P9": Representa el intervalo de salida de la ruta en cuestion
      "P10":Representa el intervalo de salida de la ruta en cuestion
      "P12":Representa el intervalo de salida de la ruta en cuestion,
      "P13":Representa el intervalo de salida de la ruta en cuestion,
      "P16":Representa el intervalo de salida de la ruta en cuestion,
      "P3": Representa el intervalo de salida de la ruta en cuestion
      "P11":Representa el intervalo de salida de la ruta en cuestion
      "P4": Representa el intervalo de salida de la ruta en cuestion
      "P5": Representa el intervalo de salida de la ruta en cuestion
      "P14":Representa el intervalo de salida de la ruta en cuestion,
      "P6": Representa el intervalo de salida de la ruta en cuestion
      "P8": Representa el intervalo de salida de la ruta en cuestion
      "PC": Representa el intervalo de salida de la ruta en cuestion
      "P15":Representa el intervalo de salida de la ruta en cuestion
    }
  }
}

VALORES POR DEFECTO:
{
    "bus_capacity": 50,
    "simulation_time": 1440, 
    "num_agents": 1000,
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

EXAMPLE:
input: que pasaria si son 1500 agentes y solo hay p11
output:
{
    "bus_capacity": 50,
    "simulation_time": 1440, 
    "num_agents": 1500,
    "distribution_file": "data/distribucion_trabajo.csv",
    "houses_file": "data/distribucion_poblacion.json",
    "output_interval": 60,
    "return_probability": 0.8,
    "departure_intervals": {
      "intervals": [[0, 180], [180, 300], [300, 540], [540, 660], [660, 900], [900, 1440]],
      "weights": [0.6, 0.15, 0.05, 0.1, 0.05, 0.05]
    },
    "bus_frequencies": {
      "P1": [1440, 1440],
      "P2": [1440, 1440],
      "P7": [1440, 1440],
      "P9": [1440, 1440],
      "P10": [1440, 1440],
      "P12": [1440, 1440],
      "P13": [1440, 1440],
      "P16": [1440, 1440],
      "P3": [1440, 1440],
      "P11": [7, 14],
      "P4": [1440, 1440],
      "P5": [1440, 1440],
      "P14": [1440, 1440],
      "P6": [1440, 1440],
      "P8": [1440, 1440],
      "PC": [1440, 1440],
      "P15": [1440, 1440]
    }
  }

observacion: Solo se modificaron los valores necesarios para el input del usuario, el resto permanece como en el ejemplo, los valores de rango de las guaguas que no salen se establecen en el valor de tiempo de simulacion 

EXAMPLE 2:
input: Como influiria en la poblacion de Habana del Este el hecho de que no hayan P1 circulando
output:
{
    "bus_capacity": 50,
    "simulation_time": 1440, 
    "num_agents": 1000,
    "distribution_file": "data/distribucion_trabajo.csv",
    "houses_file": "data/distribucion_poblacion.json",
    "output_interval": 3600,
    "return_probability": 0.8,
    "departure_intervals": {
      "intervals": [[0, 180], [180, 300], [300, 540], [540, 660], [660, 900], [900, 1440]],
      "weights": [0.6, 0.15, 0.05, 0.1, 0.05, 0.05]
    },
    "bus_frequencies": {
      "P1": [1440, 1440],
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

observacion: Solo se modificaron los valores necesarios para el input del usuario, el resto permanece como en el ejemplo, los valores de rango de las guaguas que no salen se establecen en el valor de tiempo de simulacion 

INPUT:
"""+text_input
result = model.generate_content(prompt)
print(result.text)
j = result.text.split('```')[1][4:]
json_result = json.loads(j)

# Guardar el JSON en un archivo
with open("out/generated_config.json", "w") as f:
    json.dump(json_result, f)

# Iniciar la simulación usando el JSON generado
start_simulation("out/generated_config.json")
# start_simulation()

resultados_formateados = cargar_resultados("out/output.csv")
resultados = ""
with open("out/output.csv", "r") as f:
    resultados = f.read()

print(resultados_formateados)

prompt2 = """Dado el input realizado por el usuario:
INPUT:"""+text_input+"""

Se realizo una simulacion completa la cual produjo los siguientes resultados:
La siguiente tabla muestra la distribucion de personas por municipios durante las 24 horas del dia.
La simulacion empieza a las 6am y termina a las 6am del dia anterior, los tiempos son en minutos,
es decir, 60 seria que paso una hora de simulacion, por tanto serian las 7am.

La simulacion empieza a las 6 de la manana
6am => 0
9am => 180
11am => 300
3pm => 540
5pm => 660
9pm => 900
6am => 1,440

"""+resultados+"""

Dale una respuesta al usuario teniendo en cuenta esos datos
"""

result = model.generate_content(prompt2)
print(result.text)