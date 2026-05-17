# --------------------------- DIJKSTRA MULTI-CRITÈRES ---------------------------
import heapq

def dijkstra(G, source, critere="temps"):
    """
    Dijkstra avec gestion de plusieurs critères :
    - "temps" : plus rapide
    - "correspondances" : moins de changements
    - "confort" : pénalise les correspondances

    Cette version tient compte de la ligne actuelle
    dans l'état du graphe :
        (station, ligne)

    Cela évite les faux plus courts chemins
    liés aux correspondances.

    Paramètres
    ----------

    G: liste d'adjacence :
    {
        station: [
            {
                "voisin": str,
                "temps": int,
                "ligne": str
            }
        ]
    }

    source: nom de la station de départ (str)
    critere: le critère utilisé

    Retourne
    -------
    un tuple (distances, parents):
    distances: dictionnaire {station: temps minimal depuis la station de départ}
    parents: dictionnaire {station: (station précédente, ligne)}
    """

    # ---------------- ÉTATS ----------------
    # Un état = (station, ligne_actuelle)

    distances_etats = {}
    parents_etats = {}

    # File de priorité
    file = []

    # État initial
    etat_initial = (source, None)

    distances_etats[etat_initial] = 0
    parents_etats[etat_initial] = None

    heapq.heappush(file, (0, source, None))

    while file:

        distance_u, u, ligne_u = heapq.heappop(file)

        # Ignore les anciennes entrées du tas
        if distance_u > distances_etats[(u, ligne_u)]:
            continue

        for arete in G[u]:

            v = arete["voisin"]
            temps = arete["temps"]
            ligne_v = arete["ligne"]

            # Correspondance ?
            changement = (
                ligne_u is not None
                and ligne_u != ligne_v
            )

            # ---------------- COÛTS ----------------
            if critere == "temps":

                cout = distance_u + temps

                if changement:
                    cout += 120

            elif critere == "correspondances":

                cout = distance_u

                if changement:
                    cout += 1

            elif critere == "confort":

                cout = distance_u + temps

                if changement:
                    cout += 300

            else:

                cout = distance_u + temps

                if changement:
                    cout += 120

            nouvel_etat = (v, ligne_v)

            # Relaxation
            if (
                nouvel_etat not in distances_etats
                or cout < distances_etats[nouvel_etat]
            ):

                distances_etats[nouvel_etat] = cout
                parents_etats[nouvel_etat] = (u, ligne_u)

                heapq.heappush(
                    file,
                    (cout, v, ligne_v)
                )

    # -------------------------------------------------
    # CONVERSION VERS LE FORMAT ORIGINAL
    # distances : {station: cout}
    # parents   : {station: (station_precedente, ligne)}
    # -------------------------------------------------

    distances = {
        station: float("inf")
        for station in G
    }

    parents = {
        station: None
        for station in G
    }

    # Pour chaque état final
    for (station, ligne), cout in distances_etats.items():

        if cout < distances[station]:

            distances[station] = cout

            parent_etat = parents_etats[(station, ligne)]

            if parent_etat is not None:

                station_parent, ligne_parent = parent_etat

                # La ligne utilisée pour arriver ici
                parents[station] = (
                    station_parent,
                    ligne
                )

    return distances, parents


# --------------------------- RECONSTRUCTION DU CHEMIN ---------------------------
def reconstruire_chemin(parents, source, arrivee):
    """
    Reconstruit le chemin optimal entre deux stations.
    """

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


# ------------------------- AFFICHAGE D'UN ITINÉRAIRE ---------------------------
def afficher_itineraire(chemin, parents, distances, critere="temps"):
    """
    Affiche un itinéraire lisible :
    - lignes utilisées
    - correspondances
    - stations
    - temps total
    """

    if chemin is None:
        print("❌ Aucun chemin trouvé.")
        return

    print("\n🚇 ITINÉRAIRE")

    # 🎯 TITRE SELON CRITÈRE
    if critere == "temps":
        print("⚡ Plus rapide\n")

    elif critere == "correspondances":
        print("🔁 Moins de correspondances\n")

    elif critere == "confort":
        print("😌 Plus confortable\n")

    ligne_actuelle = None

    for i in range(len(chemin) - 1):

        station = chemin[i]
        suivante = chemin[i + 1]

        ligne = parents[suivante][1]

        if ligne_actuelle is None:
            print(f"➡️ Prendre la ligne {ligne} à {station}")

        elif ligne != ligne_actuelle:
            print(
                f"🔁 Correspondance à {station} "
                f"(ligne {ligne_actuelle} → {ligne})"
            )

        print(
            f"   {station} → {suivante} "
            f"(ligne {ligne})"
        )

        ligne_actuelle = ligne

    print(f"\n🏁 Arrivée à {chemin[-1]}")

    # Affichage du coût
    if critere == "correspondances":
        print(
            f"🔁 Nombre de correspondances : "
            f"{distances[chemin[-1]]}"
        )

    else:
        print(
            f"⏱ Temps total : "
            f"{distances[chemin[-1]]} secondes"
        )

    print()


# ---------------------- AFFICHAGE DES 3 ITINÉRAIRES ---------------------------
def afficher_tous_les_itineraires(G, depart, arrivee):

    print("\n" + "="*60)
    print("🚇 CALCULATEUR D'ITINÉRAIRES MULTI-CRITÈRES")
    print("="*60)
    print(f"📍 Trajet de {depart} à {arrivee}")
    print("="*60)

    # ⚡ Plus rapide
    dist, parents = dijkstra(G, depart, "temps")
    chemin = reconstruire_chemin(parents, depart, arrivee)
    afficher_itineraire(chemin, parents, dist, "temps")

    print("-"*60)

    # 🔁 Moins de correspondances
    dist2, parents2 = dijkstra(G, depart, "correspondances")
    chemin2 = reconstruire_chemin(parents2, depart, arrivee)
    afficher_itineraire(
        chemin2,
        parents2,
        dist2,
        "correspondances"
    )

    print("-"*60)

    # 😌 Plus confortable
    dist3, parents3 = dijkstra(G, depart, "confort")
    chemin3 = reconstruire_chemin(parents3, depart, arrivee)
    afficher_itineraire(
        chemin3,
        parents3,
        dist3,
        "confort"
    )

    print("="*60)