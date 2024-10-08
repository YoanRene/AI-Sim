import heapq
from agent import Agente
from graph import Grafo,cargar_datos
from astar import a_star
from utils import get_random_parada 

class Evento:
    def __init__(self, event_name, time, args):
        self.event_name = event_name
        self.time = time
        self.args = args
    def __lt__(self, other):
        return self.time <= other.time

class Guagua:
    def __init__(self, ruta):
        self.ruta = ruta
        self.position = 0
        self.pasajeros = []

    def has_capacity(self):
        return len(self.pasajeros) < 50  # Assuming a capacity of 50

def simulacion(grafo, num_agentes, tiempo_max):
    eventos = []
    current_time = 0

    # Inicialización
    for i in range(num_agentes):
        origen = get_random_parada(grafo)
        destino = get_random_parada(grafo)
        agente = Agente(i,origen,destino)
        evento = Evento("person_arrival", current_time-1, agente)
        heapq.heappush(eventos, evento)

    # Inicializar guaguas
    for ruta in grafo.rutas:
        evento = Evento("init_bus", current_time, ruta)
        heapq.heappush(eventos, evento)

    # Bucle principal de simulación
    while eventos and current_time < tiempo_max:
        evento = heapq.heappop(eventos)
        current_time = evento.time

        if evento.event_name == "person_arrival":
            agente = evento.args
            agente.elegir_ruta(grafo)  # Pasar información de guaguas
            if(len(agente.intenciones)<2):
                continue
            proxima_guagua = agente.intenciones[1][1]  # Asumiendo que intenciones[1] es (parada, guagua)
            
            if proxima_guagua not in agente.creencias["parada_actual"].colas:
                agente.creencias["parada_actual"].colas[proxima_guagua]=[]
            agente.creencias["parada_actual"].colas[proxima_guagua].append(agente)
        
        elif evento.event_name == "init_bus":
            ruta = evento.args
            if(len(ruta)<1):
                continue
            guagua = Guagua(ruta)
            evento_siguiente = Evento("next_stop", current_time, guagua)
            heapq.heappush(eventos, evento_siguiente)

        elif evento.event_name == "next_stop":
            guagua = evento.args
            parada_actual = guagua.ruta[guagua.position]
            if(not parada_actual):
                continue
        
            # Bajar pasajeros
            guagua.pasajeros = [p for p in guagua.pasajeros if p.creencias["destino"] != parada_actual]
        
            # Subir pasajeros
            while guagua.has_capacity() and (guagua in parada_actual.colas) and len(parada_actual.colas[guagua])>0:
                pasajero = parada_actual.colas[guagua].pop(0)
                guagua.pasajeros.append(pasajero)
        
            guagua.position += 1
            if guagua.position < len(guagua.ruta):
                tiempo_viaje = 10  # Tiempo fijo entre paradas, podría ser variable
                evento_siguiente = Evento("next_stop", current_time + tiempo_viaje, guagua)
                heapq.heappush(eventos, evento_siguiente)
            else:
                # La guagua ha completado su ruta, reiniciar
                guagua.position = 0
                evento_reinicio = Evento("init_bus", current_time, guagua.ruta)
                heapq.heappush(eventos, evento_reinicio)

    print("Simulación completada")

# Uso en la simulación
if __name__ == '__main__':
    grafo=Grafo()
    cargar_datos(grafo)
    simulacion(grafo, num_agentes=20, tiempo_max=1800)  # Simular 30 minutos con 50 agentes    simulacion(grafo, num_agentes=100, tiempo_max=3600)  # Simular 1 hora con 100 agentes