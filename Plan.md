# Plan du Projet

## Reformulation du problème
Le but du projet est de fournir un algorithme capable de donner le meilleur itinéraire
(en termes de temps de parcours) pour relier les stations des réseaux de transport des
villes de Paris, Bordeaux, Lille et Lyon.


## Entrées / Sorties
Entrées:
- fichier json

Sorties:
- graphes
- parcours BFS (parcours en largeur) du graphe
- parcours DFS (parcours en profondeur) du graphe
- affichage de l'itinéraire:
  o Station de montée et ligne
  o Stations traversées
  o Correspondances eSectuées
  o Station de descente et ligne
  o Temps total de parcours
- interface utilisateur
- Visualisation du graphe
## Liste des tâches
### Charger des données : (JULIE)
- Lire les données d'un réseau à partir d'un fichier JSON contenant: les Lignes de métro/bus, la liste des connexions entre stations voisines (station départ, station arrivée, temps en secondes, ligne), et les Correspondances : liste des stations de correspondance (station, lignes desservies, temps de correspondance)
- Construire un graphe pondéré à partir de ces données
- Choisir la structure de données la plus adaptée : matrice d'adjacence ou
liste d'adjacence

### Parcourir le réseau (SARAH)
- Implémenter les algorithmes de parcours de graphe pour trouver le chemin avec le moins
d'arrêts : BFS (parcours en largeur) et DFS (parcours en profondeur)
- Vérifier que toutes les stations sont accessibles depuis n'importe quelle
autre station
- Identifier les stations de correspondance dans le réseau

### Trouver le meilleur itinéraire (ROSALIE)
- Implémenter l'algorithme de Dijkstra pour calculer le plus court chemin
en temps de parcours
- Intégrer le temps de correspondance (120 secondes) dans le calcul
-Reconstruire et afficher l'itinéraire de manière lisible :
o Station de montée et ligne
o Stations traversées
o Correspondances eSectuées
o Station de descente et ligne
o Temps total de parcours

### Généraliser à plusieurs villes
- Proposer à l'utilisateur de choisir une ville parmi celles disponibles
- Charger automatiquement les données du réseau correspondant
- Permettre de choisir une station de départ et une station d'arrivée
- Prouver la généricité du code : l'ajout d'une nouvelle ville ne nécessite aucune modification du code, seulement l'ajout d'un fichier JSON

### Interface utilisateur (console)
- Créer un menu interactif en console permettant de :
o Sélectionner la ville
o Saisir les stations de départ et d'arrivée (avec gestion des erreurs de saisie)
o Afficher l'itinéraire de manière claire et formatée
o Relancer un calcul ou quitter
Créer une interface graphique avec PyQt5

### Optionnel : Visualisation du graphe (ARTHUR)
- Intégrer une visualisation du réseau à l'aide de la bibliothèque networkx :
- Afficher le graphe du réseau avec les stations et les connexions
- Mettre en évidence l'itinéraire calculé sur le graphe
- Différencier les lignes par couleur

### Optionnel : Gestion des perturbations
- Permettre à l'utilisateur de fermer une station (travaux, incident) : le calculateur doit recalculer un itinéraire alternatif en excluant cette station du graphe
- Permettre de fermer un tronçon entre deux stations consécutives (ligne interrompue entre deux arrêts)
- Permettre de fermer une ligne entière (grève, maintenance prolongée)
- Afficher un message d'avertissement lorsque l'itinéraire initialement demandée est impacté par une perturbation
- Comparer le temps de trajet normal vs le temps avec perturbation pour quantifier l'impact sur le voyageur

  
## Cas limites à gérer
2 chemins ont la même longueur
