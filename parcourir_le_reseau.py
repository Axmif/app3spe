"""
=============================================================
Contenu :
  - BFS : chemin avec le moins d'arrêts
  - DFS : exploration en profondeur
  - Vérification de la connexité du réseau
  - Identification des stations de correspondance
=============================================================
"""

from collections import deque
from charger_donnees import charger_reseau



def bfs(graphe, depart, arrivee):
    """
    Parcours en largeur (Breadth-First Search).

    Trouve le chemin passant par le MOINS D'ARRÊTS entre
    `depart` et `arrivee`, sans tenir compte des poids.

    Paramètres
    ----------
    graphe : dictionnaire
    depart : station de départ
    arrivee  : station d'arrivée

    Retourne
    --------
    dict avec :
      'path'        : liste des stations du chemin ([] si introuvable)
      'stops'       : nombre d'arrêts intermédiaires
      'visited'     : liste de toutes les stations visitées (ordre BFS)
      'found'       : booléen
    """

    if depart not in graphe:
        raise ValueError(f"Station inconnue : {depart}")

    if arrivee not in graphe:
        raise ValueError(f"Station inconnue : {arrivee}")

    file = deque([(depart, [depart])])

    visites = set([depart])

    ordre_visite = []

    while file:

        station, chemin = file.popleft()

        ordre_visite.append(station)

        # Arrivée trouvée
        if station == arrivee:

            return {
                "path": chemin,
                "stops": len(chemin) - 2,
                "visited": ordre_visite,
                "found": True
            }

        # Parcours des voisins
        for arete in graphe[station]:

            voisin = arete["voisin"]

            if voisin not in visites:

                visites.add(voisin)

                file.append((voisin, chemin + [voisin]))

    return {
        "path": [],
        "stops": -1,
        "visited": ordre_visite,
        "found": False
    }


def dfs(graphe, depart, arrivee=None):
    """
    Parcours en profondeur (Depth-First Search).

    Si `arrivee` est fourni, s'arrête dès que la station est trouvée
    et retourne le chemin. Sinon, explore tout le graphe accessible
    depuis `depart`.

    Paramètres
    ----------
    graphe : dictionnaire
    depart : station de départ
    arrivee   : (optionnel) station cible

    Retourne
    --------
    dict avec :
      'path'    : chemin vers `end` (si précisé et trouvé)
      'visited' : liste de toutes les stations visitées (ordre DFS)
      'found'   : booléen (False si end=None car pas de cible)
    """

    if depart not in graphe:
        raise ValueError(f"Station inconnue : {depart}")

    visites = set()

    ordre_visite = []

    def parcours(station, chemin):

        visites.add(station)

        ordre_visite.append(station)

        # Arrivée trouvée
        if station == arrivee:
            return chemin

        for arete in graphe[station]:

            voisin = arete["voisin"]

            if voisin not in visites:

                resultat = parcours(voisin, chemin + [voisin])

                if resultat is not None:
                    return resultat

        return None

    chemin = parcours(depart, [depart])

    if arrivee is None:

        return {
            "path": [],
            "visited": ordre_visite,
            "found": False
        }

    return {
        "path": chemin if chemin else [],
        "visited": ordre_visite,
        "found": chemin is not None
    }

def verifier_connexite(graphe):
    """
    Vérifie que toutes les stations du réseau sont accessibles
    depuis n'importe quelle autre station (graphe connexe).

    Stratégie : BFS depuis la première station.
    Si toutes les stations sont atteintes → graphe connexe.

    Retourne
    --------
    dict avec :
      'is_connected'     : booléen
      'reachable_count'  : nombre de stations atteintes
      'total_count'      : nombre total de stations
      'unreachable'      : liste des stations inaccessibles ([] si connexe)
    """

    stations = list(graphe.keys())

    if not stations:

        return {
            "is_connected": True,
            "reachable_count": 0,
            "total_count": 0,
            "unreachable": []
        }

    depart = stations[0]

    visites = set([depart])

    file = deque([depart])

    while file:

        station = file.popleft()

        for arete in graphe[station]:

            voisin = arete["voisin"]

            if voisin not in visites:

                visites.add(voisin)

                file.append(voisin)

    inaccessibles = [
        s for s in stations
        if s not in visites
    ]

    return {
        "is_connected": len(inaccessibles) == 0,
        "reachable_count": len(visites),
        "total_count": len(stations),
        "unreachable": inaccessibles
    }


