"""
Fenêtre principale de l'application EduPaie.
Contient le menu principal et la barre de statut.
"""

from PySide6.QtWidgets import QMainWindow, QStatusBar, QMenuBar, QMenu, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from ui.eleves_widget import ElevesWidget
from ui.dashboard_widget import DashboardWidget


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    
    def __init__(self):
        """Initialise la fenêtre principale."""
        super().__init__()
        self.setWindowTitle("EduPaie - Gestion des Paiements Scolaires")
        self.setMinimumSize(1000, 700)
        
        self.eleves_widget = None
        self.dashboard_widget = None
        self.setup_ui()
        
        # Affiche le tableau de bord au démarrage
        self.afficher_tableau_de_bord()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.create_menu_bar()
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Crée la barre de menu."""
        menu_bar = self.menuBar()
        
        # Menu Fichier
        fichier_menu = menu_bar.addMenu("&Fichier")
        
        # Menu Élèves
        eleves_menu = menu_bar.addMenu("&Élèves")
        gestion_eleves_action = eleves_menu.addAction("Gérer les élèves")
        gestion_eleves_action.triggered.connect(self.afficher_gestion_eleves)
        
        # Menu Paiements
        paiements_menu = menu_bar.addMenu("&Paiements")
        enregistrer_paiement_action = paiements_menu.addAction("Enregistrer un paiement")
        enregistrer_paiement_action.triggered.connect(self.enregistrer_paiement)
        
        # Menu Tableau de bord
        tableau_menu = menu_bar.addMenu("&Tableau de bord")
        afficher_tableau_action = tableau_menu.addAction("Afficher le tableau de bord")
        afficher_tableau_action.triggered.connect(self.afficher_tableau_de_bord)
        
        # Menu Aide
        aide_menu = menu_bar.addMenu("&Aide")
    
    def create_status_bar(self):
        """Crée la barre de statut."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")
    
    def afficher_gestion_eleves(self):
        """Affiche le widget de gestion des élèves."""
        if self.eleves_widget is None:
            self.eleves_widget = ElevesWidget(main_window=self)
        
        # Crée un widget central avec layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.eleves_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setCentralWidget(central_widget)
        self.status_bar.showMessage("Gestion des élèves")
    
    def enregistrer_paiement(self):
        """Affiche la gestion des élèves pour enregistrer un paiement."""
        self.afficher_gestion_eleves()
        self.status_bar.showMessage("Sélectionnez un élève, puis cliquez sur 'Enregistrer paiement'")
    
    def afficher_tableau_de_bord(self):
        """Affiche le tableau de bord."""
        if self.dashboard_widget is None:
            self.dashboard_widget = DashboardWidget()
        
        # Crée un widget central avec layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.dashboard_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setCentralWidget(central_widget)
        self.status_bar.showMessage("Tableau de bord")
    
    def rafraichir_tableau_de_bord(self):
        """Rafraîchit le tableau de bord s'il est affiché."""
        if self.dashboard_widget is not None:
            self.dashboard_widget.rafraichir()
