import csv
from astar import a_star,distancia_euclidea
from haversine import haversine
class Parada:
    def __init__(self, id, nombre, codigo, direccion, x, y, county):
        self.id = id
        self.nombre = nombre
        self.codigo = codigo
        self.direccion = direccion
        self.county = county
        self.colas = {}
        if x=='':
            self.x=0
            self.y=0
        else:
            self.x = float(x)
            self.y = float(y)
    def __lt__(self,otra):
        return True

    def __str__(self):
        return f"Parada {self.nombre} ({self.codigo})"

class Guagua:
    def __init__(self, id, ruta, nombre, terminal, origen, destino):
        self.id = id
        self.ruta = ruta
        self.nombre = nombre
        self.terminal = terminal
        self.origen = origen
        self.destino = destino
    def __lt__(self,otra):
        return True
    def __str__(self):
        return f"({self.ruta})"
        # return f"Guagua {self.nombre} ({self.ruta})"

class Grafo:
    def __init__(self):
        self.vertices = {}
        self.aristas = {}
        self.rutas = []  # Add this line to include routes

    def get_parada(self,id):
        return self.vertices[id]

    def agregar_vertice(self, parada):
        self.vertices[parada.id] = parada
        self.aristas[parada.id]= {}

    def agregar_arista(self, parada1, parada2, guagua):
        if parada1.id not in self.aristas:
            self.aristas[parada1.id] = {}
        if parada2.id not in self.aristas[parada1.id]:
            self.aristas[parada1.id][parada2.id] = []
        self.aristas[parada1.id][parada2.id].append(guagua)

    def obtener_guaguas(self, parada1, parada2):
        return self.aristas.get(parada1.id, {}).get(parada2.id, [])

def cargar_datos(grafo):
    with open('data/listaparadas.csv','r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Saltar la cabecera
        for id, nombre, codigo, direccion, x, y, county in reader:
            parada = Parada(id, nombre, codigo, direccion, x, y, county)
            grafo.agregar_vertice(parada)

    # Diccionario para almacenar las paradas de cada ruta por ID de ruta
    paradas_por_ruta = {}

    with open('data/paradasruta.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Saltar cabecera
        for id, codigo_parada, orden, id_ruta, regreso in reader:
            if id_ruta not in paradas_por_ruta:
                paradas_por_ruta[id_ruta] = []
            paradas_por_ruta[id_ruta].append((codigo_parada, orden))

    with open('data/rutas.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Saltar cabecera
        for id, ruta, nombre, terminal, origen, destino, *_ in reader:
            guagua = Guagua(id, ruta, nombre, terminal, origen, destino)

            # Obtener las paradas de la ruta (asumiendo que están ordenadas)
            paradas_de_la_ruta = paradas_por_ruta.get(id, [])
            ruta=[]
            # Agregar aristas al grafo para cada par de paradas consecutivas
            for i in range(len(paradas_de_la_ruta) - 1):
                codigo_parada1, _ = paradas_de_la_ruta[i]
                codigo_parada2, _ = paradas_de_la_ruta[i + 1]
                parada1 = next((p for p in grafo.vertices.values() if p.codigo == codigo_parada1), None)
                ruta.append((parada1,id))
                parada2 = next((p for p in grafo.vertices.values() if p.codigo == codigo_parada2), None)
                if(i==len(paradas_de_la_ruta)-2):
                    ruta.append((parada2,id))
                if parada1 and parada2:
                    grafo.agregar_arista(parada1, parada2, id)
            grafo.rutas.append(ruta)
        
        #Agregar paradas cercanas para ir a pie
        for parada in grafo.vertices.values():
            for parada2 in grafo.vertices.values():
                if parada == parada2:
                    continue
                dist = haversine((parada.y,parada.x), (parada2.y,parada2.x))
                if dist > 0.5:
                    continue
                grafo.agregar_arista(parada, parada2, 'pie')

def distancia_ruta(ruta):
  """
  Calcula la distancia total de una ruta dada como una lista de paradas.
  """
  distancia_total = 0
  for i in range(len(ruta) - 1):
    # print(distancia_total)
    parada1 = ruta[i]
    parada2 = ruta[i+1]
    distancia_tramo = distancia_euclidea(parada1,parada2)
    distancia_total += distancia_tramo
  return distancia_total


if __name__ == '__main__':
    grafo = Grafo()
    cargar_datos(grafo)
    print(grafo.get_parada('3108'))
    # Encontrar la ruta usando la heurística de distancia
    ruta = a_star(grafo, grafo.vertices["3108"], grafo.vertices["917"],estrategia='distancia')
    for i,j in ruta:
        print(f"{j}:{i}")
    print(len(ruta),len(set(id for _,id in ruta[1:])),distancia_ruta([x for x,_ in ruta]))
    ruta = a_star(grafo, grafo.vertices["3108"], grafo.vertices["3456"],estrategia='menos_paradas')
    for i,j in ruta:
        print(f"{j}:{i}")
    print(len(ruta),len(set(a for _,a in ruta[1:])),distancia_ruta([x for x,_ in ruta]))

    ruta = a_star(grafo, grafo.vertices["3108"], grafo.vertices["3456"],estrategia='ruta_fija')
    for i,j in ruta:
        print(f"{j}:{i}")
    print(len(ruta),len(set(a for _,a in ruta[1:])),distancia_ruta([x for x,_ in ruta]))
