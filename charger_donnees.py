import json
import networkx as nx
import matplotlib.pyplot as plt

def charger_json(fichier):
    """
    Charge un fichier JSON et retourne un dictionnaire Python.
    """
    with open(fichier, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def construire_graphe(data):
    """
    Construit le graphe sous forme de liste d'adjacence.

    Format :
    {
        station: [
            {
                "voisin": str,
                "temps": int,
                "ligne": str
            }
        ]
    }
    """

    graphe = {}

    temps_moyen = data["temps_moyen"]

    # Parcours des lignes
    for ligne, infos in data["lignes"].items():

        stations = infos["stations"]

        # Création des sommets
        for station in stations:

            if station not in graphe:
                graphe[station] = []

        # Création des connexions
        for i in range(len(stations) - 1):

            s1 = stations[i]
            s2 = stations[i + 1]

            arete = {
                "voisin": s2,
                "temps": temps_moyen,
                "ligne": ligne
            }

            arete_retour = {
                "voisin": s1,
                "temps": temps_moyen,
                "ligne": ligne
            }

            # Graphe non orienté
            graphe[s1].append(arete)
            graphe[s2].append(arete_retour)

    return graphe


def charger_reseau(fichier):
    """
    Charge entièrement un réseau.
    """

    data = charger_json(fichier)

    reseau = {
        "nom": data["nom"],
        "graphe": construire_graphe(data),
        "lignes": data["lignes"],
        "correspondances": data["correspondances"],
        "temps_moyen": data["temps_moyen"]
    }

    return reseau

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

if __name__ == "__main__":

    reseau = charger_reseau("bordeaux.json")

    graphe = reseau["graphe"]

    print("Nom du réseau :", reseau["nom"])
    print("Nombre de stations :", len(graphe))

    # afficher quelques stations
    for i, (station, voisins) in enumerate(graphe.items()):
        print("\nStation :", station)

        for v in voisins:
            print("  ->", v)

        if i == 3:  # on limite l'affichage
            break