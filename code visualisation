import matplotlib.patches as mpatches

# ── Couleurs par ligne ────────────────────────────────────────────
PALETTE      = ["#1565C0","#C62828","#AD1457","#6A1B9A","#E65100","#00838F","#F9A825","#4E342E"]
HUB_COLOR    = "#2E7D32"   # vert  = correspondance
SIMPLE_COLOR = "#1A237E"   # bleu  = station simple



def graphe_vers_networkx(graphe, data):
    """Convertit la liste d'adjacence en graphe NetworkX pour la visualisation."""
    G    = nx.Graph()
    hubs = {c["station"] for c in data.get("correspondances", [])}

    for station, voisins in graphe.items():
        if station not in G:
            G.add_node(station, hub=station in hubs)
        for arete in voisins:
            v, t, l = arete["voisin"], arete["temps"], arete["ligne"]
            if G.has_edge(station, v):
                G.edges[station, v]["lignes"].add(l)
            else:
                G.add_edge(station, v, weight=t, lignes={l})

    return G


def visualiser_graphe(G, data, itineraire=None):
    lignes   = data["lignes"]
    couleurs = {lid: PALETTE[i % len(PALETTE)] for i, lid in enumerate(sorted(lignes))}
    n        = G.number_of_nodes()

    # Taille et polices selon densité
    fig_w  = 10 if n <= 20 else (16 if n <= 60 else 22)
    fs_lbl = 9  if n <= 20 else (7  if n <= 60 else 5)
    fs_wt  = 8  if n <= 20 else (6  if n <= 60 else 0)

    fig, ax = plt.subplots(figsize=(fig_w, fig_w * 0.75))
    ax.set_facecolor("#F5F0E8")
    fig.patch.set_facecolor("#F5F0E8")

    pos = (nx.kamada_kawai_layout(G) if n <= 30
           else nx.spring_layout(G, seed=42, k=2.5/n**0.5, iterations=150))

    # Arêtes colorées par ligne
    for lid, col in couleurs.items():
        aretes = [(u, v) for u, v, d in G.edges(data=True) if lid in d.get("lignes", {})]
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aretes, edge_color=col, width=2.5, alpha=0.8)

    # Itinéraire en surbrillance
    if itineraire and len(itineraire) >= 2:
        itin_edges = [(itineraire[i], itineraire[i+1])
                      for i in range(len(itineraire)-1)
                      if G.has_edge(itineraire[i], itineraire[i+1])]
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=itin_edges, edge_color="white",   width=10, alpha=0.5)
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=itin_edges, edge_color="#FFD600", width=6, alpha=1.0)
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[itineraire[0]], node_color="#00C853", node_size=900, edgecolors="white", linewidths=2)
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[itineraire[-1]], node_color="#D50000", node_size=900, edgecolors="white", linewidths=2)

    # Nœuds
    colors = [HUB_COLOR if G.nodes[nd].get("hub") else SIMPLE_COLOR for nd in G.nodes]
    sizes  = [700       if G.nodes[nd].get("hub") else 350           for nd in G.nodes]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors,
                           node_size=sizes, edgecolors="white", linewidths=1.5)
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=fs_lbl, font_color="white", font_weight="bold")

    # Poids sur les arêtes
    if fs_wt > 0:
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax,
            edge_labels={(u,v): d["weight"] for u,v,d in G.edges(data=True)},
            font_size=fs_wt, font_color="#BF360C", font_weight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="#F5F0E8", ec="none", alpha=0.8))

    # Légende
    patches = [mpatches.Patch(color=HUB_COLOR,    label="Correspondance"),
               mpatches.Patch(color=SIMPLE_COLOR, label="Station")]
    if itineraire:
        patches += [mpatches.Patch(color="#FFD600", label="Itinéraire"),
                    mpatches.Patch(color="#00C853", label=f"Départ : {itineraire[0]}"),
                    mpatches.Patch(color="#D50000", label=f"Arrivée : {itineraire[-1]}")]
    for lid, col in sorted(couleurs.items()):
        patches.append(mpatches.Patch(color=col, label=lignes[lid].get("nom", f"Ligne {lid}")))
    ax.legend(handles=patches, loc="upper left", fontsize=8,
              title="Légende", framealpha=0.9, edgecolor="#ccc")

    nom = data.get("nom", "Réseau")
    ax.set_title(f"Réseau — {nom}  ({n} stations · {G.number_of_edges()} connexions)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(f"graphe_{nom.lower().replace(' ','_')}.png", dpi=150, bbox_inches="tight")
    plt.show()


# ── Point d'entrée ────────────────────────────────────────────────
if __name__ == "__main__":
    fichier = sys.argv[1] if len(sys.argv) > 1 else "bordeaux.json"
    data    = charger_reseau(fichier)
    graphe  = construire_graphe(data)              # liste d'adjacence (ton format)
    G       = graphe_vers_networkx(graphe, data)   # conversion pour visualisation
    visualiser_graphe(G, data)

    # Itinéraire : décommenter pour tester
    # visualiser_graphe(G, data, itineraire=["Quinconces", "Victoire", "Gare Saint-Jean"])²
