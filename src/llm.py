import os
import google.generativeai as genai
import json
from simulation import start_simulation
# from simulation import start_simulation
genai.configure(api_key='AIzaSyCms9w4Pf4MDyfcehjN-c4vYBUj0PNDwP4')

text_input = input("Enter text: ")

model = genai.GenerativeModel("gemini-1.5-flash-latest")
prompt = """Genera un json para crear un archivo de configuracion para una simulación de transporte público. Los valores del json deben estar de acuerdo a los 
requerimientos iniciales entendidos de la siguiente entrada del usuario:
--Input--
"""+text_input+"""
---------
Use this JSON schema:
{
  "openapi": "3.0.0",
  "info": {
    "title": "Simulación de Transporte Público",
    "version": "1.0.0",
    "description": "Configuración para la simulación de transporte público."
  },
  "components": {
    "schemas": {
      "Config": {
        "type": "object",
        "properties": {
          "bus_capacity": {
            "type": "integer",
            "description": "Capacidad de las guaguas (número de pasajeros).",
            "example": 50
          },
          "simulation_time": {
            "type": "integer",
            "description": "Tiempo total de la simulación en segundos.",
            "example": 1440
          },
          "num_agents": {
            "type": "integer",
            "description": "Número de agentes en la simulación.",
            "example": 1000
          },
          "distribution_file": {
            "type": "string",
            "description": "Ruta al archivo CSV con la distribución de destinos.",
            "example": "data/distribucion.csv"
          },
          "houses_file": {
            "type": "string",
            "description": "Ruta al archivo JSON con la distribución de casas por municipio.",
            "example": "data/distribucion.json"
          },
          "output_interval": {
            "type": "integer",
            "description": "Intervalo de tiempo en segundos para guardar los datos.",
            "example": 3600
          },
          "return_probability": {
            "type": "number",
            "format": "float",
            "description": "Probabilidad de que un agente regrese a casa.",
            "example": 0.8
          },
          "departure_intervals": {
            "type": "object",
            "properties": {
              "intervals": {
                "type": "array",
                "items": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                },
                "description": "Intervalos de tiempo en minutos para la salida de agentes.",
                "example": [[0, 180], [180, 300], [300, 540], [540, 660], [660, 900], [900, 1440]]
              },
              "weights": {
                "type": "array",
                "items": {
                  "type": "number",
                  "format": "float"
                },
                "description": "Pesos o probabilidades de cada intervalo de salida.",
                "example": [0.6, 0.15, 0.05, 0.1, 0.05, 0.05]
              }
            }
          },
          "bus_frequencies": {
            "type": "object",
            "additionalProperties": {
              "type": "array",
              "items": {
                "type": "integer"
              },
              "description": "Frecuencia de salida de guaguas por ruta (en minutos)."
            },
            "example": {
              "P1": [10, 20],
              "P2": [5, 15],
              "P3": [10, 20],
              "P4": [18, 36],
              "P5": [20, 40],
              "P6": [15, 30],
              "P7": [15, 30],
              "P8": [12, 24],
              "P9": [12, 24],
              "P10": [8, 16],
              "P11": [7, 14],
              "P12": [20, 40],
              "P13": [25, 50],
              "P14": [22, 44],
              "P15": [11, 22],
              "P16": [15, 30],
              "PC": [9, 18]
            }
          }
        }
      }
    }
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
    "output_interval": 3600,
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
"""
result = model.generate_content(prompt)
print(result.text)
j = result.text.split('```')[1][4:]
json_result = json.loads(j)

# Guardar el JSON en un archivo
with open("generated_config.json", "w") as f:
    json.dump(json_result, f)

# Iniciar la simulación usando el JSON generado
start_simulation("generated_config.json")
# start_simulation()

resultados = get_resultados()

prompt2 = """Dado el input realizado por el usuario:
INPUT:"""+text_input+"""

Se realizo una simulacion completa la cual produjo los siguientes resultados
"""+resultados+"""

Dale una respuesta al usuario teniendo en cuenta esos datos
"""

result = model.generate_content(prompt2)
print(result.text)