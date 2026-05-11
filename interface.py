"""
interface.py — Interface graphique pour l'application de transport en commun
Utilise tkinter (bibliothèque standard Python, aucune installation requise).

Dépendances internes :
    - charger_donnees.py
    - meilleur_itineraire.py
    - parcourir_le_reseau.py
    - gestion_des_perturbations.py
    - bordeaux.json, lyon.json, lille.json, paris.json, mini_reseau.json

Lancement : python interface.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import copy

# ── Imports du projet ────────────────────────────────────────────────────────
from charger_donnees import charger_reseau
from meilleur_itineraire import dijkstra, reconstruire_chemin
from parcourir_le_reseau import bfs, dfs, verifier_connexite, get_transfer_stations
from gestion_des_perturbations import (
    fermer_station,
    fermer_troncon,
    fermer_ligne_entiere,
    comparer_temps_trajet,
)

# ── Palette de couleurs ───────────────────────────────────────────────────────
COULEURS = {
    "bg_sombre":   "#0f1923",
    "bg_panel":    "#1a2535",
    "bg_widget":   "#243040",
    "accent":      "#00c9a7",       # vert menthe vif
    "accent2":     "#f7941d",       # orange chaud
    "danger":      "#e05c5c",
    "texte":       "#e8edf3",
    "texte_gris":  "#7a8fa6",
    "bord":        "#2e4060",
    "ligne_A":     "#e63946",
    "ligne_B":     "#457b9d",
    "ligne_C":     "#2a9d8f",
    "ligne_D":     "#e9c46a",
    "ligne_E":     "#a8dadc",
}

FICHIERS_RESEAU = {
    "Bordeaux":   "bordeaux.json",
    "Lyon":       "lyon.json",
    "Lille":      "lille.json",
    "Paris":      "paris.json",
    "Mini réseau":"mini_reseau.json",
}


# ══════════════════════════════════════════════════════════════════════════════
#  Widgets utilitaires
# ══════════════════════════════════════════════════════════════════════════════

class ScrolledText(tk.Frame):
    """Zone de texte avec scrollbar verticale."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COULEURS["bg_panel"])
        self._text = tk.Text(
            self,
            wrap=tk.WORD,
            bg=COULEURS["bg_widget"],
            fg=COULEURS["texte"],
            insertbackground=COULEURS["accent"],
            relief=tk.FLAT,
            font=("Courier", 10),
            padx=10, pady=8,
            **kwargs,
        )
        sb = tk.Scrollbar(self, command=self._text.yview, bg=COULEURS["bg_panel"])
        self._text.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # tags de couleur pour le rendu riche
        self._text.tag_configure("titre",  foreground=COULEURS["accent"],  font=("Courier", 11, "bold"))
        self._text.tag_configure("ok",     foreground=COULEURS["accent"])
        self._text.tag_configure("warn",   foreground=COULEURS["accent2"])
        self._text.tag_configure("err",    foreground=COULEURS["danger"])
        self._text.tag_configure("gris",   foreground=COULEURS["texte_gris"])
        self._text.tag_configure("bold",   font=("Courier", 10, "bold"))

    def clear(self):
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)

    def append(self, texte, tag=None):
        self._text.configure(state=tk.NORMAL)
        if tag:
            self._text.insert(tk.END, texte, tag)
        else:
            self._text.insert(tk.END, texte)
        self._text.see(tk.END)

    def set_readonly(self):
        self._text.configure(state=tk.DISABLED)


def styled_label(parent, text, size=10, bold=False, color=None):
    weight = "bold" if bold else "normal"
    color  = color or COULEURS["texte"]
    return tk.Label(
        parent, text=text,
        bg=COULEURS["bg_panel"], fg=color,
        font=("Helvetica", size, weight),
    )


def styled_button(parent, text, command, color=None, width=18):
    bg = color or COULEURS["accent"]
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=COULEURS["bg_sombre"],
        activebackground=COULEURS["bg_widget"],
        activeforeground=COULEURS["texte"],
        relief=tk.FLAT, padx=10, pady=6,
        font=("Helvetica", 10, "bold"),
        cursor="hand2", width=width,
    )
    return btn


