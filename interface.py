"""
interface.py — Interface graphique (PyQt5 / PyQt6) + visualisation Matplotlib.

Dépendances : PyQt6 (recommandé) ou PyQt5, matplotlib, networkx
Lancement : python interface.py
"""

from __future__ import annotations

import copy
import math
import sys

# ── PyQt : PyQt6 prioritaire, repli PyQt5 ─────────────────────────────────────
try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QScrollArea,
        QSplitter,
        QTabWidget,
        QVBoxLayout,
        QWidget,
        QListWidget,
    )

    _QT = 6
except ImportError:  # pragma: no cover
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QScrollArea,
        QSplitter,
        QTabWidget,
        QVBoxLayout,
        QWidget,
        QListWidget,
    )

    _QT = 5

# Constantes Qt compatibles PyQt5 / PyQt6
if _QT == 6:
    _QT_HORIZ = Qt.Orientation.Horizontal
    _QT_SCROLL_OFF = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    _QT_ALIGN_TOP = Qt.AlignmentFlag.AlignTop
    _QT_FONT_BOLD = QFont.Weight.Bold
else:
    _QT_HORIZ = Qt.Horizontal
    _QT_SCROLL_OFF = Qt.ScrollBarAlwaysOff
    _QT_ALIGN_TOP = Qt.AlignTop
    _QT_FONT_BOLD = QFont.Bold

if _QT == 6:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
else:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

import matplotlib.pyplot as plt

from charger_donnees import charger_reseau
from meilleur_itineraire import dijkstra, reconstruire_chemin
from parcourir_le_reseau import bfs, dfs, verifier_connexite, get_transfer_stations
from gestion_des_perturbations import (
    fermer_station,
    fermer_troncon,
    fermer_ligne_entiere,
    comparer_temps_trajet,
)
import visualisation as viz

# ── Thème sombre (proche de l’ancienne interface) ────────────────────────────
COLORS = {
    "bg_dark": "#0f1923",
    "bg_panel": "#1a2535",
    "accent": "#00c9a7",
    "accent2": "#f7941d",
    "danger": "#e05c5c",
    "text": "#e8edf3",
    "muted": "#7a8fa6",
}

FICHIERS_RESEAU = {
    "Bordeaux": "bordeaux.json",
    "Lyon": "lyon.json",
    "Lille": "lille.json",
    "Paris": "paris.json",
    "Mini réseau": "mini_reseau.json",
}


def _warn(parent, title: str, text: str):
    QMessageBox.warning(parent, title, text)


def _err(parent, title: str, text: str):
    QMessageBox.critical(parent, title, text)


def _attach_mpl_wheel_navigation(canvas, ax) -> None:
    """
    Navigation type trackpad / souris sur le graphe Matplotlib :
    - molette ou défilement 2 doigts : panoramique vertical
    - Maj + molette : panoramique horizontal
    - Ctrl + molette : zoom centré sur le curseur
    """

    def on_scroll(event):
        if event.inaxes != ax:
            return
        step = float(getattr(event, "step", 0) or 0)
        if step == 0:
            return
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        k = (event.key or "").lower()
        ctrl = "ctrl" in k or "control" in k
        shift = "shift" in k

        if ctrl and event.xdata is not None and event.ydata is not None:
            scale = math.pow(1.2, -step)
            cx, cy = float(event.xdata), float(event.ydata)
            relx = (cx - x0) / w
            rely = (cy - y0) / h
            nw, nh = w * scale, h * scale
            ax.set_xlim(cx - nw * relx, cx + nw * (1.0 - relx))
            ax.set_ylim(cy - nh * rely, cy + nh * (1.0 - rely))
        elif shift:
            dx = w * 0.12 * step
            ax.set_xlim(x0 - dx, x1 - dx)
        else:
            dy = h * 0.12 * step
            ax.set_ylim(y0 - dy, y1 - dy)

        canvas.draw_idle()

    canvas.mpl_connect("scroll_event", on_scroll)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
