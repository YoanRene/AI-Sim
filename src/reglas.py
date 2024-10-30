def termino_trabajo_y_regreso_a_casa(state):
  """Si termino el trabajo y regreso a casa, voy a casa."""
  if state['trabajo_terminado'] and state['en_casa'] == False:
    return 'voy_a_casa'
  return None

def estoy_en_la_casa_y_tengo_que_trabajar(state):
  """Si estoy en la casa y tengo que trabajar, voy a trabajar."""
  if state['en_casa'] and state['trabajo_pendiente']:
    return 'voy_a_trabajar'
  return None

def voy_a_trabajar_y_voy_a_la_parada(state):
  """Si voy a trabajar, voy a la parada."""
  if state['trabajo_pendiente'] and state['en_la_parada'] == False:
    return 'voy_a_la_parada'
  return None

def estoy_en_la_parada_y_no_se_quaguna(state):
  """Si estoy en la parada y no se qué hacer, planifico qué hacer."""
  if state['en_la_parada'] and state['planificado'] == False:
    return 'planifico_que_hacer'
  return None

def estoy_en_la_parada_y_se_quaguna(state):
  """Si estoy en la parada y sé qué hacer, camino hasta la parada."""
  if state['en_la_parada'] and state['planificado'] == True:
    return 'camino_hasta_sig_parada'
  return None

def estoy_en_la_parada_y_cola_de_la_quaguna(state):
  """Si estoy en la parada y estoy en la cola de la quaguna, me monto en la quaguna."""
  if state['en_la_cola_de_la_quaguna']:
    return 'me_monto_en_la_quaguna'
  return None

def estoy_en_la_cola_de_la_quaguna_y_me_paciencia(state):
  """Si estoy en la cola de la quaguna y me estoy impacientando, me impaciento."""
  if state['en_la_cola_de_la_quaguna'] and state['impaciente']:
    return 'me_impaciento'
  return None

def estoy_en_la_cola_de_la_quaguna_y_estoy_aguaguna_que_no_es_la_mia(state):
  """Si estoy en la cola de la quaguna y estoy aguagunando que no es la mia, veo si me adelanta la quaguna que no es mia."""
  if state['en_la_cola_de_la_quaguna'] and state['aguagunando_que_no_es_mia']:
    return 'veo_si_me_adelanta_la_quaguna_que_no_es_mia'
  return None

def si_estoy_en_la_quaguna_y_estoy_en_parada_que_toca_bajarse(state):
  """Si estoy en la quaguna y estoy en parada que toca bajarse, bajo en la parada."""
  if state['en_la_quaguna'] and state['en_parada_que_toca_bajarse']:
    return 'bajo_en_la_parada'
  return None

def si_me_adelanta_la_quaguna_que_no_es_mia(state):
  """Si me adelanta la quaguna que no es mia, marco en la cola de la quaguna."""
  if state['adelanta_la_quaguna_que_no_es_mia']:
    return 'marco_en_la_cola_de_la_quaguna'
  return None

def si_estoy_impacientado_y_no_mis_pretenicas_se_inclinan_por_trabajar(state):
  """Si estoy impacientado y no mis pretenicas se inclinan por trabajar, voy a casa."""
  if state['impaciente'] and state['no_mis_pretenicas_se_inclinan_por_trabajar']:
    return 'voy_a_casa'
  return None

def voy_a_casa_y_voy_a_la_parada(state):
  """Si voy a casa, voy a la parada."""
  if state['en_casa'] == False and state['en_la_parada'] == False:
    return 'voy_a_la_parada'
  return None

def si_estoy_impacientado_y_no_cojo_quaguna(state):
  """Si estoy impacientado y no cojo quaguna, quiero carro."""
  if state['impaciente'] and state['cojo_quaguna'] == False:
    return 'quiero_carro'
  return None

def si_no_cojo_quaguna_y_quiero_caminar(state):
  """Si no cojo quaguna y quiero caminar, voy caminando a destino."""
  if state['cojo_quaguna'] == False and state['quiero_caminar']:
    return 'voy_caminando_a_destino'
  return None

def si_llego_a_mi_destino_y_es_el_trabajo(state):
  """Si llego a mi destino y es el trabajo, trabajo."""
  if state['llego_a_mi_destino'] and state['es_el_trabajo']:
    return 'trabajar'
  return None

def si_llego_a_mi_destino_y_es_casa(state):
  """Si llego a mi destino y es casa, descanso."""
  if state['llego_a_mi_destino'] and state['es_casa']:
    return 'descansar'
  return None


def inferencia_bdi(state):
  """Inferencia BDI para determinar la intencion a tomar."""
  intencion = None

  # Iterar sobre las funciones de inferencia
  for funcion in [
    termino_trabajo_y_regreso_a_casa,
    estoy_en_la_casa_y_tengo_que_trabajar,
    voy_a_trabajar_y_voy_a_la_parada,
    estoy_en_la_parada_y_no_se_quaguna,
    estoy_en_la_parada_y_se_quaguna,
    estoy_en_la_parada_y_cola_de_la_quaguna,
    estoy_en_la_cola_de_la_quaguna_y_me_paciencia,
    estoy_en_la_cola_de_la_quaguna_y_estoy_aguaguna_que_no_es_la_mia,
    si_estoy_en_la_quaguna_y_estoy_en_parada_que_toca_bajarse,
    si_me_adelanta_la_quaguna_que_no_es_mia,
    si_estoy_impacientado_y_no_mis_pretenicas_se_inclinan_por_trabajar,
    voy_a_casa_y_voy_a_la_parada,
    si_estoy_impacientado_y_no_cojo_quaguna,
    si_no_cojo_quaguna_y_quiero_caminar,
    si_llego_a_mi_destino_y_es_el_trabajo,
    si_llego_a_mi_destino_y_es_casa,
  ]:
    intencion = funcion(state)
    if intencion is not None:
      break

  return intencion

state = {
  'trabajo_terminado': True,
  'en_casa': False,
  'trabajo_pendiente': False,
  'en_la_parada': False,
  'planificado': False,
  'en_la_cola_de_la_quaguna': False,
  'impaciente': False,
  'aguagunando_que_no_es_mia': False,
  'en_parada_que_toca_bajarse': False,
  'adelanta_la_quaguna_que_no_es_mia': False,
  'cojo_quaguna': False,
  'quiero_caminar': False,
  'llego_a_mi_destino': False,
  'es_el_trabajo': False,
  'es_casa': False,
}