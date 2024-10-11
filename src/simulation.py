import heapq
from agent import Agente
from graph import Grafo,cargar_datos
from astar import a_star
from utils import get_random_parada 
import random
import json
import numpy as np
import pandas as pd

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
        return len(self.pasajeros) < 500  # Assuming a capacity of 50

def simulacion(grafo, num_agentes, tiempo_max):
    """
    Simula un sistema de transporte público con agentes que viajan en guaguas
    entre paradas.

    Args:
        grafo: Grafo que representa el sistema de transporte público.
        num_agentes: Número de agentes que se inicializarán en la simulación.
        tiempo_max: Tiempo máximo de simulación en segundos.
    """
    eventos = []
    current_time = 0

    print(f"Iniciando simulación con {num_agentes} agentes durante {tiempo_max} segundos")
    agentes = []
    municipios_inicio= {}
    distribucion = cargar_distribucion('data/distribucion.csv')
    houses = json.load(open('data/distribucion.json',encoding='utf-8'))['house']
    # Inicialización
    agentes_tempranos = 0
    heapq.heappush(eventos, Evento("person_arrival", 66, Agente(-1, grafo.get_parada('1867'), grafo.get_parada('2682'),True)))
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
            agente = Agente(f'{i}-{j}', origen, destino,random.random()<=0.8)
            agentes.append(agente)

            s,e = random.choices([(0,180),(180,300),(300,540),(540,660),(660,900),(900,1440)],[0.6,0.15,0.05,0.1,0.05,0.05])[0]
            time_get_out = random.randint(s,e)
            if time_get_out <=900:
                agentes_tempranos+=1
            agente.salida = time_get_out
            evento = Evento("person_arrival", time_get_out, agente)
            heapq.heappush(eventos, evento)
    # Inicializar guaguas
    for ruta in grafo.rutas:
        evento = Evento("init_bus", current_time, ruta)
        heapq.heappush(eventos, evento)
    agentes_llegan_trabajo = 0
    agentes_regresan_casa = 0
    agentes_destino = 0
    agente_bien = 0 

    agentes_regresan_impaciencia = 0
    agentes_carro = 0
    agentes_caimando = 0
    #Evento para guardar los datos cada una hora para hacer analisis
    evento = Evento("save_data",current_time+60,None)
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
            if(len(agente.intenciones)==0):
                agente.elegir_ruta(grafo)
                agente.creencias["cursor_parada"]=0
                agente.creencias["cursor_ruta"]=1
            else:
                if agente.creencias['repite']:
                    agente.creencias['repite']=False
                else:
                    agente.creencias["cursor_parada"]+=1
                # if agente.creencias["parada_actual"] != agente.creencias["destino"]:
                #     if agente.creencias["cursor_ruta"] >= len(agente.intenciones):
                #         agente.creencias["cursor_ruta"]=1
                #         agente.creencias['cursor_parada']=0
                        # agente.elegir_ruta(grafo)
            if agente.creencias["parada_actual"] == agente.creencias["destino"]:
                agentes_destino+=1
                if agente.llegada == -1:
                    agente_bien +=1
                print(f"Agente {agente.id} llegó su destino en {agente.creencias['parada_actual']}")
                if agente.creencias['destino']==agente.creencias['parada_origen']:
                    agentes_regresan_casa+=1
                else:
                    agentes_llegan_trabajo +=1
                    agente.llegada = current_time
                    if agente.creencias["regresa"]:
                        #Si el agente regresa a casa lo hace con mayor probabilidad en el horario de 4-6
                        #A no ser que no llege a un minimo de 6 horas de trabajo
                        tiempo_regreso = current_time + 6*60
                        #Si las 6 horas se cumplen antes de las 4 de la tarde sale en ese rango
                        if tiempo_regreso <= 600:
                            tiempo_regreso = random.randint(600,720)
                        else:
                            #Si no regresa en un rango de hasta 3 horas 
                            #Es decir la jornada laboral seria de 6-9 horas
                            tiempo_regreso += random.randint(0,120)
                        #Actualizamos las creencias del agente
                        agente.creencias["destino"]=agente.creencias["parada_origen"]
                        agente.creencias['regresa']=False
                        agente.intenciones = []
                        agente.creencias["cursor_parada"]=0
                        agente.creencias["cursor_ruta"]=1
                        evento = Evento('person_arrival',tiempo_regreso,agente)
                        heapq.heappush(eventos,evento)
                continue
            if(len(agente.intenciones)<2):
                continue

            # print(f"Agente {agente.id} llegó{' a pie' if agente.intenciones[1][1] == 'pie' else ''} a la parada {agente.creencias['parada_actual']}")
            proxima_guagua = agente.intenciones[agente.creencias["cursor_ruta"]][1]  # Asumiendo que intenciones[1] es (parada, guagua)

            if proxima_guagua == "pie":
                # Cuando tiene que ir para la proxima parada a pie
                #Actualizamos sus creencias
                agente.creencias["parada_actual"] = agente.intenciones[agente.creencias["cursor_ruta"]][0]
                agente.creencias["cursor_ruta"]+=1
                #Creamos el evento de llegada a la proxima parada
                #TODO: Cambiar el +10 por alguna metrica que tenga que ver con la distancia entre paradas.
                evento_person_arrival = Evento("person_arrival", current_time+10, agente)
                #Lo agregamos al heap
                heapq.heappush(eventos, evento_person_arrival)
                continue

            if proxima_guagua not in agente.creencias["parada_actual"].colas:
                agente.creencias["parada_actual"].colas[proxima_guagua]=[]
            agente.creencias["parada_actual"].colas[proxima_guagua].append(agente)
            tiempo_impaciencia = agente.preferencias['paciencia'] * random.randint(60,120)
            agente.tiempo_impaciencia =current_time+tiempo_impaciencia
            evento = Evento('impaciencia',current_time+tiempo_impaciencia,(agente,agente.creencias['parada_actual']))
            heapq.heappush(eventos,evento)
        
        elif evento.event_name=="impaciencia":
            agente, parada = evento.args
            if agente.in_guagua or parada != agente.creencias['parada_actual'] or current_time!= agente.tiempo_impaciencia:
                continue
            # print("Impaciento")
            if(agente.preferencias["laboriosidad"]<0.4 and agente.creencias["regresa"]):
                #Regresa a la casa
                agentes_regresan_impaciencia +=1
                agente.creencias["destino"]=agente.creencias["parada_origen"]
            #Sale de la parada
            agente.creencias['parada_actual'].colas[agente.intenciones[agente.creencias["cursor_ruta"]][1]].remove(agente)
            agente.creencias['parada_actual']=agente.creencias['destino']
            if(0.3*agente.preferencias["condicion_fisica"]+0.7*agente.preferencias["ganancias"]>0.6):
                #Coge un carro para el destino
                agentes_carro+=1
                evento_destino = Evento("person_arrival", current_time+10, agente) 
            else:
                #Caminando
                agentes_caimando+=1
                evento_destino = Evento("person_arrival", current_time+40, agente) 
            heapq.heappush(eventos, evento_destino)

        elif evento.event_name == "init_bus":
            """
            Se inicializa una guagua en una ruta.
            """
            ruta = evento.args
            if(len(ruta)<1):
                continue
            guagua = Guagua(ruta[0][1],ruta)
            evento_siguiente = Evento("next_stop", current_time, guagua)
            heapq.heappush(eventos, evento_siguiente)
            #Iniciamos una nueva guagua en un tiempo aleatorio
            # next_time = np.random.exponential(rutas_config[guagua.id])
            new_guagua = Evento('init_bus',current_time + random.randint(15,60),ruta)
            heapq.heappush(eventos,new_guagua)
        elif evento.event_name == "next_stop":
            """
            La guagua llega a una parada y sube/baja pasajeros.
            """
            guagua = evento.args
            parada_actual = guagua.ruta[guagua.position][0]
            if(not parada_actual):
                continue
            #se monta en 3187 hasta el 2668
            # Bajar pasajeros
            pasajeros_antes = len(guagua.pasajeros)
            for pasajero in guagua.pasajeros:
                pasajero.creencias["cursor_ruta"]+=1
                pasajero.creencias["parada_actual"] = parada_actual
                if pasajero.creencias['parada_actual'] != pasajero.intenciones[pasajero.creencias["cursor_ruta"]-1][0] :
                    print('pp')
                if parada_actual not in [x for x,_ in pasajero.intenciones]:
                    print("Mango")
               
                if pasajero.creencias["paradas_next"][pasajero.creencias["cursor_parada"]] == parada_actual or guagua.position == len(guagua.ruta)-1:
                    pasajero.in_guagua = False
                    if pasajero.creencias["destino"] != parada_actual:
                        pasajero.creencias["repite"]=guagua.position == len(guagua.ruta)-1 and not pasajero.creencias["paradas_next"][pasajero.creencias["cursor_parada"]] == parada_actual
                        evento_person_arrival = Evento("person_arrival", current_time-0.01, pasajero)
                        heapq.heappush(eventos, evento_person_arrival)
                    else:
                        agentes_destino+=1
                        if pasajero.llegada == -1:
                            agente_bien +=1
                        if pasajero.creencias['destino']==pasajero.creencias['parada_origen']:
                            agentes_regresan_casa+=1
                        else:
                            agentes_llegan_trabajo +=1
                            pasajero.llegada = current_time
                            if pasajero.creencias["regresa"]:
                                evento = Evento('person_arrival',current_time,pasajero)
                                heapq.heappush(eventos,evento)
                        print(f"Agente {pasajero.id} llegó a su destino en {parada_actual.nombre}")
                        pass
            guagua.pasajeros = [p for p in guagua.pasajeros if p.creencias["paradas_next"][p.creencias["cursor_parada"]] != parada_actual and guagua.position != len(guagua.ruta)-1]
            pasajeros_bajados = pasajeros_antes - len(guagua.pasajeros)
            if(pasajeros_bajados>0):
                print(f"Pasajeros bajados en {parada_actual.nombre}: {pasajeros_bajados}")
            
            # Subir pasajeros
            pasajeros_subidos = 0
            while guagua.has_capacity() and (guagua.id in parada_actual.colas) and len(parada_actual.colas[guagua.id])>0 and guagua.position < len(guagua.ruta) - 1:
                pasajero = parada_actual.colas[guagua.id].pop(0)
                pasajero.tiempo_impaciencia =-1
                pasajero.in_guagua = True
                guagua.pasajeros.append(pasajero)
                pasajeros_subidos += 1
            
            #Si la guagua tiene capacidad el resto de los pasajeros en la parada se lo piensa
            if guagua.has_capacity() and guagua.position < len(guagua.ruta) - 1:
                for cola in parada_actual.colas.values():
                    for pasajero in cola:
                        if not guagua.has_capacity():
                            break
                        if pasajero.piensa_cambiar_ruta(grafo,guagua):
                            pasajero.tiempo_impaciencia =-1

                            pasajero.in_guagua =True
                            guagua.pasajeros.append(pasajero)
                            cola.remove(pasajero)

            guagua.position += 1
            if guagua.position < len(guagua.ruta):
                tiempo_viaje = 10  # Tiempo fijo entre paradas, podría ser variable
                evento_siguiente = Evento("next_stop", current_time + tiempo_viaje, guagua)
                heapq.heappush(eventos, evento_siguiente)
            else:
                # La guagua ha completado su ruta, reiniciar
                # guagua.position = 0
                # evento_reinicio = Evento("init_bus", current_time, guagua.ruta)
                # heapq.heappush(eventos, evento_reinicio)
                pass
            
        elif evento.event_name == "save_data":
            #Programamos el evento para la proxima hora
            evento = Evento("save_data",current_time+60,None)
            heapq.heappush(eventos,evento)

            #Guardamos datos
            municipios = {}
            for agente in agentes:
                if agente.creencias['parada_actual'].county not in municipios:
                    municipios[agente.creencias['parada_actual'].county] = 0
                municipios[agente.creencias['parada_actual'].county] +=1
            with open(f'out/{current_time}.txt','w',encoding='utf-8') as file:
                for k,v in municipios.items():
                    file.write(f'{k},{v}\n')
                    # print(f'Municipio {k} tiene {municipios_inicio[k] if k in municipios_inicio else 0} agentes al pricipio y {v} al final')
        print(f'{current_time}', end='\r')

    print(f"\n\nSimulación con {len(agentes)} agentes completada:\n Agentes que llegaron al trabajo:", agentes_llegan_trabajo)
    print(" Agentes que regresaron a la casa:",agentes_regresan_casa)
    print(" Agentes que salieron para el trabajo antes de las 9pm:",agentes_tempranos)
    print(" Viajes Completados:",agentes_destino)
    print(" Destinos Completados:",agente_bien)
    print(" Agentes que regresaron a la casa sin llegar al trabajo:",agentes_regresan_impaciencia)
    print(" Agentes que se van en carro:",agentes_carro)
    print(" Agentes que se van caminando:",agentes_caimando)

    time_of_travel = 0
    municipios = {}
    for agente in agentes:
        if agente.creencias['parada_actual'] != agente.creencias['destino'] and agente.salida<=900:
            # print(f"Agente {agente.id} no llegó a su destino")
            # print(f'Salio a las {agente.salida} de {agente.creencias["parada_origen"].nombre}')
            # print(f'Se quedo en la parada {agente.creencias["parada_actual"].nombre}')
            # #Mostrar todas las guaguas que pasan por la parada en que se quedo
            # for guagua in agente.creencias["parada_actual"].colas:
            #     print(f'Guagua {guagua} en la parada {agente.creencias["parada_actual"].nombre}')
            # if len(agente.intenciones)==0:
            #     print("Agente en el trabajo")
            # else:
            #     print(f'Proxima guagua: {agente.intenciones[1][1]}')
            #     print(f'Proxima parada: {agente.intenciones[1][0].nombre}')
            #     print(f'Destino: {agente.creencias["destino"].nombre}')
            pass
        else:
            time_of_travel += agente.llegada-agente.salida
            if agente.creencias['parada_actual'].county not in municipios:
                municipios[agente.creencias['parada_actual'].county] = 0
            municipios[agente.creencias['parada_actual'].county] +=1

    print(f'\nTiempo Promedio de viaje: {time_of_travel/agentes_llegan_trabajo}\n')
    for k,v in municipios.items():
        print(f'Municipio {k} tiene {municipios_inicio[k] if k in municipios_inicio else 0} agentes al pricipio y {v} al final')
    for parada in grafo.vertices.values():
        personas_en_cola = sum(len(colas) for colas in parada.colas.values())
        if personas_en_cola>0:
            print(f"Parada {parada} tiene {personas_en_cola} personas en cola")
# Uso en la simulación
if __name__ == '__main__':
    grafo=Grafo()
    cargar_datos(grafo)
    simulacion(grafo, num_agentes=1000, tiempo_max=1440)  # Simular 30 minutos con 50 agentes    simulacion(grafo, num_agentes=100, tiempo_max=3600)  # Simular 1 hora con 100 agentes