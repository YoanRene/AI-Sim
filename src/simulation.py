import heapq
from agent import Agente
from graph import Grafo,cargar_datos
from astar import a_star
from utils import get_random_parada 
import random
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
        return len(self.pasajeros) < 50  # Assuming a capacity of 50

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
    # Inicialización
    heapq.heappush(eventos, Evento("person_arrival", current_time-2,Agente(-1,grafo.get_parada('3108'),grafo.get_parada('917'))))
    for i in range(num_agentes):
        origen = get_random_parada(grafo)
        if origen.county not in municipios_inicio:
            municipios_inicio[origen.county] = 0
        municipios_inicio[origen.county] +=1
        destino = get_random_parada(grafo)
        agente = Agente(i,origen,destino)
        agentes.append(agente)
        evento = Evento("person_arrival", current_time-1, agente)
        heapq.heappush(eventos, evento)

    # Inicializar guaguas
    for ruta in grafo.rutas:
        evento = Evento("init_bus", current_time, ruta)
        heapq.heappush(eventos, evento)
    agente_en_destino = 0
    # Bucle principal de simulación
    while eventos and current_time < tiempo_max:
        print(f'{current_time}', end='\r')
        evento = heapq.heappop(eventos)
        current_time = evento.time

        if evento.event_name == "person_arrival":
            """
            Un agente llega a una parada y decide qué guagua tomar.
            """
            agente = evento.args
            agente.elegir_ruta(grafo)
            if agente.creencias["parada_actual"] == agente.creencias["destino"]:
                print(f"Agente {agente.id} llegó su destino en {agente.creencias['parada_actual']}")
                agente_en_destino +=1
                continue
            if(len(agente.intenciones)<2):
                continue
            # print(f"Agente {agente.id} llegó{' a pie' if agente.intenciones[1][1] == 'pie' else ''} a la parada {agente.creencias['parada_actual']}")
            proxima_guagua = agente.intenciones[1][1]  # Asumiendo que intenciones[1] es (parada, guagua)

            if proxima_guagua == "pie":
                # Cuando tiene que ir para la proxima parada a pie
                #Actualizamos sus creencias
                agente.creencias["parada_actual"] = agente.intenciones[1][0]
                #Creamos el evento de llegada a la proxima parada
                #TODO: Cambiar el +10 por alguna metrica que tenga que ver con la distancia entre paradas.
                evento_person_arrival = Evento("person_arrival", current_time+10, agente)
                #Lo agregamos al heap
                heapq.heappush(eventos, evento_person_arrival)
                continue

            if proxima_guagua not in agente.creencias["parada_actual"].colas:
                agente.creencias["parada_actual"].colas[proxima_guagua]=[]
            agente.creencias["parada_actual"].colas[proxima_guagua].append(agente)
        
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
            new_guagua = Evento('init_bus',current_time + random.randint(100,200),ruta)
            heapq.heappush(eventos,new_guagua)
        elif evento.event_name == "next_stop":
            """
            La guagua llega a una parada y sube/baja pasajeros.
            """
            guagua = evento.args
            parada_actual = guagua.ruta[guagua.position][0]
            if(not parada_actual):
                continue

            # Bajar pasajeros
            pasajeros_antes = len(guagua.pasajeros)
            for pasajero in guagua.pasajeros:
                if pasajero.creencias["parada_next"] == parada_actual or guagua.position == len(guagua.ruta)-1:
                    pasajero.creencias["parada_actual"] = parada_actual
                    if pasajero.creencias["destino"] != parada_actual:
                        evento_person_arrival = Evento("person_arrival", current_time-0.01, pasajero)
                        heapq.heappush(eventos, evento_person_arrival)
                    else:
                        agente_en_destino +=1
                        print(f"Agente {pasajero.id} llegó a su destino en {parada_actual.nombre}")
                        pass
            guagua.pasajeros = [p for p in guagua.pasajeros if p.creencias["parada_next"] != parada_actual]
            pasajeros_bajados = pasajeros_antes - len(guagua.pasajeros)
            if(pasajeros_bajados>0):
                # print(f"Pasajeros bajados en {parada_actual.nombre}: {pasajeros_bajados}")
                pass
        
            # Subir pasajeros si no es la ultima parada
            pasajeros_subidos = 0
            while guagua.has_capacity() and (guagua.id in parada_actual.colas) and len(parada_actual.colas[guagua.id])>0 and guagua.position < len(guagua.ruta) - 1:
                pasajero = parada_actual.colas[guagua.id].pop(0)
                guagua.pasajeros.append(pasajero)
                pasajeros_subidos += 1
            
        
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


    print("Simulación completada, agente en destino:", agente_en_destino)

    municipios = {}
    for agente in agentes:
        if agente.creencias['parada_actual'] != agente.creencias['destino']:
            print(f"Agente {agente.id} no llegó a su destino")
            print(f'Se quedo en la parada {agente.creencias["parada_actual"].nombre}')
            #Mostrar todas las guaguas que pasan por la parada en que se quedo
            for guagua in agente.creencias["parada_actual"].colas:
                print(f'Guagua {guagua} en la parada {agente.creencias["parada_actual"].nombre}')
            print(f'Proxima guagua: {agente.intenciones[1][1]}')
            print(f'Proxima parada: {agente.intenciones[1][0].nombre}')
            print(f'Destino: {agente.creencias["destino"].nombre}')
        else:
            if agente.creencias['parada_actual'].county not in municipios:
                municipios[agente.creencias['parada_actual'].county] = 0
            municipios[agente.creencias['parada_actual'].county] +=1
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
    simulacion(grafo, num_agentes=2000, tiempo_max=18000)  # Simular 30 minutos con 50 agentes    simulacion(grafo, num_agentes=100, tiempo_max=3600)  # Simular 1 hora con 100 agentes