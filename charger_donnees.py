import json

def charger_json(fichier):
    """
    Charge un fichier JSON et retourne un dictionnaire Python.

    Paramètres
    ---------
    fichier: un fichier json

    Retourne
    --------
    data: Contenu du fichier JSON sous forme de dictionnaire Python.
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

    Paramètres
    ----------
    data: dictionnaire contenant les informations du réseau de tansport d'une ville

    Retourne
    --------
    graphe: dictionnaire python. Graphe représentant le réseau sous forme de liste d'adjacence.
        Chaque station est associée à une liste de connexions vers
        ses stations voisines, le temps et la ligne associée
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
    Charge entièrement un réseau de transport depuis un fichier json.

    Paramètres
    ---------
    fichier: un ficher json

    Retourne
    --------
    reseau : 
        Dictionnaire contenant :
        - le nom du réseau,
        - le graphe des stations,
        - les lignes du réseau,
        - les correspondances,
        - le temps moyen entre stations.
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