def styled_combo(parent, values, textvariable=None, width=30):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Dark.TCombobox",
        fieldbackground=COULEURS["bg_widget"],
        background=COULEURS["bg_widget"],
        foreground=COULEURS["texte"],
        arrowcolor=COULEURS["accent"],
        bordercolor=COULEURS["bord"],
        lightcolor=COULEURS["bord"],
        darkcolor=COULEURS["bord"],
    )
    combo = ttk.Combobox(
        parent, values=values,
        textvariable=textvariable,
        style="Dark.TCombobox",
        state="readonly", width=width,
        font=("Helvetica", 10),
    )
    return combo


# ══════════════════════════════════════════════════════════════════════════════
#  Fenêtre principale
# ══════════════════════════════════════════════════════════════════════════════

class AppTransport(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Réseau de Transport — Navigation")
        self.configure(bg=COULEURS["bg_sombre"])
        self.geometry("1150x720")
        self.minsize(900, 600)
        self.resizable(True, True)

        # État interne
        self.reseau         = None
        self.graphe_actif   = None   # peut être modifié par les perturbations
        self.graphe_original= None
        self.perturbations  = []     # liste de textes résumant les perturb. actives

        self._construire_interface()

    # ── Construction ──────────────────────────────────────────────────────────

    def _construire_interface(self):
        # Barre du haut
        self._barre_haut()

        # Corps principal : panneau gauche + zone résultats
        corps = tk.Frame(self, bg=COULEURS["bg_sombre"])
        corps.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Panneau gauche (controls)
        self.panneau_gauche = tk.Frame(corps, bg=COULEURS["bg_panel"],
                                       width=370, bd=0)
        self.panneau_gauche.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self.panneau_gauche.pack_propagate(False)

        # Zone résultats (droite)
        droite = tk.Frame(corps, bg=COULEURS["bg_sombre"])
        droite.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._zone_resultats(droite)
        self._panneau_reseau()
        self._panneau_itineraire()
        self._panneau_parcours()
        self._panneau_perturbations()

    def _barre_haut(self):
        barre = tk.Frame(self, bg=COULEURS["bg_panel"], height=60)
        barre.pack(fill=tk.X, padx=10, pady=(10, 6))

        tk.Label(
            barre, text="🚇  Réseau de Transport",
            bg=COULEURS["bg_panel"], fg=COULEURS["accent"],
            font=("Helvetica", 18, "bold"),
        ).pack(side=tk.LEFT, padx=18, pady=10)

        # Indicateur de réseau chargé
        self.lbl_reseau_actif = tk.Label(
            barre, text="Aucun réseau chargé",
            bg=COULEURS["bg_panel"], fg=COULEURS["texte_gris"],
            font=("Helvetica", 10),
        )
        self.lbl_reseau_actif.pack(side=tk.RIGHT, padx=18)

        # Indicateur perturbations
        self.lbl_perturb = tk.Label(
            barre, text="✔  Aucune perturbation",
            bg=COULEURS["bg_panel"], fg=COULEURS["accent"],
            font=("Helvetica", 10),
        )
        self.lbl_perturb.pack(side=tk.RIGHT, padx=12)

    def _zone_resultats(self, parent):
        tk.Label(
            parent, text="RÉSULTATS",
            bg=COULEURS["bg_sombre"], fg=COULEURS["texte_gris"],
            font=("Helvetica", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.zone_res = ScrolledText(parent, height=30)
        self.zone_res.pack(fill=tk.BOTH, expand=True)

        self._afficher_accueil()

    # ── Sections du panneau gauche ────────────────────────────────────────────

    def _section(self, titre):
        """Crée un cadre section avec titre dans le panneau gauche."""
        sep = tk.Frame(self.panneau_gauche, bg=COULEURS["bord"], height=1)
        sep.pack(fill=tk.X, padx=10, pady=(10, 0))
        tk.Label(
            self.panneau_gauche, text=titre.upper(),
            bg=COULEURS["bg_panel"], fg=COULEURS["accent"],
            font=("Helvetica", 9, "bold"),
        ).pack(anchor="w", padx=14, pady=(6, 2))
        frame = tk.Frame(self.panneau_gauche, bg=COULEURS["bg_panel"])
        frame.pack(fill=tk.X, padx=10, pady=(0, 4))
        return frame

    def _panneau_reseau(self):
        f = self._section("1 · Chargement du réseau")

        styled_label(f, "Choisir une ville :").pack(anchor="w", pady=(4, 2))
        self.var_ville = tk.StringVar(value="Bordeaux")
        styled_combo(f, list(FICHIERS_RESEAU.keys()),
                     textvariable=self.var_ville, width=28).pack(anchor="w")

        styled_button(f, "⬇  Charger le réseau",
                      self._charger_reseau, width=24).pack(pady=6, anchor="w")

    def _panneau_itineraire(self):
        f = self._section("2 · Meilleur itinéraire (Dijkstra)")

        styled_label(f, "Départ :").pack(anchor="w", pady=(4, 1))
        self.var_depart = tk.StringVar()
        self.combo_depart = styled_combo(f, [], textvariable=self.var_depart, width=28)
        self.combo_depart.pack(anchor="w")

        styled_label(f, "Arrivée :").pack(anchor="w", pady=(6, 1))
        self.var_arrivee = tk.StringVar()
        self.combo_arrivee = styled_combo(f, [], textvariable=self.var_arrivee, width=28)
        self.combo_arrivee.pack(anchor="w")

        styled_button(f, "🔍  Calculer l'itinéraire",
                      self._calculer_itineraire, width=24).pack(pady=6, anchor="w")

    def _panneau_parcours(self):
        f = self._section("3 · Parcours du réseau")

        styled_label(f, "Station de départ :").pack(anchor="w", pady=(4, 1))
        self.var_bfs_dep = tk.StringVar()
        self.combo_bfs_dep = styled_combo(f, [], textvariable=self.var_bfs_dep, width=28)
        self.combo_bfs_dep.pack(anchor="w")

        styled_label(f, "Station d'arrivée :").pack(anchor="w", pady=(4, 1))
        self.var_bfs_arr = tk.StringVar()
        self.combo_bfs_arr = styled_combo(f, [], textvariable=self.var_bfs_arr, width=28)
        self.combo_bfs_arr.pack(anchor="w")

        ligne_btns = tk.Frame(f, bg=COULEURS["bg_panel"])
        ligne_btns.pack(anchor="w", pady=4)
        styled_button(ligne_btns, "BFS", self._faire_bfs, width=9).pack(side=tk.LEFT, padx=(0, 4))
        styled_button(ligne_btns, "DFS", self._faire_dfs, width=9,
                      color=COULEURS["accent2"]).pack(side=tk.LEFT)

        ligne_info = tk.Frame(f, bg=COULEURS["bg_panel"])
        ligne_info.pack(anchor="w", pady=2)
        styled_button(ligne_info, "📡  Connexité",   self._verifier_connexite, width=12).pack(side=tk.LEFT, padx=(0, 4))
        styled_button(ligne_info, "🔁  Correspondances", self._afficher_correspondances,
                      width=16, color="#6c8ebf").pack(side=tk.LEFT)

    def _panneau_perturbations(self):
        f = self._section("4 · Perturbations")

        styled_label(f, "Station à fermer :").pack(anchor="w", pady=(4, 1))
        self.var_fermer_station = tk.StringVar()
        self.combo_fermer_station = styled_combo(f, [], textvariable=self.var_fermer_station, width=28)
        self.combo_fermer_station.pack(anchor="w")
        styled_button(f, "🚫  Fermer station",
                      self._fermer_station, color=COULEURS["danger"], width=24).pack(pady=3, anchor="w")

        styled_label(f, "Ligne entière à fermer :").pack(anchor="w", pady=(4, 1))
        self.var_fermer_ligne = tk.StringVar()
        self.combo_fermer_ligne = styled_combo(f, [], textvariable=self.var_fermer_ligne, width=28)
        self.combo_fermer_ligne.pack(anchor="w")
        styled_button(f, "🚫  Fermer ligne",
                      self._fermer_ligne, color=COULEURS["danger"], width=24).pack(pady=3, anchor="w")

        styled_button(f, "↩  Rétablir le réseau",
                      self._retablir, color="#4a6fa5", width=24).pack(pady=(6, 2), anchor="w")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _afficher_accueil(self):
        self.zone_res.clear()
        self.zone_res.append("╔══════════════════════════════════════════════╗\n", "titre")
        self.zone_res.append("║   Bienvenue dans l'app Transport en Commun   ║\n", "titre")
        self.zone_res.append("╚══════════════════════════════════════════════╝\n\n", "titre")
        self.zone_res.append("→  Chargez d'abord un réseau (section 1).\n", "gris")
        self.zone_res.append("→  Puis calculez un itinéraire ou parcourez le réseau.\n", "gris")
        self.zone_res.set_readonly()

    def _charger_reseau(self):
        ville  = self.var_ville.get()
        fichier = FICHIERS_RESEAU[ville]
        try:
            self.reseau          = charger_reseau(fichier)
            self.graphe_original = self.reseau["graphe"]
            self.graphe_actif    = copy.deepcopy(self.graphe_original)
            self.perturbations   = []
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Fichier introuvable : {fichier}\n"
                                           "Assurez-vous que le JSON est dans le même dossier.")
            return
        except Exception as e:
            messagebox.showerror("Erreur de chargement", str(e))
            return

        stations = sorted(self.graphe_original.keys())
        lignes   = sorted(self.reseau["lignes"].keys())

        for combo in (self.combo_depart, self.combo_arrivee,
                      self.combo_bfs_dep, self.combo_bfs_arr,
                      self.combo_fermer_station):
            combo["values"] = stations
            combo.set(stations[0] if stations else "")

        self.combo_fermer_ligne["values"] = lignes
        self.combo_fermer_ligne.set(lignes[0] if lignes else "")

        self.lbl_reseau_actif.configure(
            text=f"Réseau : {self.reseau['nom']}  ({len(stations)} stations)",
            fg=COULEURS["accent"],
        )
        self._mettre_a_jour_perturb()

        # Affichage résumé
        self.zone_res.clear()
        self.zone_res.append(f"Réseau chargé : {self.reseau['nom']}\n\n", "titre")
        self.zone_res.append(f"  Stations      : {len(stations)}\n", "ok")
        self.zone_res.append(f"  Lignes        : {len(lignes)} — {', '.join(lignes)}\n", "ok")
        corresp = self.reseau.get("correspondances", [])
        self.zone_res.append(f"  Correspondances: {len(corresp)}\n", "ok")
        self.zone_res.append(f"  Temps moyen/arrêt : {self.reseau['temps_moyen']} s\n\n", "gris")
        self.zone_res.append("Tout est prêt. Bonne navigation ! 🚇\n", "bold")
        self.zone_res.set_readonly()

    def _verifier_reseau(self):
        if self.graphe_actif is None:
            messagebox.showwarning("Réseau non chargé", "Chargez d'abord un réseau.")
            return False
        return True

    def _calculer_itineraire(self):
        if not self._verifier_reseau():
            return
        depart  = self.var_depart.get()
        arrivee = self.var_arrivee.get()
        if not depart or not arrivee:
            messagebox.showwarning("Champs manquants", "Sélectionnez un départ et une arrivée.")
            return
        if depart == arrivee:
            messagebox.showinfo("Info", "Départ et arrivée sont identiques.")
            return

        try:
            distances, parents = dijkstra(self.graphe_actif, depart)
            chemin = reconstruire_chemin(parents, depart, arrivee)
        except Exception as e:
            messagebox.showerror("Erreur Dijkstra", str(e))
            return

        self.zone_res.clear()
        self.zone_res.append("🚇  ITINÉRAIRE OPTIMAL  (Dijkstra)\n", "titre")
        self.zone_res.append(f"    {depart}  →  {arrivee}\n\n", "bold")

        if not chemin:
            self.zone_res.append("  ✗  Aucun itinéraire possible.\n", "err")
            if self.perturbations:
                self.zone_res.append("  (Des perturbations sont actives — essayez de les lever)\n", "warn")
            self.zone_res.set_readonly()
            return

        temps_total = distances[arrivee]
        ligne_actuelle = None

        for i in range(len(chemin) - 1):
            station  = chemin[i]
            suivante = chemin[i + 1]
            ligne    = parents[suivante][1] if parents[suivante] else "?"

            if ligne_actuelle is None:
                self.zone_res.append(f"  ▶  Prendre la ligne ", "gris")
                self.zone_res.append(f"{ligne}", "bold")
                self.zone_res.append(f" à {station}\n")
            elif ligne != ligne_actuelle:
                self.zone_res.append(f"\n  🔁  Correspondance à ", "warn")
                self.zone_res.append(f"{station}", "bold")
                self.zone_res.append(f"  ({ligne_actuelle} → {ligne})\n", "warn")
            else:
                self.zone_res.append(f"      ↓  {station}\n", "gris")

            ligne_actuelle = ligne

        self.zone_res.append(f"\n  🏁  Arrivée : {chemin[-1]}\n", "ok")
        minutes = temps_total // 60
        secondes = temps_total % 60
        self.zone_res.append(f"\n  ⏱  Temps total : {temps_total} s  ({minutes} min {secondes} s)\n", "bold")
        self.zone_res.append(f"  📍  Stations traversées : {len(chemin)}\n", "gris")

        if self.perturbations:
            self.zone_res.append("\n  ⚠  Perturbations actives :\n", "warn")
            for p in self.perturbations:
                self.zone_res.append(f"      • {p}\n", "warn")

        self.zone_res.set_readonly()

    def _faire_bfs(self):
        if not self._verifier_reseau():
            return
        depart  = self.var_bfs_dep.get()
        arrivee = self.var_bfs_arr.get()
        if not depart or not arrivee:
            messagebox.showwarning("Champs manquants", "Sélectionnez un départ et une arrivée.")
            return
        try:
            res = bfs(self.graphe_actif, depart, arrivee)
        except ValueError as e:
            messagebox.showerror("Erreur BFS", str(e))
            return

        self.zone_res.clear()
        self.zone_res.append("🔵  BFS — Chemin avec le MOINS D'ARRÊTS\n", "titre")
        self.zone_res.append(f"    {depart}  →  {arrivee}\n\n", "bold")

        if not res["found"]:
            self.zone_res.append("  ✗  Aucun chemin trouvé.\n", "err")
        else:
            self.zone_res.append(f"  Arrêts intermédiaires : {res['stops']}\n", "ok")
            self.zone_res.append(f"  Stations totales      : {len(res['path'])}\n\n", "ok")
            for i, s in enumerate(res["path"]):
                if s == depart:
                    self.zone_res.append(f"  ▶ DÉPART : {s}\n", "bold")
                elif s == arrivee:
                    self.zone_res.append(f"  🏁 ARRIVÉE : {s}\n", "ok")
                else:
                    self.zone_res.append(f"      {i}. {s}\n", "gris")

        self.zone_res.append(f"\n  Stations visitées par BFS : {len(res['visited'])}\n", "gris")
        self.zone_res.set_readonly()

    def _faire_dfs(self):
        if not self._verifier_reseau():
            return
        depart  = self.var_bfs_dep.get()
        arrivee = self.var_bfs_arr.get()
        if not depart:
            messagebox.showwarning("Champs manquants", "Sélectionnez au moins un départ.")
            return
        try:
            res = dfs(self.graphe_actif, depart, arrivee if arrivee else None)
        except ValueError as e:
            messagebox.showerror("Erreur DFS", str(e))
            return

        self.zone_res.clear()
        self.zone_res.append("🟠  DFS — Exploration en profondeur\n", "titre")
        if arrivee:
            self.zone_res.append(f"    {depart}  →  {arrivee}\n\n", "bold")
        else:
            self.zone_res.append(f"    Depuis : {depart} (exploration complète)\n\n", "bold")

        if arrivee and res["found"]:
            self.zone_res.append(f"  Chemin trouvé ({len(res['path'])} stations) :\n", "ok")
            for s in res["path"]:
                marker = "▶" if s == depart else ("🏁" if s == arrivee else " ·")
                self.zone_res.append(f"  {marker}  {s}\n", "gris" if marker == " ·" else "bold")
        elif arrivee:
            self.zone_res.append("  ✗  Aucun chemin trouvé.\n", "err")

        self.zone_res.append(f"\n  Ordre de visite DFS ({len(res['visited'])} stations) :\n", "gris")
        preview = res["visited"][:15]
        self.zone_res.append("  " + " → ".join(preview))
        if len(res["visited"]) > 15:
            self.zone_res.append(" → …\n", "gris")
        else:
            self.zone_res.append("\n")
        self.zone_res.set_readonly()

    def _verifier_connexite(self):
        if not self._verifier_reseau():
            return
        res = verifier_connexite(self.graphe_actif)

        self.zone_res.clear()
        self.zone_res.append("📡  CONNEXITÉ DU RÉSEAU\n\n", "titre")
        self.zone_res.append(f"  Stations totales    : {res['total_count']}\n", "bold")
        self.zone_res.append(f"  Stations accessibles: {res['reachable_count']}\n", "bold")

        if res["is_connected"]:
            self.zone_res.append("\n  ✔  Le réseau est CONNEXE.\n", "ok")
            self.zone_res.append("     Toutes les stations sont mutuellement accessibles.\n", "gris")
        else:
            self.zone_res.append("\n  ✗  Le réseau N'EST PAS connexe !\n", "err")
            self.zone_res.append(f"     {len(res['unreachable'])} station(s) inaccessible(s) :\n", "warn")
            for s in res["unreachable"]:
                self.zone_res.append(f"     • {s}\n", "warn")
        self.zone_res.set_readonly()

    def _afficher_correspondances(self):
        if not self._verifier_reseau():
            return
        transfers = get_transfer_stations(self.reseau)

        self.zone_res.clear()
        self.zone_res.append(f"🔁  STATIONS DE CORRESPONDANCE  ({len(transfers)})\n\n", "titre")

        if not transfers:
            self.zone_res.append("  Aucune correspondance dans ce réseau.\n", "gris")
        else:
            for station, lignes in transfers:
                self.zone_res.append(f"  ◉  {station:<35}", "bold")
                self.zone_res.append(f"  [{', '.join(sorted(lignes))}]\n", "ok")
        self.zone_res.set_readonly()

    def _fermer_station(self):
        if not self._verifier_reseau():
            return
        station = self.var_fermer_station.get()
        if not station:
            return
        if station not in self.graphe_actif:
            messagebox.showwarning("Introuvable", f"La station « {station} » n'est pas dans le graphe actif.")
            return

        self.graphe_actif = fermer_station(self.graphe_actif, station)
        self.perturbations.append(f"Station fermée : {station}")
        self._mettre_a_jour_perturb()

        # Mettre à jour les combos (retirer la station fermée)
        stations_restantes = sorted(self.graphe_actif.keys())
        for combo in (self.combo_depart, self.combo_arrivee,
                      self.combo_bfs_dep, self.combo_bfs_arr,
                      self.combo_fermer_station):
            combo["values"] = stations_restantes

        self.zone_res.clear()
        self.zone_res.append(f"🚫  Station fermée : {station}\n\n", "err")
        self.zone_res.append("  Le graphe actif a été mis à jour.\n", "warn")
        self.zone_res.append("  Les calculs suivants excluront cette station.\n", "gris")
        self.zone_res.set_readonly()

    def _fermer_ligne(self):
        if not self._verifier_reseau():
            return
        ligne = self.var_fermer_ligne.get()
        if not ligne:
            return
        self.graphe_actif = fermer_ligne_entiere(self.graphe_actif, ligne)
        self.perturbations.append(f"Ligne fermée : {ligne}")
        self._mettre_a_jour_perturb()

        self.zone_res.clear()
        self.zone_res.append(f"🚫  Ligne fermée : {ligne}\n\n", "err")
        self.zone_res.append("  Tous les trajets sur cette ligne sont suspendus.\n", "warn")
        self.zone_res.append("  Relancez un calcul d'itinéraire pour voir l'impact.\n", "gris")
        self.zone_res.set_readonly()

    def _retablir(self):
        if self.graphe_original is None:
            return
        self.graphe_actif  = copy.deepcopy(self.graphe_original)
        self.perturbations = []
        self._mettre_a_jour_perturb()

        # Restaurer les listes de stations
        stations = sorted(self.graphe_original.keys())
        for combo in (self.combo_depart, self.combo_arrivee,
                      self.combo_bfs_dep, self.combo_bfs_arr,
                      self.combo_fermer_station):
            combo["values"] = stations

        self.zone_res.clear()
        self.zone_res.append("✔  Réseau rétabli dans son état initial.\n\n", "ok")
        self.zone_res.append("  Toutes les perturbations ont été levées.\n", "gris")
        self.zone_res.set_readonly()

    def _mettre_a_jour_perturb(self):
        if self.perturbations:
            n = len(self.perturbations)
            self.lbl_perturb.configure(
                text=f"⚠  {n} perturbation{'s' if n > 1 else ''} active{'s' if n > 1 else ''}",
                fg=COULEURS["accent2"],
            )
        else:
            self.lbl_perturb.configure(
                text="✔  Aucune perturbation",
                fg=COULEURS["accent"],
            )


# ══════════════════════════════════════════════════════════════════════════════
#  Point d'entrée
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = AppTransport()
    app.mainloop()
