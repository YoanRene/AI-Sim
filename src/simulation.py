import heapq
from haversine import haversine
from agent import Agente
from graph import Grafo,cargar_datos
from astar import a_star
from utils import get_random_parada 
import random
import json
import numpy as np
import pandas as pd
import csv
import os

# Cargar configuración desde JSON
def cargar_configuracion(filepath):
    with open(filepath, "r") as f:
        config = json.load(f)
    return config

# Acceder a los parámetros de configuración
def get_config_values(config):
    BUS_CAPACITY = config["bus_capacity"]
    SIMULATION_TIME = config["simulation_time"]
    NUM_AGENTS = config["num_agents"]
    DISTRIBUTION_FILE = config["distribution_file"]
    HOUSES_FILE = config["houses_file"]
    OUTPUT_INTERVAL = config["output_interval"]
    # Probabilidad de que un agente regrese a casa (del 0 al 1)
    RETURN_PROBABILITY = config["return_probability"]

    # Intervalos de tiempo de salida y sus pesos
    DEPARTURE_INTERVALS = config["departure_intervals"]["intervals"]
    DEPARTURE_WEIGHTS = config["departure_intervals"]["weights"]

    # Frecuencia de salida de guaguas por ruta (en minutos)
    BUS_FREQUENCIES = config.get("bus_frequencies", {})  # Diccionario ruta:frecuencia
    return BUS_CAPACITY, SIMULATION_TIME, NUM_AGENTS, DISTRIBUTION_FILE, HOUSES_FILE, OUTPUT_INTERVAL, RETURN_PROBABILITY, DEPARTURE_INTERVALS, DEPARTURE_WEIGHTS, BUS_FREQUENCIES


def cargar_distribucion(filepath):
    distribucion = pd.read_csv(filepath)
    return distribucion

def obtener_destino(municipio_origen, distribucion):
    destinos = distribucion.columns[1:-1]  # Ignorar la primera columna y la última
    porcentajes = distribucion.loc[distribucion['Municipio de Residencia'] == municipio_origen].values[0][1:-1]
    return random.choices(destinos, weights=porcentajes, k=1)[0]
class Evento:
    def __init__(self, event_name, time, args):
        self.event_name = event_name
        self.time = time
        self.args = args
    def __lt__(self, other):
        return self.time <= other.time

class Guagua:
    def __init__(self,id, ruta):
        self.id=id
        self.ruta = ruta
        self.position = 0
        self.pasajeros = []

    def has_capacity(self):
        return len(self.pasajeros) < BUS_CAPACITY  # Assuming a capacity of 50

