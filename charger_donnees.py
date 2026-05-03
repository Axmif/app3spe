import json
import networkx as nx
import matplotlib.pyplot as plt

def charger_json(fichier):
    with open(fichier) as f:
        # transformation du json en dictionnaire python
        data = json.load(f)
    return data

def construire_graphe(fichier):
    """
    Construit un graphe représentant le réseau de transport d'une ville,
    sous forme d'un graphe non orienté
    """
    data = charger_json(fichier)      # data est un dictionnaire qui contient tout le réseau
    G = nx.Graph()
    temps = data["temps_moyen"]       # récupération du temps moyen entre 2 stations consécutives

    for ligne, infos in data["lignes"].items():          # infos contient nom + couleur + stations
        # on récupère la liste des stations de la ligne
        stations = infos["stations"]

        for i in range(len(stations) - 1):

            s1 = stations[i]
            s2 = stations[i + 1]

            G.add_edge(
                s1,
                s2,
                weight=temps,
                ligne=ligne
            )
        
        # on ajoute les correspondances
        for c in data["correspondances"]:
            station = c["station"]

            # si la station n'est pas trouvée, on passe à la suivante
            if station not in G:
                continue

            G.nodes[station]["correspondance"] = True
            G.nodes[station]["correspondance_time"] = c["temps"]
            G.nodes[station]["lignes"] = c["lignes"]

    return G


# fonction pour tester pour l'instant (c'est probablement la partie 6)
def montrer_graphe(fichier):
    G = construire_graphe(fichier)
    positions = nx.spring_layout(G, seed=42)
    nx.draw(G, positions, with_labels=True,
            node_color='lightblue', node_size=800, font_weight='bold')
    # Etiquettes de temps
    temps = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, positions, edge_labels=temps)
    plt.show()