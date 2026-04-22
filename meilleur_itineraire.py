import heapq

def dijkstra(graphe, depart, arrivee):
    # Initialisation
    distances = {station: float('inf') for station in graphe}
    distances[depart] = 0

    precedent = {station: None for station in graphe}

    # File de priorité (distance, station, ligne)
    file = [(0, depart, None)]

    while file:
        distance_actuelle, station_actuelle, ligne_actuelle = heapq.heappop(file)

        if station_actuelle == arrivee:
            break

        for voisin, temps, ligne in graphe[station_actuelle]:
            # Ajouter temps de correspondance si changement de ligne
            correspondance = 0
            if ligne_actuelle is not None and ligne != ligne_actuelle:
                correspondance = 120

            nouvelle_distance = distance_actuelle + temps + correspondance

            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedent[voisin] = (station_actuelle, ligne)
                heapq.heappush(file, (nouvelle_distance, voisin, ligne))

    return distances, precedent


# à suivre...
