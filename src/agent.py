import random
from astar import a_star
from graph import Grafo,cargar_datos
from haversine import haversine
class Agente:
    def __init__(self, id, parada_actual, destino, regresa=True):
        self.id = id
        self.in_guagua = False
        self.salida= 0
        self.llegada = -1
        self.cursor_parada = 0
        self.cursor_ruta = 1
        self.repite = False
        self.creencias = {
            "regresa":regresa, #El Agente regresa a la casa despues de haber trabajado
            "parada_origen":parada_actual, #Parada de origen del agente
            "parada_actual": parada_actual, #Parada actual donde esta el agente
            "destino": destino, #Parada a la cual se dirige el agente
            "paradas_next":[], #Lista de paradas donde el agente cambia de guagua
            "current_time":0,
            "ruta_planificada":[],
            "llego_trabajo": False,
            "regreso_casa":False,
            "cogio_carro":False,
            "caminando":False
            }
        
        self.intenciones = ['salir de casa']
        self.deseos = ["llegar_destino"]
        self.puntuacion_ruta = 0
        self.tiempo_impaciencia=-1
        # Preferencias del agente (ajusta los valores según la importancia)
        self.preferencias = {
            "rapidez": random.random(),
            "comodidad": random.random(),
            "ganancias": random.random(),
            "laboriosidad":random.random(),
            "condicion_fisica":random.random(),
            "paciencia":random.random() 
        }
    def proxima_bajada(self):
        return self.creencias["paradas_next"][self.cursor_parada]
    def impaciente(self):
        inicio = self.parada_actual()
        #Regresa a la casa
        if(self.preferencias["laboriosidad"]<0.4 and self.creencias["regresa"]):
            self.creencias["destino"]=self.creencias["parada_origen"]
            if 'salir de casa' in self.intenciones:
                self.intenciones.remove('salir de casa')
            self.deseos = ["regresar a casa"]
        #Sale de la parada
        self.tiempo_impaciencia = -1
        self.creencias['parada_actual'].colas[self.proxima_guagua()].remove(self)
        self.creencias['parada_actual']=self.creencias['destino']
        final = self.parada_actual()
        distancia = haversine((inicio.x,inicio.y),(final.x,final.y))
        tiempo = 0
        if(0.3*self.preferencias["condicion_fisica"]+0.7*self.preferencias["ganancias"]>0.6):
            #Coge un carro para el destino
            self.intenciones.append("ir en carro")
            tiempo = distancia * 5
        else:
            #Caminando
            self.intenciones.append("ir caminando")
            tiempo = distancia * self.preferencias['condicion_fisica']*50
        return tiempo
    def recalcula_impaciencia(self,current_time):
            tiempo_impaciencia = self.preferencias['paciencia'] * random.randint(60,120)
            self.tiempo_impaciencia =current_time+tiempo_impaciencia
            return tiempo_impaciencia

    def intenta_regresar(self,current_time):
        if not self.regresa():
            return False
        #Si el agente regresa a casa lo hace con mayor probabilidad en el horario de 4-6
        #A no ser que no llege a un minimo de 6 horas de trabajo
        self.tiempo_regreso = current_time + 6*60
        #Si las 6 horas se cumplen antes de las 4 de la tarde sale en ese rango
        if self.tiempo_regreso <= 600:
            self.tiempo_regreso = random.randint(600,720)
        else:
            #Si no regresa en un rango de hasta 3 horas 
            #Es decir la jornada laboral seria de 6-9 horas
            self.tiempo_regreso += random.randint(0,120)
        #Actualizamos las creencias del agente
        self.creencias["destino"]=self.creencias["parada_origen"]
        self.creencias['regresa']=False
        self.creencias['ruta_planificada'] = []
        self.intenciones = ['salir del trabajo']
        self.cursor_parada=0
        self.cursor_ruta=1
        if self.creencias['parada_actual']==self.creencias['destino']:
            self.tiempo_regreso = 0
            self.intenciones = []
            return True
        return True
    def mueve_parada(self,parada=None):
        pos_i = self.creencias['parada_actual']
        if parada:
            self.creencias['parada_actual']=parada
        else:
            self.creencias['parada_actual'] = self.creencias['ruta_planificada'][self.cursor_ruta][0]
        self.cursor_ruta+=1
        pos_f = self.creencias['parada_actual']
        
        return haversine((pos_i.x,pos_i.y),(pos_f.x,pos_f.y)) * self.preferencias['condicion_fisica'] * 60
    def parada_actual(self):
        return self.creencias['parada_actual']
    def proxima_guagua(self):
        return self.creencias['ruta_planificada'][self.cursor_ruta][1]

    def regresa(self):
        return self.creencias['regresa']
    def en_destino(self):
        return self.creencias['parada_actual']==self.creencias['destino']
    def regreso_a_casa(self):
        return self.creencias['destino']==self.creencias['parada_origen']==self.creencias['parada_actual']
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
            self.creencias['ruta_planificada'] =[(self.creencias['parada_actual'],guagua.id),*new_ruta]
            self.cursor_parada=0
            self.cursor_ruta=1
            self.creencias['paradas_next'] = []
            for i in range(1,len(self.creencias['ruta_planificada'])-1):
                if self.creencias['ruta_planificada'][i][1]!=self.creencias['ruta_planificada'][i+1][1]:
                    self.creencias["paradas_next"].append(self.creencias['ruta_planificada'][i][0])
                elif self.creencias['ruta_planificada'][i][1]=="pie":
                    self.creencias["paradas_next"].append(self.creencias['ruta_planificada'][i][0])
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
            self.creencias['ruta_planificada'] = mejor_ruta
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
                puntuacion += self.preferencias["comodidad"] * (1 / len(set(parada.id for parada, _ in ruta[1:])))
        elif estrategia == "ruta_fija":
            guaguas_diferentes = set(g for _, g in ruta[0:])
            puntuacion += (self.preferencias['comodidad']+self.preferencias['ganancias'])/2 * (1/len(guaguas_diferentes))
        return puntuacion

    def actualizar_creencias(self, current_time, evento,grafo):
        """
        Actualiza la creencia sobre el tiempo actual.

        Args:
            nueva_parada: La nueva parada donde se encuentra el agente.
        """
        self.creencias["current_time"] = current_time
        if evento.args == self and evento.event_name == 'person_arrival':
            if 'salir de casa' in self.intenciones:
                self.intenciones.remove('salir de casa')
                # if self.proxima_guagua() == 'pie':
                #     self.intenciones.append('caminar a la siguiente parada')
                # else:
                #     self.intenciones.append('esperar la guagua')
        # if tiempo_promedio_ruta(self.creencias['ruta_actual'][self.cursor_ruta-1:])+self.creencias['current_time']>=self.creencias['horario_llegada']:
        #     if 'llegar_temprano' in self.deseos:
        #         self.intenciones = ['coger carro']
        if self.tiempo_impaciencia!=-1 and self.creencias["current_time"] >= self.tiempo_impaciencia and self.preferencias['paciencia']<-1:
            if not self.in_guagua:
                t = self.impaciente()
                return ('person_arrival',current_time+ t , self)
                # #Regresa a la casa
                # if "regresa a casa" in self.deseos:
                #     agentes_regresan_impaciencia +=1
                # if "ir en carro" in self.deseos:
                #     agentes_carro+=1
                # else:
                #     #Caminando
                #     agentes_caimando+=1
        if evento.event_name == 'next_stop':
            guagua = evento.args
            parada_actual =  guagua.ruta[guagua.position-1][0]
            if self.parada_actual==parada_actual and not self.in_guagua and guagua.has_capacity():
                if self.piensa_cambiar_ruta(grafo,guagua):
                    self.tiempo_impaciencia =-1
                    self.in_guagua =True
                    guagua.self.append(self)
                    self.creencias['parada_actual'].colas[self.proxima_guagua()].remove(self)





if __name__=="__main__":
    g = Grafo()
    cargar_datos(g)
    a = Agente(1,g.get_parada('3108'),g.get_parada('3456'))
    a.elegir_ruta(g)