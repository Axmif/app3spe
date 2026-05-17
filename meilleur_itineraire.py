# --------------------------- DIJKSTRA MULTI-CRITÈRES ---------------------------
def dijkstra(G, source, critere="temps"):
    """
    Dijkstra avec gestion de plusieurs critères :
    - "temps" : plus rapide
    - "correspondances" : moins de changements
    - "confort" : pénalise les correspondances

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
    lignes = {station: None for station in G}

    non_visites = set(G)

    while non_visites:

        u = min(non_visites, key=lambda x: distances[x])

        if distances[u] == float("inf"):
            break

        for arete in G[u]:

            v = arete["voisin"]
            temps = arete["temps"]
            ligne = arete["ligne"]

            changement = lignes[u] is not None and lignes[u] != ligne

            # 🔥 Gestion des critères
            if critere == "temps":
                cout = distances[u] + temps
                if changement:
                    cout += 120      # temps de correspondance réelle

            elif critere == "correspondances":
                cout = distances[u]
                if changement:
                    cout += 1      # on minimise uniquement le nombre

            elif critere == "confort":
                cout = distances[u] + temps
                if changement:
                    cout += 300  # pénalité de confort (éviter les changements)

            else:
                cout = distances[u] + temps
                if changement:
                    cout += 120

            # Relaxation
            if cout < distances[v]:
                distances[v] = cout
                parents[v] = (u, ligne)
                lignes[v] = ligne

        non_visites.remove(u)

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
            print(f"🔁 Correspondance à {station} (ligne {ligne_actuelle} → {ligne})")

        print(f"   {station} → {suivante} (ligne {ligne})")

        ligne_actuelle = ligne

    print(f"\n🏁 Arrivée à {chemin[-1]}")

    # Affichage du coût
    if critere == "correspondances":
        print(f"🔁 Nombre de correspondances : {distances[chemin[-1]]}")
    else:
        print(f"⏱ Temps total : {distances[chemin[-1]]} secondes")

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
    afficher_itineraire(chemin2, parents2, dist2, "correspondances")

    print("-"*60)

    # 😌 Plus confortable
    dist3, parents3 = dijkstra(G, depart, "confort")
    chemin3 = reconstruire_chemin(parents3, depart, arrivee)
    afficher_itineraire(chemin3, parents3, dist3, "confort")

    print("="*60)
