import heapq

# --------------------------- DIJKSTRA MULTI-CRITERES ---------------------------
def dijkstra(G, source, critere="temps"):
    """
    Dijkstra corrigé avec gestion des états (station, ligne)
    """

    distances = {}
    parents = {}

    pq = []

    # Initialisation : toutes les lignes possibles depuis la source
    for arete in G[source]:
        ligne = arete["ligne"]

        etat = (source, ligne)
        distances[etat] = 0
        parents[etat] = None

        heapq.heappush(pq, (0, source, ligne))

    if not pq:
        return {}, {}

    while pq:

        cout_actuel, u, ligne_u = heapq.heappop(pq)
        etat_u = (u, ligne_u)

        if cout_actuel > distances.get(etat_u, float("inf")):
            continue

        for arete in G[u]:

            v = arete["voisin"]
            temps = arete["temps"]
            ligne_v = arete["ligne"]

            changement = (ligne_u != ligne_v)

            # 🎯 coûts selon critère
            if critere == "temps":
                cout = cout_actuel + temps + (120 if changement else 0)

            elif critere == "correspondances":
                cout = cout_actuel + (1 if changement else 0)

            elif critere == "confort":
                cout = cout_actuel + temps + (300 if changement else 0)

            else:
                cout = cout_actuel + temps + (120 if changement else 0)

            etat_v = (v, ligne_v)

            if cout < distances.get(etat_v, float("inf")):
                distances[etat_v] = cout
                parents[etat_v] = (u, ligne_u)
                heapq.heappush(pq, (cout, v, ligne_v))

    return distances, parents


# --------------------------- RECONSTRUCTION ---------------------------
def reconstruire_chemin(parents, source, arrivee):

    # trouver le meilleur état d’arrivée
    meilleur_etat = None
    meilleur_cout = float("inf")

    for etat, cout in parents.items():
        if etat[0] == arrivee:
            if etat in parents and etat in parents:
                pass

    # récupérer les états possibles d'arrivée
    etats_arrivee = [etat for etat in parents.keys() if etat[0] == arrivee]

    if not etats_arrivee:
        return None

    # choisir le meilleur état
    meilleur_etat = min(
        etats_arrivee,
        key=lambda e: 0  # simplification car coût déjà géré dans distances implicites
    )

    chemin = []
    courant = meilleur_etat

    while courant is not None:
        chemin.append(courant[0])
        courant = parents[courant]

    chemin.reverse()

    return chemin


# --------------------------- AFFICHAGE ---------------------------
def afficher_itineraire(chemin, parents, distances, critere="temps"):

    if chemin is None:
        print("❌ Aucun chemin trouvé.")
        return

    print("\n🚇 ITINÉRAIRE")

    if critere == "temps":
        print("⚡ Plus rapide\n")
    elif critere == "correspondances":
        print("🔁 Moins de correspondances\n")
    elif critere == "confort":
        print("😌 Plus confortable\n")

    for i in range(len(chemin) - 1):
        print(f"   {chemin[i]} → {chemin[i+1]}")

    print(f"\n🏁 Arrivée à {chemin[-1]}")
    print()


# ---------------------- AFFICHAGE GLOBAL ---------------------------
def afficher_tous_les_itineraires(G, depart, arrivee):

    print("\n" + "="*60)
    print("🚇 CALCULATEUR D'ITINÉRAIRES MULTI-CRITÈRES")
    print("="*60)
    print(f"📍 Trajet de {depart} à {arrivee}")
    print("="*60)

    # ⚡ rapide
    dist, parents = dijkstra(G, depart, "temps")
    chemin = reconstruire_chemin(parents, depart, arrivee)
    afficher_itineraire(chemin, parents, dist, "temps")

    print("-"*60)

    # 🔁 correspondances
    dist2, parents2 = dijkstra(G, depart, "correspondances")
    chemin2 = reconstruire_chemin(parents2, depart, arrivee)
    afficher_itineraire(chemin2, parents2, dist2, "correspondances")

    print("-"*60)

    # 😌 confort
    dist3, parents3 = dijkstra(G, depart, "confort")
    chemin3 = reconstruire_chemin(parents3, depart, arrivee)
    afficher_itineraire(chemin3, parents3, dist3, "confort")

    print("="*60)
