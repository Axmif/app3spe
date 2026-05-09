def dijkstra(G, source):
    """
    Algorithme de Dijkstra adapté aux réseaux de transport.

    Chaque arête contient :
    - temps de trajet
    - ligne de transport

    Une correspondance coûte 120 secondes si changement de ligne.
    """

    # Distance minimale vers chaque station
    distances = {x: float('inf') for x in G}
    distances[source] = 0

    # Permet de reconstruire le chemin
    parents = {x: None for x in G}

    # Ligne utilisée pour atteindre chaque station
    lignes = {x: None for x in G}

    # Ensemble des stations non traitées
    non_visites = set(G)

    while non_visites:

        # Choix du sommet avec distance minimale
        u = min(non_visites, key=lambda x: distances[x])

        # Exploration des voisins
        for v in G[u]:

            for temps, ligne in G[u][v]:

                # Coût de base
                cout = distances[u] + temps

                # Ajout correspondance si changement de ligne
                if lignes[u] is not None and lignes[u] != ligne:
                    cout += 120

                # Relaxation
                if cout < distances[v]:
                    distances[v] = cout
                    parents[v] = (u, ligne)
                    lignes[v] = ligne

        non_visites.remove(u)

    return distances, parents

#---------------------------RECONSTRUCTION DU CHEMIN-----------------------------------------
def reconstruire_chemin(parents, source, arrivee):
    """
    Reconstruit le chemin optimal entre deux stations.
    """

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