def get_transfer_stations(reseau):
    """
    Identifie et retourne les stations de correspondance du réseau,
    c'est-à-dire les stations desservies par au moins deux lignes.

    Retourne
    --------
    Liste de tuples (station, lignes) triée par nom de station.
    """

    resultats = []

    for correspondance in reseau["correspondances"]:

        station = correspondance["station"]

        lignes = correspondance["lignes"]

        resultats.append(
            (station, lignes)
        )

    return sorted(resultats)

# à enlever (partie 5 interface)
def display_bfs_result(result: dict, start: str, end: str) -> None:
    """Affiche le résultat d'un parcours BFS de façon lisible."""
    print("\n" + "═" * 55)
    print(f"  BFS — Chemin avec le moins d'arrêts")
    print(f"  De : {start}  →  Vers : {end}")
    print("═" * 55)

    if not result['found']:
        print("  ✗ Aucun chemin trouvé.")
        return

    print(f"  Nombre d'arrêts intermédiaires : {result['stops']}")
    print(f"  Nombre total de stations       : {len(result['path'])}")
    print()
    for i, station in enumerate(result['path']):
        if station == start:
            prefix = "   DÉPART   :"
        elif station == end:
            prefix = "   ARRIVÉE  :"
        else:
            prefix = f"  ·  arrêt {i:2d} :"
        print(f"{prefix} {station}")

    print(f"\n  Stations visitées par BFS : {len(result['visited'])}")
    print("═" * 55)

# à enlever (partie 5 interface)
def display_dfs_result(result: dict, start: str, end: str = None) -> None:
    """Affiche le résultat d'un parcours DFS de façon lisible."""
    print("\n" + "═" * 55)
    print(f"  DFS — Exploration en profondeur")
    if end:
        print(f"  De : {start}  →  Vers : {end}")
    else:
        print(f"  Depuis : {start}  (exploration complète)")
    print("═" * 55)

    if end and result['found']:
        print(f"  Chemin trouvé ({len(result['path'])} stations) :")
        for station in result['path']:
            marker = ":)" if station == start else (":(" if station == end else "·")
            print(f"  {marker}  {station}")
    elif end:
        print("  ✗ Aucun chemin trouvé.")

    print(f"\n  Ordre de visite DFS ({len(result['visited'])} stations) :")
    print("  " + " → ".join(result['visited'][:10])
          + (" → ..." if len(result['visited']) > 10 else ""))
    print("═" * 55)


def display_connectivity(result: dict) -> None:
    """Affiche le résultat de la vérification de connexité."""
    print("\n" + "═" * 55)
    print("  VÉRIFICATION DE CONNEXITÉ DU RÉSEAU")
    print("═" * 55)
    print(f"  Stations totales     : {result['total_count']}")
    print(f"  Stations accessibles : {result['reachable_count']}")

    if result['is_connected']:
        print("    Le réseau est CONNEXE.")
        print("      Toutes les stations sont accessibles.")
    else:
        print("    Le réseau N'EST PAS connexe !")
        print(f"      {len(result['unreachable'])} station(s) inaccessible(s) :")
        for s in result['unreachable']:
            print(f"        • {s}")
    print("═" * 55)


def display_transfer_stations(transfers: list) -> None:
    """Affiche les stations de correspondance identifiées."""
    print("\n" + "═" * 55)
    print(f"  STATIONS DE CORRESPONDANCE ({len(transfers)} trouvées)")
    print("═" * 55)
    if not transfers:
        print("  Aucune station de correspondance.")
    else:
        for station, lines in transfers:
            lines_str = ", ".join(sorted(lines))
            print(f"   {station:<35} [{lines_str}]")
    print("═" * 55)


if __name__ == "__main__":
    reseau = charger_reseau("bordeaux.json")
    graphe = reseau["graphe"]
    resultat = bfs(
    graphe,
    "Quinconces",
    "Pessac Bersol"
)

    print(resultat)

    resultat = dfs(
    graphe,
    "Quinconces",
    "Floirac Dravemont"
)

    print(resultat)

    connectivite = verifier_connexite(graphe)
    print(connectivite)

    transfers = get_transfer_stations(reseau)
    print(transfers)