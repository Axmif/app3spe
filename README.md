# QUIKWAY 🚆
# APP3 : Petite balade en métro et en tramway 🚋


## Membres du groupe et rôles
Sarah (sarahaguessy): Barreur  
Julie (Julie-2006) : Secrétaire    
Romain (Romainmiro) : Activateur  
Arthur (jurevej) : Gardien du temps   
Arthaud (Axmif Akiiko) : Intégrateur Git     
Rosalie (user1-r0) : Barreur  
## Description
Ce projet consiste à développer un calculateur d'itinéraires de transports en commun hors ligne, basé sur des graphes et l'algorithme de Dijkstra. Il permet de trouver différents trajets entre deux stations selon plusieurs critère (temps, correspondances, confort), tout en étant générique et adaptable à plusieurs villes via des fichiers JSON.
## Parties à coder
-> main.py
- charger_donnees.py  
- parcours_reseau.py
- meilleur_itineraire.py
- interface.py
- visualisation_graphe.py
- gestion_des_perturbations.py

  
## Choix techniques : structure de données, algorithmes utilisés...
### Structures de données utilisées :
- graphes non orientés
- listes d’adjacence
- dictionnaires Python (dict)
- listes (list)
- ensembles (set)
- files (deque)
- tuples
- graphes NetworkX
- interface graphique PyQt
- figures Matplotlib

### Algorithmes utilisés  :
- algorithme de Dijkstra
- parcours en largeur (BFS)
- parcours en profondeur (DFS)
- reconstruction de chemin optimal
- vérification de connexité
- gestion des correspondances
- suppression de sommets (fermeture de station)
- suppression d’arêtes (fermeture de tronçon)
- suppression de lignes entières
- comparaison de temps de trajet
- parcours récursif
- visualisation de graphe
- placement automatique de sommets (spring_layout, kamada_kawai_layout)

## Utilisation


Pour utiliser ce programme:
1. Installer les bibliothèques nécessaires :
   - PyQt5 ou PyQt6
   - matplotlib
   - networkx
2. Placer les fichiers JSON des réseaux (bordeaux.json, lyon.json, paris.json, lille.json) dans le même dossier que le projet.
3. Lancer le programme avec le fichier interface.py
4. Sélectionner une ville dans l’interface.
5. Choisir une station de départ et une station d’arrivée.
6. Cliquer sur Calculer l’itinéraire pour obtenir dans l'onglet "Résultats":
   - le meilleur trajet,
   - les lignes empruntées,
   - les correspondances,
   - le temps total de parcours
7. Utiliser les autres fonctionnalités disponibles :
   - BFS (moins d’arrêts),
   - DFS,
   - vérification de connexité,
   - affichage des correspondances,
   - visualisation du réseau,
   - gestion des perturbations : fermeture de station, fermeture de tronçon, fermeture de ligne entière.
8. Le graphe du réseau et l’itinéraire calculé sont affichés dans l’onglet Visualisation


## Structure du projet
Lors de la première séance nous avons pris connaissance du sujet et des différentes tâches à réaliser. Nous nous sommes également répartis le travail de la manière suivante : 
- Romain : 
- Julie : Charger des données + gestion des perturbations
- Sarah : Parcourir le réseau
- Rosalie : Trouver le meilleur itinéraire (en implémentant l'algorithme de Dijkstra) et ajouter des critères (le plus rapide, avec le moins de correspondances, le plus confortable)
- Arthaud : Interface PyQt + Généraliser à plusieurs villes
- Arthur : Visualisation du graphe
  
Nous avons chacun de notre côté commencé à travailler sur notre partie afin de bien comprendre les livrables attendus ainsi que les algorithmes à utiliser.

Lors des séances suivantes, nous avons chacun travaillé sur notre code, puis nous avons mis en commun.
Nous avons ensuite amélioré l'interface afin qu'elle soit la mieux contruite possible. Nous avons également rajouter des options comme la gestion des perturbations ou encore la visualisation du graphe.

Contrairement aux approches classiques qui proposent un seul itinérair optionnel, notre code intègre un système multi-critères permettant de générer plusieurs trajets adaptés aux préférences de l'utilisateur (temps, correspondances, confort). 

## Difficultés rencontrées 
Fonctionnement des différents codes ensemble


## Bonnes pratiques de programmation
Nous avons veillé à respecter les bonnes pratiques de programmation tout au long du projet, à savoir :
- la syntaxe 
- l’organisation du code 
- le découpage en fonctions
- l’indentation 
- les méthodes d’importation
- les règles de nommage
- la gestion des espaces
- la rédaction et la présentation des docstrings
- les affectations
- l’utilisation de boucles
- la structure des programmes
