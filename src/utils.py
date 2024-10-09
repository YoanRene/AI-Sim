import random

def get_random_parada(grafo, county=None):
    """
    Returns a random parada (stop) from the graph.

    Args:
        grafo: The graph object representing the transport system.

    Returns:
        A random Parada object from the graph.
    """
    paradas = list(grafo.vertices.values())
    a = [p for p in paradas if p.county == county]
    return random.choice(a)
