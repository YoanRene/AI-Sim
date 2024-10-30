import random
from astar import a_star
from graph import Grafo,cargar_datos
from haversine import haversine
class self:
    def __init__(self, id, parada_actual, destino, regresa=True):
        self.id = id
        self.in_guagua = False
        self.salida= 0
        self.llegada = -1
        self.cursor_parada = 0
        self.cursor_ruta = 1
        self.repite = False
        self.creencias = {
            "regresa":regresa, #El self regresa a la casa despues de haber trabajado
            "parada_origen":parada_actual, #Parada de origen del self
            "parada_actual": parada_actual, #Parada actual donde esta el self
            "destino": destino, #Parada a la cual se dirige el self
            "paradas_next":[], #Lista de paradas donde el self cambia de guagua
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
        # Preferencias del self (ajusta los valores según la importancia)
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
        #Si el self regresa a casa lo hace con mayor probabilidad en el horario de 4-6
        #A no ser que no llege a un minimo de 6 horas de trabajo
        self.tiempo_regreso = current_time + 6*60
        #Si las 6 horas se cumplen antes de las 4 de la tarde sale en ese rango
        if self.tiempo_regreso <= 600:
            self.tiempo_regreso = random.randint(600,720)
        else:
            #Si no regresa en un rango de hasta 3 horas 
            #Es decir la jornada laboral seria de 6-9 horas
            self.tiempo_regreso += random.randint(0,120)
        #Actualizamos las creencias del self
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
                # Evaluar la ruta según las preferencias del self
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
        Elige la mejor ruta utilizando A* y una heurística basada en las preferencias del self.

        Args:
            grafo: El grafo del sistema de transporte.
            informacion_guaguas: Un diccionario con información sobre las guaguas (capacidad, etc.).
        """
        self.creencias['paradas_next'] = []
        posibles_rutas = {}
        for estrategia in ["distancia", "menos_paradas", "ruta_fija"]:
            ruta = a_star(grafo, self.creencias["parada_actual"], self.creencias["destino"], estrategia)
            if ruta:
                # Evaluar la ruta según las preferencias del self
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
            # print(f"self {self.id} eligió ruta con estrategia: {mejor_estrategia}")
        else:
            print(f"self {self.id} no encontró una ruta viable.")

    def evaluar_ruta(self, ruta, estrategia, informacion_guaguas=None):
        """
        Evalúa la ruta según las preferencias del self.

        Args:
            ruta: La ruta a evaluar.
            estrategia: La estrategia de heurística utilizada para encontrar la ruta.
            informacion_guaguas: Información sobre las guaguas.

        Returns:
            Una puntuación numérica que representa la calidad de la ruta para el self.
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

    def actualizar_creencias(self, current_time, evento, grafo):
        """
        Actualiza las creencias y resuelve conflictos usando un ciclo de punto fijo.
        """
        self.creencias["current_time"] = current_time

        acciones_posibles = []

        # Definir funciones para cada posible acción/decisión
        def accion_llegar_casa():
            if evento.args == self and evento.event_name == 'person_arrival':
                if 'salir de casa' in self.intenciones:
                    self.intenciones.remove('salir de casa')
                    return True
            return False


        def accion_impaciencia():
            if self.tiempo_impaciencia != -1 and self.creencias["current_time"] >= self.tiempo_impaciencia and self.preferencias['paciencia'] < -1:  # Corregir la condición de paciencia
                if not self.in_guagua:
                    t = self.impaciente()
                    acciones_posibles.append(('person_arrival', current_time + t, self))
                    return True
            return False

        def accion_subir_guagua():
            if evento.event_name == 'next_stop':
                guagua = evento.args
                parada_actual = guagua.ruta[guagua.position - 1][0]
                if self.parada_actual == parada_actual and not self.in_guagua and guagua.has_capacity():
                    if self.piensa_cambiar_ruta(grafo, guagua):
                        self.tiempo_impaciencia = -1
                        self.in_guagua = True
                        guagua.passengers.append(self)  # Agregar al self a la guagua
                        self.creencias['parada_actual'].colas[self.proxima_guagua()].remove(self)
                        return True

            return False

        def accion_regresar_del_trabajo():
            if self.intenta_regresar(current_time):
                acciones_posibles.append(('person_arrival',self.tiempo_regreso,self))  #Considerar el tiempo de regreso
                return True
            return False
        
        self.actualizar_intenciones(grafo, current_time)
        # Ciclo de punto fijo
        estado_anterior = None
        estado_actual = tuple(self.intenciones)  # Usamos las intenciones como representación del estado


        while estado_anterior != estado_actual:
            estado_anterior = estado_actual
            acciones_realizadas = []

            for accion in [accion_llegar_casa,accion_regresar_del_trabajo, accion_impaciencia, accion_subir_guagua]:
                if accion():
                    acciones_realizadas.append(accion.__name__)

            estado_actual = tuple(self.intenciones)

        return acciones_posibles  # Devolver la lista de acciones posibles
    
    def actualizar_intenciones(self, grafo, current_time):
        """
        Actualiza las intenciones del  basándose en sus creencias, preferencias y el contexto.

        Args:
            self: El self cuya intención se va a actualizar.
            grafo: El grafo del sistema de transporte.
            informacion_guaguas: Información sobre las guaguas disponibles.
            current_time: Tiempo actual en minutos desde el inicio de la simulación.

        Returns:
            Una lista actualizada de intenciones.
        """

        # 1. Evaluar el estado actual
        estado_actual = self.creencias['parada_actual'].id
        destino = self.creencias['destino'].id

        # 2. Considerar factores de tiempo y preferencias
        hora = current_time // 60  # Convertir minutos a horas
        last = self.intenciones
        while True:
            # 3. Reglas para la actualización de intenciones
            if self.intenciones == ['salir de casa']:
                # Si es temprano, espera en casa
                if hora < 8:
                    self.intenciones = ['llegar al trabajo']
                else:
                    self.intenciones = ['esperar en casa'] # por defecto

            elif self.intenciones == ['llegar al trabajo']:
                if self.en_destino():
                    self.creencias['llego_trabajo'] = True
                    self.intenciones = ['trabajar'] # Trabajar
                elif self.in_guagua:
                    self.intenciones = ['esperar_guagua']
                else:
                    if self.preferencias['rapidez'] > self.preferencias['comodidad']:
                        self.intenciones = ['buscar ruta mas rapida']
                    else:
                        self.intenciones = ['buscar ruta mas comoda']

            elif self.intenciones == ['trabajar']:
                if current_time > self.tiempo_regreso > 0:
                    self.intenciones = ['regresar a casa']
                else:
                    self.intenciones = ['trabajar']

            elif self.intenciones == ['regresar a casa']:
                if self.regreso_a_casa():
                    self.intenciones = ['descansar']
                elif self.in_guagua:
                    self.intenciones = ['esperar_guagua']
                else:
                    self.intenciones = ['buscar ruta mas rapida']
                    #Se añade la posibilidad de coger un carro dependiendo de la preferencia del self
                    if self.preferencias['comodidad'] > 0.7:
                        self.intenciones.append('coger carro')

            elif self.intenciones == ['buscar ruta mas rapida']:
                self.elegir_ruta(grafo)
                self.intenciones = ['esperar_guagua']

            elif self.intenciones == ['buscar ruta mas comoda']:
                self.elegir_ruta(grafo)
                self.intenciones = ['esperar_guagua']
            elif self.intenciones == ['esperar_guagua']:
                if not self.in_guagua:
                    self.intenciones = ['buscar_guagua']  # Buscar la guagua
                else:
                    self.intenciones = ['viajar en guagua']
            elif self.intenciones == ['buscar_guagua']:
                # Logica para buscar la proxima guagua
                self.intenciones = ['esperar_guagua']

            elif self.intenciones == ['viajar en guagua']:
                if not self.in_guagua:
                    self.intenciones = ['buscar_guagua']
                elif self.en_destino():
                    if self.creencias['llego_trabajo']:
                        self.intenciones = ['trabajar']
                    else:
                        self.intenciones = ['descansar']
                else:
                    self.intenciones = ['viajar en guagua']

            elif self.intenciones == ['descansar']:
                self.intenciones = []  # Sin más intenciones

            if last == self.intenciones:
                break
            else:
                last = self.intenciones
        return self.intenciones





if __name__=="__main__":
    g = Grafo()
    cargar_datos(g)
    a = self(1,g.get_parada('3108'),g.get_parada('3456'))
    a.elegir_ruta(g)