QWidget {
    color: #e8edf3;
    font-size: 12px;
}

QPushButton {
    background-color: #1a2535;
    border: 1px solid #2e4060;
    padding: 6px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #24344a;
}

QComboBox {
    background-color: #1a2535;
    border: 1px solid #2e4060;
    padding: 4px;
}

QComboBox QAbstractItemView {
    background-color: #1a2535;
    selection-background-color: #00c9a7;
}

QListWidget {
    background-color: #1a2535;
    border: 1px solid #2e4060;
}

QTabWidget::pane {
    border: 1px solid #2e4060;
    background: #0f1923;
}

QTabBar::tab {
    background: #1a2535;
    color: #e8edf3;
    padding: 8px 14px;
    border: 1px solid #2e4060;
    border-bottom: none;
}

QTabBar::tab:selected {
    background: #24344a;
    color: #00c9a7;
}

QTabBar::tab:hover {
    background: #2b3d55;
}
""")
        self.setWindowTitle("Réseau de Transport — Navigation")
        self.resize(1200, 780)
        self.setMinimumSize(960, 620)

        self.reseau: dict | None = None
        self.graphe_original: dict | None = None
        self.graphe_actif: dict | None = None
        self.perturbations: list[str] = []
        self._viz_pos = None
        self._viz_fig = None
        self._viz_canvas = None
        self._viz_toolbar = None
        self._viz_itineraire: list[str] | None = None

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(8, 8, 8, 8)

        # Barre haute
        bar = QFrame()
        bar.setStyleSheet(f"background-color: {COLORS['bg_panel']}; border-radius: 4px;")
        bl = QHBoxLayout(bar)
        title = QLabel("Réseau de Transport")
        title.setFont(QFont("Segoe UI", 16, _QT_FONT_BOLD))
        title.setStyleSheet(f"color: {COLORS['accent']}; padding: 8px;")
        bl.addWidget(title)
        bl.addStretch()
        self.lbl_perturb = QLabel("Aucune perturbation")
        self.lbl_perturb.setStyleSheet(f"color: {COLORS['accent']}; padding: 8px;")
        bl.addWidget(self.lbl_perturb)
        self.lbl_reseau = QLabel("Aucun réseau chargé")
        self.lbl_reseau.setStyleSheet(f"color: {COLORS['muted']}; padding: 8px;")
        bl.addWidget(self.lbl_reseau)
        root_layout.addWidget(bar)

        splitter = QSplitter(_QT_HORIZ)
        root_layout.addWidget(splitter, 1)

        # Panneau gauche (scroll)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(_QT_SCROLL_OFF)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {COLORS['bg_dark']}; }}")
        left_inner = QWidget()
        left_inner.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        self.left_layout = QVBoxLayout(left_inner)
        self.left_layout.setAlignment(_QT_ALIGN_TOP)
        scroll.setWidget(left_inner)
        scroll.setMinimumWidth(360)
        splitter.addWidget(scroll)

        self._build_left_panels()

        # Droite : onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            f"QTabWidget::pane {{ border: 1px solid #2e4060; background: {COLORS['bg_dark']}; }}"
        )
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(1, 1)

        self.out = QPlainTextEdit()
        self.out.setReadOnly(True)
        self.out.setFont(QFont("Consolas", 10))
        self.out.setStyleSheet(
            f"QPlainTextEdit {{ background: {COLORS['bg_panel']}; color: {COLORS['text']}; }}"
        )
        self.tabs.addTab(self.out, "Résultats")

        self.viz_container = QWidget()
        viz_outer = QVBoxLayout(self.viz_container)
        viz_outer.setContentsMargins(4, 4, 4, 4)

        bar_viz = QHBoxLayout()
        self.chk_viz_legend = QCheckBox("Afficher la légende")
        self.chk_viz_legend.setChecked(True)
        self.chk_viz_legend.setStyleSheet(f"color: {COLORS['text']};")
        self.chk_viz_legend.stateChanged.connect(self._on_viz_legend_toggled)
        bar_viz.addWidget(self.chk_viz_legend)
        hint = QLabel(
            "Molette ou piste tactile 2 doigts : déplacer · "
            "Maj + molette : gauche/droite · Ctrl + molette : zoom sous le curseur"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLORS['muted']}; font-size: 11px;")
        bar_viz.addWidget(hint, 1)
        viz_outer.addLayout(bar_viz)

        self.viz_plot_host = QWidget()
        self.viz_plot_layout = QVBoxLayout(self.viz_plot_host)
        self.viz_plot_layout.setContentsMargins(0, 0, 0, 0)
        viz_outer.addWidget(self.viz_plot_host, 1)

        self.tabs.addTab(self.viz_container, "Visualisation")

        self._welcome()

    def _group(self, title: str) -> tuple[QGroupBox, QVBoxLayout]:
        g = QGroupBox(title)
        g.setStyleSheet(
            f"QGroupBox {{ font-weight: bold; color: {COLORS['accent']}; "
            f"border: 1px solid #2e4060; margin-top: 8px; padding-top: 8px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; }}"
        )
        lo = QVBoxLayout(g)
        return g, lo

    def _build_left_panels(self):
        # 1 Réseau
        g, lo = self._group("1 · Chargement du réseau")
        lo.addWidget(QLabel("Ville :"))
        self.combo_ville = QComboBox()
        self.combo_ville.addItems(list(FICHIERS_RESEAU.keys()))
        lo.addWidget(self.combo_ville)
        b_load = QPushButton("Charger le réseau")
        b_load.clicked.connect(self._charger_reseau)
        lo.addWidget(b_load)
        self.left_layout.addWidget(g)

        # 2 Itinéraire
        g, lo = self._group("2 · Meilleur itinéraire (Dijkstra)")
        lo.addWidget(QLabel("Départ :"))
        self.combo_dep = QComboBox()
        lo.addWidget(self.combo_dep)
        lo.addWidget(QLabel("Arrivée :"))
        self.combo_arr = QComboBox()
        lo.addWidget(self.combo_arr)
        b_it = QPushButton("Calculer l'itinéraire")
        b_it.clicked.connect(self._calculer_itineraire)
        lo.addWidget(b_it)
        self.left_layout.addWidget(g)

        # 3 Parcours
        g, lo = self._group("3 · Parcours du réseau")
        lo.addWidget(QLabel("Départ BFS/DFS :"))
        self.combo_bfs_dep = QComboBox()
        lo.addWidget(self.combo_bfs_dep)
        lo.addWidget(QLabel("Arrivée BFS/DFS :"))
        self.combo_bfs_arr = QComboBox()
        lo.addWidget(self.combo_bfs_arr)
        row = QHBoxLayout()
        b_bfs = QPushButton("BFS")
        b_bfs.clicked.connect(self._faire_bfs)
        b_dfs = QPushButton("DFS")
        b_dfs.clicked.connect(self._faire_dfs)
        row.addWidget(b_bfs)
        row.addWidget(b_dfs)
        lo.addLayout(row)
        row2 = QHBoxLayout()
        b_co = QPushButton("Connexité")
        b_co.clicked.connect(self._verifier_connexite)
        b_tr = QPushButton("Correspondances")
        b_tr.clicked.connect(self._afficher_correspondances)
        row2.addWidget(b_co)
        row2.addWidget(b_tr)
        lo.addLayout(row2)
        self.left_layout.addWidget(g)

        # 4 Perturbations (setup complet)
        g, lo = self._group("4 · Perturbations")
        lo.addWidget(QLabel("Fermer une station :"))
        self.combo_fermer_st = QComboBox()
        lo.addWidget(self.combo_fermer_st)
        b_fs = QPushButton("Appliquer · station fermée")
        b_fs.setStyleSheet(f"background-color: {COLORS['danger']}; color: white; font-weight: bold;")
        b_fs.clicked.connect(self._fermer_station)
        lo.addWidget(b_fs)

        lo.addWidget(QLabel("Fermer une ligne entière :"))
        self.combo_fermer_ligne = QComboBox()
        lo.addWidget(self.combo_fermer_ligne)
        b_fl = QPushButton("Appliquer · ligne fermée")
        b_fl.setStyleSheet(f"background-color: {COLORS['danger']}; color: white; font-weight: bold;")
        b_fl.clicked.connect(self._fermer_ligne)
        lo.addWidget(b_fl)

        lo.addWidget(QLabel("Fermer un tronçon (deux stations voisines) :"))
        grid_t = QGridLayout()
        grid_t.addWidget(QLabel("Station A"), 0, 0)
        self.combo_tron_a = QComboBox()
        grid_t.addWidget(self.combo_tron_a, 0, 1)
        grid_t.addWidget(QLabel("Station B"), 1, 0)
        self.combo_tron_b = QComboBox()
        grid_t.addWidget(self.combo_tron_b, 1, 1)
        lo.addLayout(grid_t)
        b_tron = QPushButton("Appliquer · tronçon fermé")
        b_tron.setStyleSheet(f"background-color: {COLORS['accent2']}; color: #1a1a1a; font-weight: bold;")
        b_tron.clicked.connect(self._fermer_troncon_ui)
        lo.addWidget(b_tron)

        lo.addWidget(QLabel("Perturbations actives :"))
        self.list_perturb = QListWidget()
        self.list_perturb.setMaximumHeight(100)
        self.list_perturb.setStyleSheet(
            f"QListWidget {{ background: {COLORS['bg_panel']}; color: {COLORS['text']}; }}"
        )
        lo.addWidget(self.list_perturb)

        b_cmp = QPushButton("Comparer temps : normal vs réseau actuel")
        b_cmp.clicked.connect(self._comparer_temps_ui)
        lo.addWidget(b_cmp)

        b_reset = QPushButton("Rétablir le réseau (tout)")
        b_reset.clicked.connect(self._retablir)
        lo.addWidget(b_reset)
        self.left_layout.addWidget(g)

        self.left_layout.addStretch()

    def _welcome(self):
        self.out.setPlainText(
            "Bienvenue.\n\n"
            "1) Chargez un réseau.\n"
            "2) Calculez un itinéraire ou explorez avec BFS/DFS.\n"
            "3) Configurez des perturbations (station, ligne, tronçon).\n"
        )

    def _append_out(self, text: str):
        self.out.appendPlainText(text)

    def _clear_out(self):
        self.out.clear()

    def _verifier_reseau(self) -> bool:
        if self.graphe_actif is None:
            _warn(self, "Réseau", "Chargez d'abord un réseau.")
            return False
        return True

    def _update_perturb_labels(self):
        if self.perturbations:
            n = len(self.perturbations)
            self.lbl_perturb.setText(f"{n} perturbation(s) active(s)")
            self.lbl_perturb.setStyleSheet(f"color: {COLORS['accent2']}; padding: 8px;")
        else:
            self.lbl_perturb.setText("Aucune perturbation")
            self.lbl_perturb.setStyleSheet(f"color: {COLORS['accent']}; padding: 8px;")
        self.list_perturb.clear()
        for p in self.perturbations:
            self.list_perturb.addItem(p)

    def _fill_station_combos(self, stations: list[str]):
        for c in (
            self.combo_dep,
            self.combo_arr,
            self.combo_bfs_dep,
            self.combo_bfs_arr,
            self.combo_fermer_st,
            self.combo_tron_a,
            self.combo_tron_b,
        ):
            c.clear()
            c.addItems(stations)

    def _charger_reseau(self):
        ville = self.combo_ville.currentText()
        fichier = FICHIERS_RESEAU[ville]
        try:
            self.reseau = charger_reseau(fichier)
            self.graphe_original = self.reseau["graphe"]
            self.graphe_actif = copy.deepcopy(self.graphe_original)
            self.perturbations = []
            self._viz_pos = None
        except FileNotFoundError:
            _err(self, "Erreur", f"Fichier introuvable : {fichier}")
            return
        except Exception as e:
            _err(self, "Chargement", str(e))
            return

        stations = sorted(self.graphe_original.keys())
        lignes = sorted(self.reseau["lignes"].keys())
        self._fill_station_combos(stations)
        self.combo_fermer_ligne.clear()
        self.combo_fermer_ligne.addItems(lignes)

        self.lbl_reseau.setText(f"{self.reseau['nom']} — {len(stations)} stations")
        self.lbl_reseau.setStyleSheet(f"color: {COLORS['accent']}; padding: 8px;")
        self._update_perturb_labels()

        self._clear_out()
        self._append_out(f"Réseau chargé : {self.reseau['nom']}\n")
        self._append_out(f"  Stations : {len(stations)}\n")
        self._append_out(f"  Lignes : {', '.join(lignes)}\n")
        self._append_out(f"  Correspondances : {len(self.reseau.get('correspondances', []))}\n")

        self._rafraichir_visualisation(None)

    def _on_viz_legend_toggled(self, *_args) -> None:
        if self.reseau is None:
            return
        self._rafraichir_visualisation(self._viz_itineraire)

    def _rafraichir_visualisation(self, itineraire: list[str] | None):
        self._viz_itineraire = itineraire

        while self.viz_plot_layout.count():
            item = self.viz_plot_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if self._viz_fig is not None:
            plt.close(self._viz_fig)
            self._viz_fig = None

        if self.reseau is None or self.graphe_actif is None:
            lab = QLabel("Chargez un réseau pour afficher le graphe.")
            lab.setStyleSheet(f"color: {COLORS['muted']}; padding: 20px;")
            self.viz_plot_layout.addWidget(lab)
            return

        if self._viz_pos is not None and set(self._viz_pos.keys()) != set(self.graphe_actif.keys()):
            self._viz_pos = None

        Gnx = viz.graphe_vers_networkx(self.graphe_actif, self.reseau)
        show_leg = self.chk_viz_legend.isChecked()
        fig, ax_viz, pos = viz.construire_figure(
            Gnx,
            self.reseau,
            itineraire=itineraire,
            pos=self._viz_pos,
            show_legend=show_leg,
        )
        self._viz_pos = pos
        self._viz_fig = fig

        canvas = FigureCanvasQTAgg(fig)
        self.viz_plot_layout.addWidget(canvas)
        toolbar = NavigationToolbar2QT(canvas, self.viz_plot_host)
        self.viz_plot_layout.addWidget(toolbar)
        _attach_mpl_wheel_navigation(canvas, ax_viz)
        canvas.draw()

    def _calculer_itineraire(self):
        if not self._verifier_reseau():
            return
        dep = self.combo_dep.currentText()
        arr = self.combo_arr.currentText()
        if not dep or not arr:
            _warn(self, "Champs", "Choisissez départ et arrivée.")
            return
        if dep == arr:
            QMessageBox.information(self, "Info", "Départ et arrivée identiques.")
            return
        try:
            distances, parents = dijkstra(self.graphe_actif, dep)
            chemin = reconstruire_chemin(parents, dep, arr)
        except Exception as e:
            _err(self, "Dijkstra", str(e))
            return

        self._clear_out()
        self._append_out("ITINÉRAIRE OPTIMAL (Dijkstra)\n")
        self._append_out(f"  {dep} → {arr}\n")

        if not chemin:
            self._append_out("\nAucun itinéraire possible.")
            if self.perturbations:
                self._append_out("(Perturbations actives — essayez de rétablir le réseau.)\n")
            self._rafraichir_visualisation(None)
            self.tabs.setCurrentIndex(0)
            return

        temps_total = distances[arr]
        ligne_actuelle = None
        for i in range(len(chemin) - 1):
            station = chemin[i]
            ligne = parents[chemin[i + 1]][1] if parents[chemin[i + 1]] else "?"
            if ligne_actuelle is None:
                self._append_out(f"\n  Prendre la ligne {ligne} à {station}")
            elif ligne != ligne_actuelle:
                self._append_out(f"\n  Correspondance à {station} ({ligne_actuelle} → {ligne})")
            else:
                self._append_out(f"    ↓ {station}")
            ligne_actuelle = ligne

        self._append_out(f"\n\nArrivée : {chemin[-1]}")
        self._append_out(f"\nTemps total : {temps_total} s ({temps_total // 60} min {temps_total % 60} s)")
        self._append_out(f"\nStations traversées : {len(chemin)}")
        if self.perturbations:
            self._append_out("\n--- Perturbations actives ---")
            for p in self.perturbations:
                self._append_out(f"  • {p}")

        self._rafraichir_visualisation(chemin)
        self.tabs.setCurrentIndex(1)

    def _faire_bfs(self):
        if not self._verifier_reseau():
            return
        dep = self.combo_bfs_dep.currentText()
        arr = self.combo_bfs_arr.currentText()
        if not dep or not arr:
            _warn(self, "BFS", "Choisissez départ et arrivée.")
            return
        try:
            res = bfs(self.graphe_actif, dep, arr)
        except ValueError as e:
            _err(self, "BFS", str(e))
            return
        self._clear_out()
        self._append_out("BFS — moins d'arrêts\n")
        if not res["found"]:
            self._append_out("Aucun chemin.")
        else:
            self._append_out(f"Arrêts intermédiaires : {res['stops']}\n")
            for s in res["path"]:
                self._append_out(f"  {s}")

    def _faire_dfs(self):
        if not self._verifier_reseau():
            return
        dep = self.combo_bfs_dep.currentText()
        arr = self.combo_bfs_arr.currentText()
        if not dep:
            _warn(self, "DFS", "Choisissez un départ.")
            return
        try:
            res = dfs(self.graphe_actif, dep, arr if arr else None)
        except ValueError as e:
            _err(self, "DFS", str(e))
            return
        self._clear_out()
        self._append_out("DFS\n")
        if arr and res["found"]:
            self._append_out("Chemin :\n" + "\n".join(f"  {s}" for s in res["path"]))
        elif arr:
            self._append_out("Aucun chemin.")
        vis = res["visited"][:20]
        self._append_out("\nVisite (extrait) : " + " → ".join(vis))
        if len(res["visited"]) > 20:
            self._append_out(" → …")

    def _verifier_connexite(self):
        if not self._verifier_reseau():
            return
        res = verifier_connexite(self.graphe_actif)
        self._clear_out()
        self._append_out("CONNEXITÉ\n")
        self._append_out(f"  Total : {res['total_count']}, accessibles : {res['reachable_count']}\n")
        if res["is_connected"]:
            self._append_out("Réseau connexe.")
        else:
            self._append_out("Réseau NON connexe. Inaccessibles :")
            for s in res["unreachable"]:
                self._append_out(f"  • {s}")

    def _afficher_correspondances(self):
        if not self._verifier_reseau():
            return
        transfers = get_transfer_stations(self.reseau)
        self._clear_out()
        self._append_out(f"CORRESPONDANCES ({len(transfers)})\n")
        for station, lignes in transfers:
            self._append_out(f"  {station}  [{', '.join(sorted(lignes))}]")

    def _fermer_station(self):
        if not self._verifier_reseau():
            return
        station = self.combo_fermer_st.currentText()
        if not station or station not in self.graphe_actif:
            _warn(self, "Station", "Station invalide.")
            return
        self.graphe_actif = fermer_station(self.graphe_actif, station)
        self.perturbations.append(f"Station fermée : {station}")
        self._update_perturb_labels()
        stations = sorted(self.graphe_actif.keys())
        self._fill_station_combos(stations)
        self._clear_out()
        self._append_out(f"Station fermée : {station}")
        self._rafraichir_visualisation(None)

    def _fermer_ligne(self):
        if not self._verifier_reseau():
            return
        ligne = self.combo_fermer_ligne.currentText()
        if not ligne:
            return
        self.graphe_actif = fermer_ligne_entiere(self.graphe_actif, ligne)
        self.perturbations.append(f"Ligne fermée : {ligne}")
        self._update_perturb_labels()
        self._clear_out()
        self._append_out(f"Ligne fermée : {ligne}")
        self._rafraichir_visualisation(None)

    def _fermer_troncon_ui(self):
        if not self._verifier_reseau():
            return
        a = self.combo_tron_a.currentText()
        b = self.combo_tron_b.currentText()
        if not a or not b:
            _warn(self, "Tronçon", "Choisissez deux stations.")
            return
        if a == b:
            _warn(self, "Tronçon", "Les deux stations doivent être différentes.")
            return
        if a not in self.graphe_actif or b not in self.graphe_actif:
            _warn(self, "Tronçon", "Station absente du graphe actif.")
            return
        voisins = {e["voisin"] for e in self.graphe_actif.get(a, [])}
        if b not in voisins:
            if _QT == 6:
                rep = QMessageBox.question(
                    self,
                    "Tronçon",
                    f"« {a} » et « {b} » ne sont pas voisines dans le graphe actuel.\n"
                    "Appliquer quand même (aucun changement si pas d'arête) ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if rep != QMessageBox.StandardButton.Yes:
                    return
            else:
                rep = QMessageBox.question(
                    self,
                    "Tronçon",
                    f"« {a} » et « {b} » ne sont pas voisines dans le graphe actuel.\n"
                    "Appliquer quand même (aucun changement si pas d'arête) ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if rep != QMessageBox.Yes:
                    return
        self.graphe_actif = fermer_troncon(self.graphe_actif, a, b)
        self.perturbations.append(f"Tronçon fermé : {a} — {b}")
        self._update_perturb_labels()
        self._clear_out()
        self._append_out(f"Tronçon fermé entre « {a} » et « {b} ».")
        self._rafraichir_visualisation(None)

    def _comparer_temps_ui(self):
        if not self._verifier_reseau() or self.graphe_original is None:
            return
        dep = self.combo_dep.currentText()
        arr = self.combo_arr.currentText()
        if not dep or not arr:
            _warn(self, "Comparaison", "Renseignez départ et arrivée (section 2).")
            return
        if dep not in self.graphe_original or arr not in self.graphe_original:
            _warn(self, "Comparaison", "Stations absentes du réseau d'origine.")
            return
        msg = comparer_temps_trajet(self.graphe_original, dep, arr, self.graphe_actif)
        self._clear_out()
        self._append_out("COMPARAISON temps (graphe d'origine vs actuel)\n")
        self._append_out(f"  {dep} → {arr}\n\n")
        self._append_out(msg)

    def _retablir(self):
        if self.graphe_original is None:
            return
        self.graphe_actif = copy.deepcopy(self.graphe_original)
        self.perturbations = []
        self._viz_pos = None
        self._update_perturb_labels()
        stations = sorted(self.graphe_original.keys())
        self._fill_station_combos(stations)
        self._clear_out()
        self._append_out("Réseau rétabli (toutes perturbations levées).")
        self._rafraichir_visualisation(None)


def main():
    if _QT == 6:
        app = QApplication(sys.argv)
    else:
        app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec() if _QT == 6 else app.exec_())


if __name__ == "__main__":
    main()
