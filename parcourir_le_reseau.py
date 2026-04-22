"""
=============================================================
Contenu :
  - Classe TransportGraph : structure de données (liste d'adjacence)
  - BFS : chemin avec le moins d'arrêts
  - DFS : exploration en profondeur
  - Vérification de la connexité du réseau
  - Identification des stations de correspondance
=============================================================
"""

from collections import defaultdict, deque

class TransportGraph:
    """
    Graphe pondéré représentant un réseau de transport en commun.

    Attributs
    ---------
    adjacency : dict  { station : [(voisin, poids, ligne), ...] }
    lines     : dict  { nom_ligne : [stations ordonnées] }
    transfers : dict  { station : [lignes desservies] }
    """

    def __init__(self):
        self.adjacency = defaultdict(list)   # liste d'adjacence
        self.lines     = {}                  # lignes et leurs stations
        self.transfers = defaultdict(set)    # station → ensemble de lignes

    # ── Ajout d'une connexion (arc orienté dans les deux sens) ──
    def add_connection(self, station_a: str, station_b: str,
                       weight: int, line: str) -> None:
        """Ajoute une connexion bidirectionnelle entre deux stations."""
        self.adjacency[station_a].append((station_b, weight, line))
        self.adjacency[station_b].append((station_a, weight, line))

    # ── Enregistrement d'une ligne ──────────────────────────────
    def add_line(self, line_name: str, stations: list) -> None:
        """Enregistre les stations d'une ligne et met à jour les correspondances."""
        self.lines[line_name] = stations
        for station in stations:
            self.transfers[station].add(line_name)

    # ── Propriétés utiles ───────────────────────────────────────
    @property
    def all_stations(self) -> list:
        """Retourne la liste de toutes les stations du réseau."""
        return list(self.adjacency.keys())

    @property
    def transfer_stations(self) -> list:
        """Retourne les stations desservies par au moins deux lignes."""
        return [s for s, lines in self.transfers.items() if len(lines) >= 2]
      

