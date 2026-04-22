import heapq

def dijkstra(graphe, depart, arrivee):
    """
    Calcule le plus court chemin (en temps) entre deux stations
    en utilisant l'algorithme de Dijkstra.

    Paramètres :
    ------------
    graphe (dict) : dictionnaire représentant le graphe sous forme de liste d'adjacence.
    depart (str) : nom de la station de départ
    arrivee (str) : nom de la station d'arrivée

    Retour :
    --------
    distances (dict) : dictionnaire des distances minimales depuis la station de départ
    precedent (dict) : dictionnaire permettant de reconstruire le chemin
    
    """

    # Initialisation des distances : infini pour toutes les stations
    distances = {station: float('inf') for station in graphe}
    
    # La distance de départ est nulle
    distances[depart] = 0

    # Dictionnaire pour reconstruire le chemin
    precedent = {station: None for station in graphe}

    # File de priorité (min-heap)
    # Contient des tuples : (distance, station, ligne_actuelle)
    file = [(0, depart, None)]

    # Boucle principale de Dijkstra
    while file:
        # On récupère la station avec la plus petite distance
        distance_actuelle, station_actuelle, ligne_actuelle = heapq.heappop(file)

        # Si on arrive à la destination, on peut arrêter
        if station_actuelle == arrivee:
            break

        # Parcours des voisins de la station actuelle
        for voisin, temps, ligne in graphe[station_actuelle]:
            
            # Calcul du temps de correspondance
            correspondance = 0
            if ligne_actuelle is not None and ligne != ligne_actuelle:
                correspondance = 120  # Temps fixe de correspondance

            # Nouvelle distance en passant par cette station
            nouvelle_distance = distance_actuelle + temps + correspondance

            # Mise à jour si on trouve un chemin plus court
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                
                # On mémorise le chemin (station précédente + ligne utilisée)
                precedent[voisin] = (station_actuelle, ligne)
                
                # Ajout dans la file de priorité
                heapq.heappush(file, (nouvelle_distance, voisin, ligne))

    return distances, precedent


# à suivre...
