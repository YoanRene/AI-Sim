import random
from astar import a_star
from graph import Grafo,cargar_datos

class Agente:
    def __init__(self, id, parada_actual, destino, regresa=True):
        self.id = id
        self.in_guagua = False
        self.salida= 0
        self.llegada = -1
        self.creencias = {"regresa":regresa,"parada_origen":parada_actual,"parada_actual": parada_actual, "destino": destino,"paradas_next":[],"cursor_parada":0,"cursor_ruta":1,"repite":False}
        self.deseos = ["llegar_destino"]
        self.intenciones = []
        self.puntuacion_ruta = 0
        # Preferencias del agente (ajusta los valores según la importancia)
        self.preferencias = {
            "rapidez": random.random(),
            "comodidad": random.random(),
            "ganancias": random.random(),
            "laboriosidad":random.random(),
            "condicion_fisica":random.random(),
            "paciencia":random.random() 
        }
    def piensa_cambiar_ruta(self,grafo,guagua):
        """
        Elige si cambiarse a una nueva ruta sabiendo que la guagua pasada por parametros esta en la parada

        Args:
            grafo: El grafo del sistema de transporte.
            guagua: Guagua que se encuentra en la parada actual
        """
        posibles_rutas = {}
        for estrategia in ["distancia", "menos_paradas", "ruta_fija"]:
            ruta = a_star(grafo, guagua.ruta[guagua.position+1][0], self.creencias["destino"], estrategia,guagua=guagua.id)
            if ruta:
                # Evaluar la ruta según las preferencias del agente
                puntuacion = self.evaluar_ruta(ruta, estrategia)
                posibles_rutas[estrategia] = (ruta, puntuacion)
        _, (new_ruta,new_pos) = max(posibles_rutas.items(),key=lambda item:item[1][1])
        if new_pos >=self.puntuacion_ruta:
            self.puntuacion_ruta = new_pos
            self.intenciones =[(self.creencias['parada_actual'],guagua.id),*new_ruta]
            self.creencias['cursor_parada']=0
            self.creencias['cursor_ruta']=1
            self.creencias['paradas_next'] = []
            for i in range(1,len(self.intenciones)-1):
                if self.intenciones[i][1]!=self.intenciones[i+1][1]:
                    self.creencias["paradas_next"].append(self.intenciones[i][0])
                elif self.intenciones[i][1]=="pie":
                    self.creencias["paradas_next"].append(self.intenciones[i][0])
            self.creencias["paradas_next"].append(self.creencias["destino"])
            return True
        return False
    def elegir_ruta(self, grafo, informacion_guaguas=None):
        """
        Elige la mejor ruta utilizando A* y una heurística basada en las preferencias del agente.

        Args:
            grafo: El grafo del sistema de transporte.
            informacion_guaguas: Un diccionario con información sobre las guaguas (capacidad, etc.).
        """
        self.creencias['paradas_next'] = []
        posibles_rutas = {}
        for estrategia in ["distancia", "menos_paradas", "ruta_fija"]:
            ruta = a_star(grafo, self.creencias["parada_actual"], self.creencias["destino"], estrategia)
            if ruta:
                # Evaluar la ruta según las preferencias del agente
                puntuacion = self.evaluar_ruta(ruta, estrategia, informacion_guaguas)
                posibles_rutas[estrategia] = (ruta, puntuacion)

        # Elegir la ruta con la mayor puntuación
        if posibles_rutas:
            mejor_estrategia, (mejor_ruta, p) = max(posibles_rutas.items(), key=lambda item: item[1][1])
            self.intenciones = mejor_ruta
            self.puntuacion_ruta = p
            for i in range(1,len(mejor_ruta)-1):
                if mejor_ruta[i][1]!=mejor_ruta[i+1][1]:
                    self.creencias["paradas_next"].append(mejor_ruta[i][0])
                elif mejor_ruta[i][1]=="pie":
                    self.creencias["paradas_next"].append(mejor_ruta[i][0])
            self.creencias["paradas_next"].append(self.creencias["destino"])
            # print(f"Agente {self.id} eligió ruta con estrategia: {mejor_estrategia}")
        else:
            print(f"Agente {self.id} no encontró una ruta viable.")

    def evaluar_ruta(self, ruta, estrategia, informacion_guaguas=None):
        """
        Evalúa la ruta según las preferencias del agente.

        Args:
            ruta: La ruta a evaluar.
            estrategia: La estrategia de heurística utilizada para encontrar la ruta.
            informacion_guaguas: Información sobre las guaguas.

        Returns:
            Una puntuación numérica que representa la calidad de la ruta para el agente.
        """
        puntuacion = 0
        if estrategia == "distancia":
            puntuacion += self.preferencias["rapidez"] * (1 / len(ruta))  # Mayor puntuación para rutas más cortas
        elif estrategia == "menos_paradas":
            if len(ruta)==1:
                puntuacion += self.preferencias["comodidad"]
            else:
                puntuacion += self.preferencias["comodidad"] * (1 / len(set(parada.id for parada, _ in ruta[1:])))  # Menos transbordos
        elif estrategia == "ruta_fija":
            # Aquí se podría evaluar la comodidad en función de la información de las guaguas
            pass 
        # ... (agregar más evaluaciones según las preferencias)
        return puntuacion

    def actualizar_creencias(self, nueva_parada):
        """
        Actualiza la creencia sobre la parada actual del agente.

        Args:
            nueva_parada: La nueva parada donde se encuentra el agente.
        """
        self.creencias["parada_actual"] = nueva_parada

if __name__=="__main__":
    g = Grafo()
    cargar_datos(g)
    a = Agente(1,g.get_parada('3108'),g.get_parada('3456'))
    a.elegir_ruta(g)