def simulacion(grafo, num_agentes, tiempo_max, config, output_dir="out"):
    """
    Simula un sistema de transporte público con agentes que viajan en guaguas
    entre paradas.

    Args:
        grafo: Grafo que representa el sistema de transporte público.
        num_agentes: Número de agentes que se inicializarán en la simulación.
        tiempo_max: Tiempo máximo de simulación en segundos.
        config: Diccionario con la configuración de la simulación
    """
    global BUS_CAPACITY, SIMULATION_TIME, NUM_AGENTS, DISTRIBUTION_FILE, HOUSES_FILE, OUTPUT_INTERVAL, RETURN_PROBABILITY, DEPARTURE_INTERVALS, DEPARTURE_WEIGHTS, BUS_FREQUENCIES
    BUS_CAPACITY, SIMULATION_TIME, NUM_AGENTS, DISTRIBUTION_FILE, HOUSES_FILE, OUTPUT_INTERVAL, RETURN_PROBABILITY, DEPARTURE_INTERVALS, DEPARTURE_WEIGHTS, BUS_FREQUENCIES = get_config_values(config)
    eventos = []
    current_time = 0
    os.makedirs(output_dir, exist_ok=True)
    print(f"Iniciando simulación con {num_agentes} agentes durante {tiempo_max} segundos")
    agentes = []
    municipios_inicio= {}
    distribucion = cargar_distribucion('data/distribucion_trabajo.csv')
    houses = json.load(open('data/distribucion_poblacion.json',encoding='utf-8'))['house']
    # Inicialización
    agentes_tempranos = 0
    # heapq.heappush(eventos, Evento("person_arrival", 66, Agente(-1, grafo.get_parada('2773'), grafo.get_parada('3449'),True)))
    t = sum(houses.values())
    for i in distribucion["Municipio de Residencia"]:
        for j in range(houses[i]//(t//num_agentes)):
            origen = get_random_parada(grafo, i)
            if origen.county not in municipios_inicio:
                municipios_inicio[origen.county] = 0
            municipios_inicio[origen.county] += 1

            # Obtener el municipio de destino basado en la distribución
            municipio_destino = obtener_destino(i, distribucion)
            destino = get_random_parada(grafo, municipio_destino,origen)
            agente = Agente(f'{i}-{j}', origen, destino,random.random()<=RETURN_PROBABILITY)
            agentes.append(agente)

            s,e = random.choices(DEPARTURE_INTERVALS,DEPARTURE_WEIGHTS)[0]
            time_get_out = random.randint(s,e)
            if time_get_out <=900:
                agentes_tempranos+=1
            agente.salida = time_get_out
            evento = Evento("person_arrival", time_get_out, agente)
            heapq.heappush(eventos, evento)
    # Inicializar guaguas
    guaguas_por_ruta = {}
    personas_transportadas_por_ruta = {}
    for ruta in grafo.rutas:
        ruta_id = ruta[0][2] # Obtener el ID de la ruta
        guaguas_por_ruta[ruta_id] = 0
        personas_transportadas_por_ruta[ruta_id] = 0
        frequency = BUS_FREQUENCIES.get(ruta_id, (15, 60)) # Obtener la frecuencia o usar el valor por defecto (15, 60)
        if len(frequency)==1:
            new_guagua = Evento(
                "init_bus", current_time + frequency[0], (ruta,frequency)
            )
        else:
            min_freq, max_freq = frequency  # Obtener los valores mínimo y máximo de la frecuencia
            new_guagua = Evento(
                "init_bus", current_time + random.randint(min_freq, max_freq), (ruta,frequency)
            )
        
        # evento = Evento("init_bus", current_time, (ruta, frequency)) # Pasar la frecuencia junto con la ruta
        heapq.heappush(eventos, new_guagua)
    agentes_llegan_trabajo = 0
    agentes_regresan_casa = 0
    agentes_destino = 0
    agente_bien = 0 

    agentes_regresan_impaciencia = 0
    agentes_carro = 0
    agentes_caimando = 0
    
    personas_rechazadas_por_lleno = 0
    promedio_llenado_rutas = {}

    # Crear un diccionario para almacenar los datos de la simulación
    datos_simulacion = {}

    #Evento para guardar los datos cada una hora para hacer analisis
    evento = Evento("save_data",current_time+OUTPUT_INTERVAL,(datos_simulacion, municipios_inicio))
    heapq.heappush(eventos,evento)

    # Bucle principal de simulación
    while eventos and current_time < tiempo_max:
        
        evento = heapq.heappop(eventos)
        current_time = evento.time

        if evento.event_name == "person_arrival":
            """
            Un agente llega a una parada y decide qué guagua tomar.
            """
            agente = evento.args
            if 'salir de casa' in agente.intenciones or 'salir del trabajo' in agente.intenciones:
                agente.elegir_ruta(grafo)
                agente.cursor_parada=0
                agente.cursor_ruta=1
                agente.actualizar_creencias(current_time,evento,grafo)
            else:
                if agente.repite:
                    agente.repite=False
                else:
                    agente.cursor_parada+=1
            if agente.en_destino():
                agentes_destino+=1
                if agente.llegada == -1:
                    agente_bien +=1
                
                if agente.regreso_a_casa():
                    agentes_regresan_casa+=1
                else:
                    agentes_llegan_trabajo +=1
                    agente.llegada = current_time
                    if agente.intenta_regresar(current_time):
                        tiempo_regreso = agente.tiempo_regreso
                        evento = Evento('person_arrival',tiempo_regreso,agente)
                        heapq.heappush(eventos,evento)
            else:
                # print(f"Agente {agente.id} llegó{' a pie' if agente.intenciones[1][1] == 'pie' else ''} a la parada {agente.creencias['parada_actual']}")
                proxima_guagua = agente.proxima_guagua()  # Asumiendo que intenciones[1] es (parada, guagua)

                if proxima_guagua == "pie":
                    # Cuando tiene que ir para la proxima parada a pie
                    tiempo = agente.mueve_parada()
                    #Creamos el evento de llegada a la proxima parada
                    evento_person_arrival = Evento("person_arrival", current_time+tiempo, agente)
                    #Lo agregamos al heap
                    heapq.heappush(eventos, evento_person_arrival)
                else:
                    if proxima_guagua not in agente.parada_actual().colas:
                        agente.parada_actual().colas[proxima_guagua]=[]
                    agente.parada_actual().colas[proxima_guagua].append(agente)
                    agente.recalcula_impaciencia(current_time)

        elif evento.event_name == "init_bus":
            """
            Se inicializa una guagua en una ruta.
            """
            ruta, frequency = evento.args
            if(len(ruta)<1):
                continue
            guagua = Guagua(ruta[0][1],ruta)
            evento_siguiente = Evento("next_stop", current_time, guagua)
            heapq.heappush(eventos, evento_siguiente)
            guaguas_por_ruta[ruta[0][2]] += 1  # Incrementa el contador de guaguas por ruta
            if len(frequency)==1:
                new_guagua = Evento(
                "init_bus", current_time + frequency[0], (ruta,frequency)
            )
            else:
                min_freq, max_freq = frequency  # Obtener los valores mínimo y máximo de la frecuencia
                new_guagua = Evento(
                    "init_bus", current_time + random.randint(min_freq, max_freq), (ruta,frequency)
                )
            heapq.heappush(eventos, new_guagua)
        elif evento.event_name == "next_stop":
            """
            La guagua llega a una parada y sube/baja pasajeros.
            """
            guagua = evento.args
            parada_actual = guagua.ruta[guagua.position][0]
            if(not parada_actual):
                continue
            ruta_id = guagua.ruta[0][2]  # Obtener el ID de la ruta
            # Bajar pasajeros
            for pasajero in guagua.pasajeros:
                pasajero.mueve_parada(parada_actual)
               
                if pasajero.proxima_bajada() == parada_actual or guagua.position == len(guagua.ruta)-1:
                    pasajero.in_guagua = False
                    if not pasajero.en_destino():
                        pasajero.repite=guagua.position == len(guagua.ruta)-1 and not pasajero.proxima_bajada() == parada_actual
                        evento_person_arrival = Evento("person_arrival", current_time, pasajero)
                        heapq.heappush(eventos, evento_person_arrival)
                    else:
                        agentes_destino+=1
                        if pasajero.llegada == -1:
                            agente_bien +=1
                        if pasajero.regreso_a_casa():
                            agentes_regresan_casa+=1
                        else:
                            pasajero.llegada = current_time
                            if pasajero.regresa:
                                evento = Evento('person_arrival',current_time,pasajero)
                                heapq.heappush(eventos,evento)
                        print(f"Agente {pasajero.id} llegó a su destino en {parada_actual.nombre}")

            guagua.pasajeros = [p for p in guagua.pasajeros if p.proxima_bajada() != parada_actual and guagua.position != len(guagua.ruta)-1]

            # Subir pasajeros
            while guagua.has_capacity() and (guagua.id in parada_actual.colas) and len(parada_actual.colas[guagua.id])>0 and guagua.position < len(guagua.ruta) - 1:
                pasajero = parada_actual.colas[guagua.id].pop(0)
                pasajero.tiempo_impaciencia =-1
                pasajero.in_guagua = True
                guagua.pasajeros.append(pasajero)
                personas_transportadas_por_ruta[ruta_id] += 1  # Incrementa el contador de personas por ruta

            # Controlar si alguien se queda en la parada porque el bus está lleno
            if (guagua.id in parada_actual.colas) and len(parada_actual.colas[guagua.id])>0 and guagua.position < len(guagua.ruta) - 1:
                personas_rechazadas_por_lleno += len(parada_actual.colas[guagua.id])

            # Calcular el porcentaje de llenado del bus
            porcentaje_llenado = len(guagua.pasajeros) / BUS_CAPACITY * 100
            if ruta_id not in promedio_llenado_rutas:
                promedio_llenado_rutas[ruta_id] = []
            promedio_llenado_rutas[ruta_id].append(porcentaje_llenado)

            guagua.position += 1
            if guagua.position < len(guagua.ruta):
                tiempo_viaje = 10  * haversine((parada_actual.x,parada_actual.y),(guagua.ruta[guagua.position][0].x,guagua.ruta[guagua.position][0].y))
                evento_siguiente = Evento("next_stop", current_time + tiempo_viaje, guagua)
                heapq.heappush(eventos, evento_siguiente)
            
        elif evento.event_name == "save_data":
            #Programamos el evento para la proxima hora
            datos_simulacion, municipios_inicio = evento.args
            evento = Evento("save_data",current_time+OUTPUT_INTERVAL,(datos_simulacion, municipios_inicio))
            heapq.heappush(eventos,evento)

            #Guardamos datos
            municipios = {}
            for agente in agentes:
                if agente.parada_actual().county not in municipios:
                    municipios[agente.parada_actual().county] = 0
                municipios[agente.parada_actual().county] +=1

            datos_simulacion[current_time] = municipios
        
        for agente in agentes:
            ev =  agente.actualizar_creencias(current_time,evento,grafo)
            if ev:
                heapq.heappush(eventos,Evento(ev[0],ev[1],ev[2]))
        print(current_time,end='\r')
            
    with open(os.path.join(output_dir, 'output.csv'), 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Obtener la lista de municipios de los datos iniciales (o de cualquier hora en datos_simulacion)
        municipios = list(municipios_inicio.keys())
        # Escribir la primera fila con los nombres de los municipios
        writer.writerow(['Hora'] + municipios)
        
        # Escribir los datos de cada hora
        for hora, datos_hora in sorted(datos_simulacion.items()):
            fila = [hora] + [datos_hora.get(municipio, 0) for municipio in municipios]
            writer.writerow(fila)

    print(f"\n\nSimulación con {len(agentes)} agentes completada:\n Agentes que llegaron al trabajo:", agentes_llegan_trabajo)
    print(" Agentes que regresaron a la casa:",agentes_regresan_casa)
    print(" Agentes que salieron para el trabajo antes de las 9pm:",agentes_tempranos)
    print(" Viajes Completados:",agentes_destino)
    print(" Destinos Completados:",agente_bien)
    print(" Agentes que regresaron a la casa sin llegar al trabajo:",agentes_regresan_impaciencia)
    print(" Agentes que se van en carro:",agentes_carro)
    print(" Agentes que se van caminando:",agentes_caimando)
    print(" Personas rechazadas por buses llenos:", personas_rechazadas_por_lleno)

    # Guardar datos de la simulación en un archivo
    with open(os.path.join(output_dir, "datos.txt"), "w") as f:
        f.write(f"Agentes que llegaron al trabajo: {agentes_llegan_trabajo}\n")
        f.write(f"Agentes que regresaron a la casa: {agentes_regresan_casa}\n")
        f.write(f"Agentes que salieron para el trabajo antes de las 9pm: {agentes_tempranos}\n")
        f.write(f"Viajes Completados: {agentes_destino}\n")
        f.write(f"Destinos Completados: {agente_bien}\n")
        f.write(f"Agentes que regresaron a la casa sin llegar al trabajo: {agentes_regresan_impaciencia}\n")
        f.write(f"Agentes que se van en carro: {agentes_carro}\n")
        f.write(f"Agentes que se van caminando: {agentes_caimando}\n")
        f.write(f"Personas rechazadas por buses llenos: {personas_rechazadas_por_lleno}\n")

        # Imprimir estadísticas de las rutas
        for ruta_id, cantidad_guaguas in guaguas_por_ruta.items():
            f.write(f"Ruta {ruta_id}: {cantidad_guaguas} guaguas salieron\n")
            f.write(f"Ruta {ruta_id}: {personas_transportadas_por_ruta[ruta_id]} personas fueron transportadas\n")
            if ruta_id in promedio_llenado_rutas:
                promedio_llenado = np.mean(promedio_llenado_rutas[ruta_id])
                f.write(f"Ruta {ruta_id}: Promedio de llenado: {promedio_llenado:.2f}%\n")

        time_of_travel = 0
        municipios = {}
        for agente in agentes:
            if agente.en_destino():
                time_of_travel += agente.llegada-agente.salida
                if agente.creencias['parada_actual'].county not in municipios:
                    municipios[agente.creencias['parada_actual'].county] = 0
                municipios[agente.creencias['parada_actual'].county] +=1

        print(f'\nTiempo Promedio de viaje: {time_of_travel/agentes_llegan_trabajo}\n')
        f.write(f'Tiempo Promedio de viaje: {time_of_travel/agentes_llegan_trabajo}\n')
    for k,v in municipios.items():
        print(f'Municipio {k} tiene {municipios_inicio[k] if k in municipios_inicio else 0} agentes al pricipio y {v} al final')
    for parada in grafo.vertices.values():
        personas_en_cola = sum(len(colas) for colas in parada.colas.values())
        if personas_en_cola>0:
            print(f"Parada {parada} tiene {personas_en_cola} personas en cola")
def start_simulation(config_filepath, output_dir="out"):
    # Cargar configuración desde el archivo JSON
    config = cargar_configuracion(config_filepath)

    # Crear el grafo
    grafo=Grafo()
    cargar_datos(grafo)

    # Iniciar la simulación
    simulacion(grafo, num_agentes=config["num_agents"], tiempo_max=config["simulation_time"], config=config,output_dir=output_dir)
# Uso en la simulación
if __name__ == '__main__':
    start_simulation("data/config.json")  # Simular utilizando el archivo "config.json"