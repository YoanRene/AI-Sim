import os
import google.generativeai as genai
import json
from simulation import start_simulation
import pandas as pd

genai.configure(api_key='AIzaSyCms9w4Pf4MDyfcehjN-c4vYBUj0PNDwP4')
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
def start_llm():
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
      "distribution_file": "data/distribucion.csv",
      "houses_file": "data/distribucion.json",
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
      "distribution_file": "data/distribucion.csv",
      "houses_file": "data/distribucion.json",
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
      "distribution_file": "data/distribucion.csv",
      "houses_file": "data/distribucion.json",
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

  """+resultados+"""

  Dale una respuesta al usuario teniendo en cuenta esos datos. Haz un analisis estadistico completo con
  los resultados, puedes usar codigo python con pandas y matplotlib para generar un graficos, pero cada imagen
  no se debe mostrar, solo guardar en un archivo .png en cual debe ser referenciado justo debajo del codigo
  en cuestion de la siguiente forma ![Descripción de la imagen](nombre_imagen.png) fuera del bloque de codigo

  Para mas informacion, en promedio los datos con parametros por defecto de la simulacion se comportan de la siguiente manera:
  Hora,Playa,Revolution Square,Centro Habana,La Habana Vieja,Regla,Habana del Este,Guanabacoa,San Miguel del Padrón,Diez de Octubre,Cerro,Marianao,La Lisa,Boyeros,Arroyo Naranjo,Cotorro
60,87,68,58,43,24,81,55,75,90,58,59,66,99,92,37
120,103,84,53,54,23,83,48,68,91,56,61,56,95,82,35
180,119,109,54,63,23,74,40,58,78,66,54,49,97,78,30
240,139,126,60,74,19,59,36,45,65,63,62,42,103,72,27
300,160,137,49,80,21,52,31,43,65,62,53,41,108,64,26
360,173,138,49,85,23,51,29,42,58,63,52,36,104,63,26
420,177,141,46,90,23,51,27,40,58,65,48,37,102,62,25
480,177,144,46,88,24,51,26,40,57,63,47,37,104,62,26
540,179,143,47,88,24,51,25,39,57,63,46,36,104,64,26
600,179,153,45,90,25,48,24,37,55,63,45,33,105,64,26
660,178,161,46,75,25,55,20,38,56,72,48,31,102,62,23
720,168,148,52,76,29,54,22,37,61,73,55,33,94,67,23
780,150,132,57,62,30,59,30,43,68,76,47,39,99,77,23
840,140,125,56,55,31,68,30,47,77,65,56,40,99,76,27
900,136,122,58,54,28,69,36,46,72,67,54,43,99,79,29
960,134,120,57,53,27,66,39,47,76,70,50,43,97,81,32
1020,138,117,56,55,26,66,40,47,78,66,51,46,95,76,35
1080,134,114,59,54,26,67,38,51,76,67,54,46,95,77,34
1140,131,110,55,57,25,66,38,54,80,68,55,50,94,76,33
1200,127,104,61,56,24,69,37,55,82,64,56,51,98,75,33
1260,118,103,59,55,26,69,38,57,76,68,57,52,100,81,33
1320,117,106,58,55,26,69,39,54,80,68,51,50,101,84,34
1380,117,101,60,53,26,71,42,55,82,67,51,50,100,84,33

Estos datos no se encuentran en ningun archivo por tanto deberas usarlos en el codigo.
  """

  result = model.generate_content(prompt2)
  print(result.text)
  open('out/informe.md','w',encoding='utf-8').write(result.text)