def bfs(graph: TransportGraph, start: str, end: str) -> dict:
    """
    Parcours en largeur (Breadth-First Search).

    Trouve le chemin passant par le MOINS D'ARRÊTS entre
    `start` et `end`, sans tenir compte des poids.

    Paramètres
    ----------
    graph : TransportGraph
    start : station de départ
    end   : station d'arrivée

    Retourne
    --------
    dict avec :
      'path'        : liste des stations du chemin ([] si introuvable)
      'stops'       : nombre d'arrêts intermédiaires
      'visited'     : liste de toutes les stations visitées (ordre BFS)
      'found'       : booléen
    """
    if start not in graph.adjacency:
        raise ValueError(f"Station de départ inconnue : '{start}'")
    if end not in graph.adjacency:
        raise ValueError(f"Station d'arrivée inconnue : '{end}'")

    # File : chaque élément = (station_courante, chemin_parcouru)
    queue    = deque([(start, [start])])
    visited  = set([start])
    bfs_order = []           # ordre de visite pour affichage pédagogique

    while queue:
        current, path = queue.popleft()
        bfs_order.append(current)

        if current == end:
            return {
                'path'    : path,
                'stops'   : len(path) - 2,   # sans départ ni arrivée
                'visited' : bfs_order,
                'found'   : True,
            }

        for neighbor, _weight, _line in graph.adjacency[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return {'path': [], 'stops': -1, 'visited': bfs_order, 'found': False}


def dfs(graph: TransportGraph, start: str, end: str = None) -> dict:
    """
    Parcours en profondeur (Depth-First Search).

    Si `end` est fourni, s'arrête dès que la station est trouvée
    et retourne le chemin. Sinon, explore tout le graphe accessible
    depuis `start`.

    Paramètres
    ----------
    graph : TransportGraph
    start : station de départ
    end   : (optionnel) station cible

    Retourne
    --------
    dict avec :
      'path'    : chemin vers `end` (si précisé et trouvé)
      'visited' : liste de toutes les stations visitées (ordre DFS)
      'found'   : booléen (False si end=None car pas de cible)
    """
    if start not in graph.adjacency:
        raise ValueError(f"Station de départ inconnue : '{start}'")

    visited   = set()
    dfs_order = []

    # ── Version récursive ────────────────────────────────────
    def _dfs_recursive(node: str, path: list) -> list | None:
        visited.add(node)
        dfs_order.append(node)

        if node == end:
            return path

        for neighbor, _weight, _line in graph.adjacency[node]:
            if neighbor not in visited:
                result = _dfs_recursive(neighbor, path + [neighbor])
                if result is not None:
                    return result

        return None  # cible non trouvée sur cette branche

    result_path = _dfs_recursive(start, [start])

    if end is None:
        return {'path': [], 'visited': dfs_order, 'found': False}

    if result_path:
        return {'path': result_path, 'visited': dfs_order, 'found': True}
    else:
        return {'path': [], 'visited': dfs_order, 'found': False}

def check_connectivity(graph: TransportGraph) -> dict:
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
    stations = graph.all_stations
    if not stations:
        return {
            'is_connected'    : True,
            'reachable_count' : 0,
            'total_count'     : 0,
            'unreachable'     : [],
        }

    # BFS depuis la première station
    start    = stations[0]
    visited  = {start}
    queue    = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor, _w, _l in graph.adjacency[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    unreachable = [s for s in stations if s not in visited]

    return {
        'is_connected'    : len(unreachable) == 0,
        'reachable_count' : len(visited),
        'total_count'     : len(stations),
        'unreachable'     : unreachable,
    }


def get_transfer_stations(graph: TransportGraph) -> list:
    """
    Identifie et retourne les stations de correspondance du réseau,
    c'est-à-dire les stations desservies par au moins deux lignes.

    Retourne
    --------
    Liste de tuples (station, frozenset(lignes)) triée par nom de station.
    """
    result = [
        (station, frozenset(lines))
        for station, lines in graph.transfers.items()
        if len(lines) >= 2
    ]
    return sorted(result, key=lambda x: x[0])


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


import json
import os

def load_graph_from_json(filepath: str) -> TransportGraph:
    """
    Construit un TransportGraph à partir d'un fichier JSON
    au format défini dans le cahier des charges :
      {
        "lignes": { "L1": {"nom": "...", "couleur": "...",
                           "stations": [...]} },
        "connexions": [{"depart": "...", "arrivee": "...",
                        "temps": 90, "ligne": "L1"}, ...],
        "correspondances": [{"station": "...", "lignes": [...],
                             "temps": 120}, ...]
      }
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    g = TransportGraph()

    # ── Lignes ──────────────────────────────────────────────
    for line_id, info in data.get("lignes", {}).items():
        g.add_line(line_id, info["stations"])

    # ── Connexions ──────────────────────────────────────────
    for conn in data.get("connexions", []):
        g.add_connection(
            conn["depart"], conn["arrivee"],
            conn["temps"],  conn["ligne"]
        )

    # ── Correspondances (enrichissement des transfers) ──────
    for transf in data.get("correspondances", []):
        for line in transf["lignes"]:
            g.transfers[transf["station"]].add(line)

    return g

def build_demo_graph() -> TransportGraph:
    """
    Construit un petit réseau de démonstration inspiré du métro parisien.

    Ligne 1  :  Argentine — Charles de Gaulle-Étoile — George V — Franklin Roosevelt
    Ligne 2  :  Charles de Gaulle-Étoile — Ternes — Courcelles — Monceau
    Ligne 6  :  Charles de Gaulle-Étoile — Kléber — Boissière
    """
    g = TransportGraph()

    # ── Ligne 1 ─────────────────────────────────────────────
    g.add_line("1", ["Argentine", "Charles de Gaulle-Étoile",
                      "George V", "Franklin Roosevelt"])
    g.add_connection("Argentine",                 "Charles de Gaulle-Étoile", 90,  "1")
    g.add_connection("Charles de Gaulle-Étoile",  "George V",                 60,  "1")
    g.add_connection("George V",                  "Franklin Roosevelt",        75,  "1")

    # ── Ligne 2 ─────────────────────────────────────────────
    g.add_line("2", ["Charles de Gaulle-Étoile", "Ternes", "Courcelles", "Monceau"])
    g.add_connection("Charles de Gaulle-Étoile",  "Ternes",     80, "2")
    g.add_connection("Ternes",                    "Courcelles", 70, "2")
    g.add_connection("Courcelles",                "Monceau",    65, "2")

    # ── Ligne 6 ─────────────────────────────────────────────
    g.add_line("6", ["Charles de Gaulle-Étoile", "Kléber", "Boissière"])
    g.add_connection("Charles de Gaulle-Étoile",  "Kléber",    55, "6")
    g.add_connection("Kléber",                    "Boissière", 60, "6")

    return g

def main():
    print("\n" + "╔" + "═" * 53 + "╗")
    print("║   APP — Partie 2 : Parcours du réseau              ║")
    print("╚" + "═" * 53 + "╝")

    # ── Chargement du graphe ─────────────────────────────────
    # Essaie d'abord un vrai fichier JSON ; sinon, utilise la démo
    json_candidates = ["paris.json", "data/paris.json"]
    graph = None

    for path in json_candidates:
        if os.path.exists(path):
            print(f"\n   Chargement de : {path}")
            graph = load_graph_from_json(path)
            break

    if graph is None:
        print("\n    Aucun fichier JSON trouvé.")
        print("      Utilisation du réseau de démonstration (Paris simplifié).\n")
        graph = build_demo_graph()

    print(f"  Réseau chargé : {len(graph.all_stations)} stations, "
          f"{len(graph.lines)} lignes.")


    print("\n\n── 2a. BFS (Breadth-First Search) ──────────────────────")
    bfs_start = "Argentine"
    bfs_end   = "Monceau"

    bfs_result = bfs(graph, bfs_start, bfs_end)
    display_bfs_result(bfs_result, bfs_start, bfs_end)

  
    print("\n\n── 2b. DFS (Depth-First Search) ────────────────────────")

    # DFS avec cible
    dfs_start  = "Argentine"
    dfs_end    = "Boissière"
    dfs_result = dfs(graph, dfs_start, dfs_end)
    display_dfs_result(dfs_result, dfs_start, dfs_end)

    # DFS exploration complète (sans cible)
    dfs_full = dfs(graph, dfs_start)
    display_dfs_result(dfs_full, dfs_start)

    
    print("\n\n── 2c. Vérification de connexité ───────────────────────")
    connectivity = check_connectivity(graph)
    display_connectivity(connectivity)
  
    print("\n\n── 2d. Stations de correspondance ──────────────────────")
    transfers = get_transfer_stations(graph)
    display_transfer_stations(transfers)

    print("\n\n── Récapitulatif ───────────────────────────────────────")
    print(f"  Stations totales          : {len(graph.all_stations)}")
    print(f"  Lignes                    : {len(graph.lines)}")
    print(f"  Stations de correspondance: {len(transfers)}")
    print(f"  Réseau connexe            : {'Oui' if connectivity['is_connected'] else 'Non ❌'}")
    print()


if __name__ == "__main__":
    main()
