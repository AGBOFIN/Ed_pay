"""
Fenêtre principale de l'application EduPaie.
Fournit une navigation fluide et intuitive entre le Tableau de bord et la Gestion des élèves,
accompagnée d'une barre d'outils moderne, de raccourcis clavier et d'un guide utilisateur intégré.
"""

from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QMenuBar, QMenu, QStackedWidget, QDialog,
    QToolBar, QLabel, QPushButton, QMessageBox, QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QFont
from ui.eleves_widget import ElevesWidget
from ui.dashboard_widget import DashboardWidget
from ui.parametres_dialog import ParametresDialog
from ui.aide_dialog import AideDialog


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application EduPaie."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduPaie - Gestion des Paiements Scolaires")
        self.setMinimumSize(1100, 740)
        
        self.setup_ui()
        
        # Affiche le tableau de bord au démarrage
        self.afficher_tableau_de_bord()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.setup_shortcuts()
        
        # UN QStackedWidget défini une seule fois comme widget central.
        # Strictement conforme aux contraintes d'architecture et de tests.
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.dashboard_widget = DashboardWidget()
        self.eleves_widget = ElevesWidget(main_window=self)
        self.stack.addWidget(self.dashboard_widget)
        self.stack.addWidget(self.eleves_widget)
    
    def create_tool_bar(self):
        """Crée une barre d'outils moderne pour navigation et actions rapides."""
        self.nav_toolbar = QToolBar("Navigation principale")
        self.nav_toolbar.setMovable(False)
        self.nav_toolbar.setIconSize(self.nav_toolbar.iconSize())
        self.addToolBar(Qt.TopToolBarArea, self.nav_toolbar)
        
        # Logo / Titre dans la toolbar
        logo_label = QLabel("  🎓 <b>EduPaie</b>  ")
        logo_label.setStyleSheet("font-size: 16px; color: #1E3A8A; font-weight: bold; padding-right: 8px;")
        self.nav_toolbar.addWidget(logo_label)
        
        # Bouton Tableau de bord
        self.btn_nav_dashboard = QPushButton("📊 Tableau de bord")
        self.btn_nav_dashboard.setToolTip("Afficher le tableau de bord financier (Ctrl+1)")
        self.btn_nav_dashboard.clicked.connect(self.afficher_tableau_de_bord)
        self.nav_toolbar.addWidget(self.btn_nav_dashboard)
        
        # Bouton Élèves
        self.btn_nav_eleves = QPushButton("👥 Gestion des élèves")
        self.btn_nav_eleves.setProperty("variant", "secondary")
        self.btn_nav_eleves.setToolTip("Afficher la liste des élèves (Ctrl+2)")
        self.btn_nav_eleves.clicked.connect(self.afficher_gestion_eleves)
        self.nav_toolbar.addWidget(self.btn_nav_eleves)
        
        # Séparateur
        self.nav_toolbar.addSeparator()
        
        # Action rapide : Nouveau versement
        self.btn_nav_paiement = QPushButton("💳 Nouveau paiement")
        self.btn_nav_paiement.setProperty("variant", "success")
        self.btn_nav_paiement.setToolTip("Enregistrer un nouveau paiement (Ctrl+P)")
        self.btn_nav_paiement.clicked.connect(self.enregistrer_paiement)
        self.nav_toolbar.addWidget(self.btn_nav_paiement)
        
        # Action rapide : Ajouter un élève
        self.btn_nav_ajouter = QPushButton("➕ Nouvel élève")
        self.btn_nav_ajouter.setProperty("variant", "secondary")
        self.btn_nav_ajouter.setToolTip("Inscrire un nouvel élève (Ctrl+N)")
        self.btn_nav_ajouter.clicked.connect(self.ajouter_nouvel_eleve)
        self.nav_toolbar.addWidget(self.btn_nav_ajouter)
        
        # Espace étirable
        from PySide6.QtWidgets import QSizePolicy
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.nav_toolbar.addWidget(spacer)
        
        # Bouton Actualiser
        self.btn_nav_refresh = QPushButton("🔄 Actualiser")
        self.btn_nav_refresh.setProperty("variant", "secondary")
        self.btn_nav_refresh.setToolTip("Actualiser toutes les données (F5)")
        self.btn_nav_refresh.clicked.connect(self.rafraichir_tout)
        self.nav_toolbar.addWidget(self.btn_nav_refresh)
        
        # Bouton Aide
        self.btn_nav_aide = QPushButton("❓ Aide & Guide")
        self.btn_nav_aide.setProperty("variant", "secondary")
        self.btn_nav_aide.setToolTip("Consulter le guide et les raccourcis (F1)")
        self.btn_nav_aide.clicked.connect(self.afficher_aide)
        self.nav_toolbar.addWidget(self.btn_nav_aide)
    
    def create_menu_bar(self):
        """Crée la barre de menu classique avec raccourcis."""
        menu_bar = self.menuBar()
        
        # Menu Fichier
        fichier_menu = menu_bar.addMenu("&Fichier")
        action_refresh = fichier_menu.addAction("Actualiser les données\tF5")
        action_refresh.triggered.connect(self.rafraichir_tout)
        
        fichier_menu.addSeparator()
        action_quitter = fichier_menu.addAction("Quitter\tCtrl+Q")
        action_quitter.triggered.connect(self.close)
        
        # Menu Élèves
        eleves_menu = menu_bar.addMenu("&Élèves")
        gestion_eleves_action = eleves_menu.addAction("Gérer les élèves")
        gestion_eleves_action.triggered.connect(self.afficher_gestion_eleves)
        
        action_ajouter = eleves_menu.addAction("Ajouter un nouvel élève\tCtrl+N")
        action_ajouter.triggered.connect(self.ajouter_nouvel_eleve)
        
        # Menu Paiements
        paiements_menu = menu_bar.addMenu("&Paiements")
        enregistrer_paiement_action = paiements_menu.addAction("Enregistrer un paiement")
        enregistrer_paiement_action.triggered.connect(self.enregistrer_paiement)
        
        # Menu Tableau de bord
        tableau_menu = menu_bar.addMenu("&Tableau de bord")
        afficher_tableau_action = tableau_menu.addAction("Afficher le tableau de bord")
        afficher_tableau_action.triggered.connect(self.afficher_tableau_de_bord)
        
        # Menu Paramètres
        parametres_menu = menu_bar.addMenu("&Paramètres")
        parametres_action = parametres_menu.addAction("Paramètres...")
        parametres_action.triggered.connect(self.afficher_parametres)
        
        # Menu Aide
        aide_menu = menu_bar.addMenu("&Aide")
        action_guide = aide_menu.addAction("Guide d'utilisation et raccourcis\tF1")
        action_guide.triggered.connect(self.afficher_aide)
        action_apropos = aide_menu.addAction("À propos d'EduPaie")
        action_apropos.triggered.connect(self.afficher_aide)
    
    def setup_shortcuts(self):
        """Configure les raccourcis clavier globaux."""
        # F5 pour actualiser
        act_f5 = QAction(self)
        act_f5.setShortcut(QKeySequence("F5"))
        act_f5.triggered.connect(self.rafraichir_tout)
        self.addAction(act_f5)
        
        # F1 pour l'aide
        act_f1 = QAction(self)
        act_f1.setShortcut(QKeySequence("F1"))
        act_f1.triggered.connect(self.afficher_aide)
        self.addAction(act_f1)
        
        # Ctrl+1 pour le tableau de bord
        act_ctrl1 = QAction(self)
        act_ctrl1.setShortcut(QKeySequence("Ctrl+1"))
        act_ctrl1.triggered.connect(self.afficher_tableau_de_bord)
        self.addAction(act_ctrl1)
        
        # Ctrl+2 pour la gestion des élèves
        act_ctrl2 = QAction(self)
        act_ctrl2.setShortcut(QKeySequence("Ctrl+2"))
        act_ctrl2.triggered.connect(self.afficher_gestion_eleves)
        self.addAction(act_ctrl2)
        
        # Ctrl+P pour enregistrer un paiement
        act_ctrl_p = QAction(self)
        act_ctrl_p.setShortcut(QKeySequence("Ctrl+P"))
        act_ctrl_p.triggered.connect(self.enregistrer_paiement)
        self.addAction(act_ctrl_p)
        
        # Ctrl+N pour ajouter un élève
        act_ctrl_n = QAction(self)
        act_ctrl_n.setShortcut(QKeySequence("Ctrl+N"))
        act_ctrl_n.triggered.connect(self.ajouter_nouvel_eleve)
        self.addAction(act_ctrl_n)
    
    def create_status_bar(self):
        """Crée la barre de statut avec indicateurs permanents."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Badge permanent dans la barre d'état
        self.badge_info = QLabel("  Base locale SQLite  |  Année 2025-2026  |  EduPaie v1.2  ")
        self.badge_info.setStyleSheet("color: #64748B; font-size: 11px;")
        self.status_bar.addPermanentWidget(self.badge_info)
        
        self.status_bar.showMessage("Prêt")
    
    def _mettre_a_jour_boutons_nav(self, est_tableau_de_bord):
        """Met à jour l'apparence des boutons de la barre d'outils selon l'écran actif."""
        if hasattr(self, 'btn_nav_dashboard') and hasattr(self, 'btn_nav_eleves'):
            if est_tableau_de_bord:
                self.btn_nav_dashboard.setProperty("variant", "")
                self.btn_nav_dashboard.setStyleSheet("background-color: #2563EB; color: white;")
                self.btn_nav_eleves.setProperty("variant", "secondary")
                self.btn_nav_eleves.setStyleSheet("")
            else:
                self.btn_nav_dashboard.setProperty("variant", "secondary")
                self.btn_nav_dashboard.setStyleSheet("")
                self.btn_nav_eleves.setProperty("variant", "")
                self.btn_nav_eleves.setStyleSheet("background-color: #2563EB; color: white;")
    
    def afficher_gestion_eleves(self):
        """Affiche le widget de gestion des élèves."""
        self.stack.setCurrentWidget(self.eleves_widget)
        self.status_bar.showMessage("Gestion des élèves - Sélectionnez un élève pour effectuer une action")
        self._mettre_a_jour_boutons_nav(False)
    
    def enregistrer_paiement(self):
        """Ouvre la liste des élèves pour choisir celui à débiter."""
        self.afficher_gestion_eleves()
        self.status_bar.showMessage("Sélectionnez un élève pour enregistrer son paiement")
    
    def afficher_tableau_de_bord(self):
        """Affiche le tableau de bord."""
        self.stack.setCurrentWidget(self.dashboard_widget)
        self.status_bar.showMessage("Tableau de bord - Vue d'ensemble financière")
        self._mettre_a_jour_boutons_nav(True)
    
    def ajouter_nouvel_eleve(self):
        """Ouvre directement le formulaire d'ajout d'élève."""
        self.afficher_gestion_eleves()
        self.eleves_widget.on_ajouter()
    
    def afficher_parametres(self):
        """Affiche le dialogue de paramètres."""
        dialog = ParametresDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Rafraîchit les écrans après modification des paramètres
            self.dashboard_widget.rafraichir()
            self.eleves_widget.charger_donnees()
            self.status_bar.showMessage("Paramètres mis à jour")
    
    def rafraichir_tableau_de_bord(self):
        """Rafraîchit le tableau de bord s'il est affiché."""
        if self.dashboard_widget is not None:
            self.dashboard_widget.rafraichir()
    
    def rafraichir_tout(self):
        """Actualise toutes les vues (tableau de bord et liste des élèves)."""
        if self.dashboard_widget is not None:
            self.dashboard_widget.rafraichir()
        if self.eleves_widget is not None:
            self.eleves_widget.charger_donnees()
        self.status_bar.showMessage("Données actualisées avec succès", 3000)
    
    def afficher_aide(self):
        """Ouvre le dialogue de guide d'utilisation et de raccourcis."""
        dialog = AideDialog(self)
        dialog.exec()
