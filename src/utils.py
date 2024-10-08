import random

def get_random_parada(grafo):
    """
    Returns a random parada (stop) from the graph.

    Args:
        grafo: The graph object representing the transport system.

    Returns:
        A random Parada object from the graph.
    """
    paradas = list(grafo.vertices.values())
    return random.choice(paradas)
