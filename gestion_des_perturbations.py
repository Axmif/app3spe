"""
Permettre à l'utilisateur de fermer une station (travaux, incident) : le
calculateur doit recalculer un itinéraire alternatif en excluant cette station
du graphe
• Permettre de fermer un tronçon entre deux stations consécutives (ligne
interrompue entre deux arrêts)
• Permettre de fermer une ligne entière (grève, maintenance prolongée)
• Afficher un message d'avertissement lorsque l'itinéraire initialement
demandée est impacté par une perturbation
• Comparer le temps de trajet normal vs le temps avec perturbation pour
quantifier l'impact sur le voyageur
"""

import copy
from meilleur_itineraire import dijkstra


def fermer_station(graphe, station):
    """
    Ferme une station du réseau. 
    Recalcule un itinéraire alternatif en excluant cette station du graphe.

    Paramètres
    ----------
    graphe: graphe sous forme de dictionnaire python au format :
    {
        station: [
            {
                "voisin": str,
                "temps": int,
                "ligne": str
            }
        ]
    }
    station: nom de la station à supprimer du graphe (str)

    Retourne
    --------
    graphe_modifie: le graphe modifié sous forme de dictionnaire python
    """
    graphe_modifie = copy.deepcopy(graphe)

    # 1. supprimer la station
    if station in graphe_modifie:
        del graphe_modifie[station]

    # 2. supprimer les arêtes reliées à cette station
    for s in graphe_modifie:
        graphe_modifie[s] = [
            arete for arete in graphe_modifie[s]
            if arete["voisin"] != station
        ]

    return graphe_modifie


def fermer_troncon(graphe, station1, station2):
    """
    Permet de fermer un tronçon entre deux stations consécutives (ligne
    interrompue entre deux arrêts)

    Paramètres
    ----------
    graphe: graphe sous forme de dictionnaire python au format :
    {
        station: [
            {
                "voisin": str,
                "temps": int,
                "ligne": str
            }
        ]
    }
    station1: nom de la première station (str)
    station2: nom de la deuxième station (str)

    Retourne
    --------
    graphe_modifie: le graphe modifié sous forme de dictionnaire python
    """
    graphe_modifie = copy.deepcopy(graphe)

    graphe_modifie[station1] = [
        arete for arete in graphe_modifie[station1]
        if arete["voisin"] != station2
    ]

    graphe_modifie[station2] = [
        arete for arete in graphe_modifie[station2]
        if arete["voisin"] != station1
    ]

    return graphe_modifie

def fermer_ligne_entiere(graphe, ligne):
    """
    Permet de fermer une ligne entière.

    Paramètres
    ----------
    Paramètres
    ----------
    graphe: graphe sous forme de dictionnaire python au format :
    {
        station: [
            {
                "voisin": str,
                "temps": int,
                "ligne": str
            }
        ]
    }
    ligne: nom de la ligne à supprimer du graphe (str)

    Retourne
    --------
    graphe_modifie: le graphe modifié sous forme de dictionnaire python
    """
    graphe_modifie = copy.deepcopy(graphe)
    
    if ligne in graphe_modifie:
        del graphe_modifie[ligne]
    
    for station in graphe_modifie:
        graphe_modifie[station] = [
            arete for arete in graphe_modifie[station]
            if arete["ligne"] != ligne
            ]
    return graphe_modifie

def comparer_temps_trajet(graphe, depart, arrivee, graphe_perturbe):
    """
    Comparer le temps de trajet normal vs le temps avec perturbation pour
    quantifier l'impact sur le voyageur
    """
    dist_normale, _ = dijkstra(graphe, depart, arrivee)
    dist_perturbe, _ = dijkstra(graphe_perturbe, depart, arrivee)

    trajet_normal = dist_normale[arrivee]
    trajet_perturbe = dist_perturbe[arrivee]

    if trajet_normal != trajet_perturbe:
        print("⚠️ Le trajet est impacté par une perturbation.")

    return (
        f"Temps de trajet normal : {trajet_normal} s\n"
        f"Temps avec perturbation : {trajet_perturbe} s\n"
        f"Impact : +{trajet_perturbe - trajet_normal} s"
    )
