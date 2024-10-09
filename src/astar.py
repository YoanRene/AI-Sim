import math
from heapq import heappop, heappush
from haversine import haversine

def distancia_euclidea(parada1, parada2):
  """
  Calcula la distancia euclidea entre dos paradas.
  """
  return math.sqrt((parada1.x - parada2.x)**2 + (parada1.y - parada2.y)**2)

def heuristica(parada1, parada2, estrategia="distancia", grafo=None, ruta_actual=None, guagua=None):
  """
  Calcula la heurística entre dos paradas según la estrategia elegida.
  """
  if estrategia == "distancia":
    return distancia_euclidea(parada1, parada2)
  
  elif estrategia == "ruta_fija":
    if not ruta_actual:
      return distancia_euclidea(parada1, parada2)  # Sin información de ruta previa
    
    _,ultima_guagua = ruta_actual[-1]  # Guagua del último tramo de la ruta
    # guaguas_disponibles = grafo.aristas.get(parada1.id, {}).get(parada2.id, [])
    penalizacion = 100  # Ajusta el valor según la penalización deseada
    if not ultima_guagua:
      return distancia_euclidea(parada1, parada2)
    if ultima_guagua == guagua:
      return distancia_euclidea(parada1, parada2) 
    else:
      return distancia_euclidea(parada1, parada2) * penalizacion

  elif estrategia == "menos_paradas":
    # Estimación simple: distancia restante / distancia promedio entre paradas
    distancia_restante = distancia_euclidea(parada1, parada2)
    paradas_estimadas = distancia_restante / 500  # Ajusta el valor según la distancia promedio
    penalizacion_por_parada = 2  # Ajusta el valor según la penalización deseada
    return distancia_euclidea(parada1, parada2) + penalizacion_por_parada * paradas_estimadas
  
  elif estrategia == "ruta_directa":
    # Calcula el ángulo entre la línea recta al destino y la dirección del movimiento
    dx_destino = parada2.x - parada1.x
    dy_destino = parada2.y - parada1.y
    angulo_destino = math.atan2(dy_destino, dx_destino)

    if not ruta_actual:
      return distancia_euclidea(parada1, parada2)  # Sin información de ruta previa
    
    dx_actual = parada1.x - ruta_actual[-2].x
    dy_actual = parada1.y - ruta_actual[-2].y
    angulo_actual = math.atan2(dy_actual, dx_actual)

    diferencia_angular = abs(angulo_destino - angulo_actual)
    penalizacion_angular = 2  # Ajusta el valor según la penalización deseada
    return distancia_euclidea(parada1, parada2) * (1 + penalizacion_angular * diferencia_angular)

  else:
    raise ValueError("Estrategia de heurística no válida.")
def a_star(grafo, origen, destino, estrategia="distancia"):
  """
  Implementa el algoritmo A* para encontrar la ruta entre dos paradas.
  """
  visitados = set()
  cola_prioridad = [(0, origen, [(origen,None)])]
  
  while cola_prioridad:
    coste_actual, parada_actual, ruta_actual = heappop(cola_prioridad)

    if parada_actual == destino:
      return ruta_actual
    
    if parada_actual.id in visitados:
      continue

    visitados.add(parada_actual.id)

    for parada_vecina, guaguas in grafo.aristas[parada_actual.id].items():
      # Puedes añadir lógica para elegir una guagua específica de la lista
      nuevo_coste = coste_actual + 1  # Considera el coste de tomar la guagua
      for guagua in guaguas:
        #TODO: Falta verificar que si es a pie darle un mayor peso en dependencia de la persona.
        coste_estimado = nuevo_coste + heuristica(grafo.vertices[parada_vecina], destino, estrategia, grafo, ruta_actual, guagua)
        heappush(cola_prioridad, (coste_estimado, grafo.vertices[parada_vecina], ruta_actual + [(grafo.vertices[parada_vecina],guagua)]))

      
  return None  # No se encontró ruta
