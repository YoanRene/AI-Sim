import random
from astar import a_star
from graph import Grafo,cargar_datos

class Agente:
    def __init__(self, id, parada_actual, destino):
        self.id = id
        self.creencias = {"parada_actual": parada_actual, "destino": destino,"parada_next":destino}
        self.deseos = ["llegar_destino"]
        self.intenciones = []
        # Preferencias del agente (ajusta los valores según la importancia)
        self.preferencias = {
            "rapidez": 0.6,
            "comodidad": 0.3,
            "costo": 0.1,
        }

    def elegir_ruta(self, grafo, informacion_guaguas=None):
        """
        Elige la mejor ruta utilizando A* y una heurística basada en las preferencias del agente.

        Args:
            grafo: El grafo del sistema de transporte.
            informacion_guaguas: Un diccionario con información sobre las guaguas (capacidad, etc.).
        """
        posibles_rutas = {}
        for estrategia in ["distancia", "menos_paradas", "ruta_fija"]:
            ruta = a_star(grafo, self.creencias["parada_actual"], self.creencias["destino"], estrategia)
            if ruta:
                # Evaluar la ruta según las preferencias del agente
                puntuacion = self.evaluar_ruta(ruta, estrategia, informacion_guaguas)
                posibles_rutas[estrategia] = (ruta, puntuacion)

        # Elegir la ruta con la mayor puntuación
        if posibles_rutas:
            mejor_estrategia, (mejor_ruta, _) = max(posibles_rutas.items(), key=lambda item: item[1][1])
            self.intenciones = mejor_ruta
            self.creencias["parada_next"]=self.creencias["destino"]
            for i in range(1,len(mejor_ruta)-1):
                if mejor_ruta[i][1]!=mejor_ruta[i+1][1]:
                    self.creencias["parada_next"] = mejor_ruta[i][0]
                    break
            if self.creencias["parada_next"]== None:
                print("Va caminando")
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