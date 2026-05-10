def dijkstra(G, source):
    """
    Algorithme de Dijkstra pour le réseau de transport.

    G est une liste d'adjacence :
    {
        station: [
            {
                "voisin": str,
                "temps": int,
                "ligne": str
            }
        ]
    }
    Atention: cette version de dijkstra peut: ajouter des correspondances inutiles,
    ou oublier des correspondances,
    donc donner un faux plus court chemin

    Retourne
    -------
    un tuple (distances, parents):
    distances: dictionnaire {station: temps minimal depuis la station de départ}
    parents: dictionnaire {station: (station précédente, ligne)}

    """

    distances = {station: float("inf") for station in G}
    distances[source] = 0

    parents = {station: None for station in G}

    # Ligne utilisée pour arriver à la station
    lignes = {station: None for station in G}

    non_visites = set(G)

    while non_visites:

        # Sommet avec la plus petite distance
        u = min(non_visites, key=lambda x: distances[x])

        # Si inaccessible
        if distances[u] == float("inf"):
            break

        # Parcours des voisins
        for arete in G[u]:

            v = arete["voisin"]
            temps = arete["temps"]
            ligne = arete["ligne"]

            cout = distances[u] + temps

            # Correspondance
            if lignes[u] is not None and lignes[u] != ligne:
                cout += 120

            # Relaxation
            if cout < distances[v]:

                distances[v] = cout

                # Parent + ligne utilisée
                parents[v] = (u, ligne)

                lignes[v] = ligne

        non_visites.remove(u)

    return distances, parents

#---------------------------RECONSTRUCTION DU CHEMIN-----------------------------------------
def reconstruire_chemin(parents, source, arrivee):
    """
    Reconstruit le chemin optimal entre deux stations.
    """

    # si dijkstra ne trouve pas de chemin
    if parents[arrivee] is None and source != arrivee:
        return None

    chemin = []
    courant = arrivee

    while courant != source:
        chemin.append(courant)
        courant = parents[courant][0]

    chemin.append(source)
    chemin.reverse()

    return chemin

#-------------------------AFFICHAGE DE L'ITINERAIRE---------------------------------------
def afficher_itineraire(chemin, parents, distances):
    """
    Affiche un itinéraire lisible :
    - lignes utilisées
    - correspondances
    - stations
    - temps total
    """

    print("\n🚇 ITINÉRAIRE OPTIMAL\n")

    ligne_actuelle = None

    for i in range(len(chemin) - 1):

        station = chemin[i]
        suivante = chemin[i + 1]

        ligne = parents[suivante][1]

        # Détection de correspondance
        if ligne_actuelle is None:
            print(f"➡️ Prendre la ligne {ligne} à {station}")

        elif ligne != ligne_actuelle:
            print(f"🔁 Correspondance à {station} (ligne {ligne_actuelle} → {ligne})")

        print(f"   {station} → {suivante} (ligne {ligne})")

        ligne_actuelle = ligne

    print(f"\n🏁 Arrivée à {chemin[-1]}")
    print(f"⏱ Temps total : {distances[chemin[-1]]} secondes\n")