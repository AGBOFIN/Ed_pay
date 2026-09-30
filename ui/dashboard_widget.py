"""
Widget pour le tableau de bord.
Affiche les indicateurs globaux et la liste des élèves filtrable.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QComboBox, QHeaderView, QFrame
)
from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel
from PySide6.QtGui import QColor, QBrush
from services.dashboard_service import DashboardService
from services.solde_service import SoldeService


class DashboardTableModel(QAbstractTableModel):
    """Modèle de table pour afficher les élèves dans le tableau de bord."""
    
    def __init__(self, eleves=None, parent=None):
        """
        Initialise le modèle.
        
        Args:
            eleves: Liste de dictionnaires représentant les élèves
            parent: Widget parent
        """
        super().__init__(parent)
        self.eleves = eleves or []
        self.headers = ["ID", "Nom", "Prénom", "Classe", "Total dû (FCFA)", "Payé (FCFA)", "Solde (FCFA)", "Statut"]
    
    def rowCount(self, parent=None):
        """Retourne le nombre de lignes."""
        return len(self.eleves)
    
    def columnCount(self, parent=None):
        """Retourne le nombre de colonnes."""
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        """Retourne les données pour une cellule."""
        if not index.isValid():
            return None
        
        eleve = self.eleves[index.row()]
        col = index.column()
        
        total_du_fcfa = eleve['total_du']
        total_paye_fcfa = eleve.get('total_paye', 0)
        
        if role == Qt.DisplayRole:
            if col == 0:
                return str(eleve['id'])
            elif col == 1:
                return eleve['nom']
            elif col == 2:
                return eleve['prenom']
            elif col == 3:
                return eleve['classe']
            elif col == 4:
                return SoldeService.formater_monnaie_fcfa(total_du_fcfa)
            elif col == 5:
                return SoldeService.formater_monnaie_fcfa(total_paye_fcfa)
            elif col == 6:
                solde = eleve.get('solde', SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa))
                return SoldeService.formater_monnaie_fcfa(solde)
            elif col == 7:
                return eleve.get('statut', SoldeService.determiner_statut(total_du_fcfa, total_paye_fcfa))
        
        elif role == Qt.BackgroundRole and col == 7:
            # Couleur de fond pour la colonne statut
            statut = eleve.get('statut', SoldeService.determiner_statut(total_du_fcfa, total_paye_fcfa))
            
            if statut == "Soldé":
                return QBrush(QColor(144, 238, 144))  # Vert clair
            elif statut == "Partiellement payé":
                return QBrush(QColor(255, 200, 100))  # Orange
            else:  # Non payé
                return QBrush(QColor(255, 182, 193))  # Rouge clair
        
        elif role == Qt.ForegroundRole and col == 7:
            # Texte foncé pour lisibilité sur fond clair
            return QBrush(QColor("#1B1B1B"))
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Retourne les en-têtes de colonnes."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def set_eleves(self, eleves):
        """
        Met à jour la liste des élèves.
        
        Args:
            eleves: Nouvelle liste d'élèves
        """
        self.beginResetModel()
        self.eleves = eleves
        self.endResetModel()


class DashboardWidget(QWidget):
    """Widget principal pour le tableau de bord."""
    
    def __init__(self, parent=None):
        """Initialise le widget."""
        super().__init__(parent)
        self.dashboard_service = DashboardService()
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Section des cartes d'indicateurs
        cartes_layout = self._creer_section_cartes()
        layout.addLayout(cartes_layout)
        
        # Ligne de séparation
        layout.addWidget(self._creer_separation())
        
        # Section du tableau des élèves
        tableau_layout = self._creer_section_tableau()
        layout.addLayout(tableau_layout)
    
    def _creer_section_cartes(self):
        """Crée la section des 4 cartes d'indicateurs."""
        layout = QHBoxLayout()
        
        # Carte 1 : Nombre d'élèves
        self.nb_eleves_card = self._creer_carte("Nombre d'élèves", "0", "#3498db")
        layout.addWidget(self.nb_eleves_card)
        
        # Carte 2 : Total encaissé
        self.total_encaisse_card = self._creer_carte("Total encaissé", "0 FCFA", "#27ae60")
        layout.addWidget(self.total_encaisse_card)
        
        # Carte 3 : Total restant dû
        self.total_restant_du_card = self._creer_carte("Total restant dû", "0 FCFA", "#e74c3c")
        layout.addWidget(self.total_restant_du_card)
        
        # Carte 4 : Élèves non soldés
        self.nb_non_soldes_card = self._creer_carte("Élèves non soldés", "0", "#f39c12")
        layout.addWidget(self.nb_non_soldes_card)
        
        return layout
    
    def _creer_carte(self, titre, valeur, couleur):
        """
        Crée une carte d'indicateur.
        
        Args:
            titre: Titre de la carte
            valeur: Valeur initiale
            couleur: Couleur de fond (code hex)
            
        Returns:
            QWidget: La carte créée
        """
        from PySide6.QtWidgets import QFrame
        
        carte = QFrame()
        carte.setStyleSheet(f"""
            QFrame {{
                background-color: {couleur};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        carte_layout = QVBoxLayout(carte)
        
        titre_label = QLabel(titre)
        titre_label.setStyleSheet("font-size: 14px; color: white; font-weight: bold;")
        carte_layout.addWidget(titre_label)
        
        valeur_label = QLabel(valeur)
        valeur_label.setStyleSheet("font-size: 28px; color: white; font-weight: bold;")
        carte_layout.addWidget(valeur_label)
        
        # Stocke la référence pour mise à jour
        carte.valeur_label = valeur_label
        
        return carte
    
    def _creer_separation(self):
        """Crée une ligne de séparation."""
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        return frame
    
    def _creer_section_tableau(self):
        """Crée la section du tableau des élèves."""
        layout = QVBoxLayout()
        
        # Barre de filtres
        filtres_layout = QHBoxLayout()
        
        filtres_layout.addWidget(QLabel("Filtrer par statut :"))
        
        self.statut_combo = QComboBox()
        self.statut_combo.addItems(["Tous", "Soldé", "Partiellement payé", "Non payé"])
        self.statut_combo.currentIndexChanged.connect(self.on_statut_changed)
        filtres_layout.addWidget(self.statut_combo)
        
        filtres_layout.addStretch()
        layout.addLayout(filtres_layout)
        
        # Table des élèves
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Classe", "Total dû (FCFA)", "Payé (FCFA)", "Solde (FCFA)", "Statut"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)  # Désactivé pendant le remplissage
        
        # Configuration des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nom
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Prénom
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Classe
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total dû
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Payé
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Solde
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Statut
        
        layout.addWidget(self.table)
        
        return layout
    
    def charger_donnees(self):
        """Charge les données depuis le service."""
        try:
            # Charge les indicateurs
            indicateurs = self.dashboard_service.obtenir_indicateurs()
            self.mettre_a_jour_cartes(indicateurs)
            
            # Charge la liste des élèves
            self.apply_filters()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données : {str(e)}")
    
    def mettre_a_jour_cartes(self, indicateurs):
        """Met à jour les cartes avec les indicateurs."""
        # Nombre d'élèves
        self.nb_eleves_card.valeur_label.setText(str(indicateurs['nb_eleves']))
        
        # Total encaissé
        self.total_encaisse_card.valeur_label.setText(SoldeService.formater_monnaie_fcfa(indicateurs['total_encaisse']))
        
        # Total restant dû
        self.total_restant_du_card.valeur_label.setText(SoldeService.formater_monnaie_fcfa(indicateurs['total_restant_du']))
        
        # Élèves non soldés
        self.nb_non_soldes_card.valeur_label.setText(str(indicateurs['nb_eleves_non_soldes']))
    
    def apply_filters(self):
        """Applique le filtre de statut."""
        statut = self.statut_combo.currentText()
        
        try:
            eleves = self.dashboard_service.obtenir_liste_eleves_filtree_par_statut(statut)
            self.mettre_a_jour_tableau(eleves)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erreur", f"Erreur lors du filtrage : {str(e)}")
    
    def mettre_a_jour_tableau(self, eleves):
        """Met à jour le tableau avec la liste des élèves."""
        self.table.setSortingEnabled(False)  # Désactive le tri pendant le remplissage
        self.table.setRowCount(len(eleves))
        
        for row, eleve in enumerate(eleves):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(eleve['id'])))
            
            # Nom
            self.table.setItem(row, 1, QTableWidgetItem(eleve['nom']))
            
            # Prénom
            self.table.setItem(row, 2, QTableWidgetItem(eleve['prenom']))
            
            # Classe
            self.table.setItem(row, 3, QTableWidgetItem(eleve['classe']))
            
            # Total dû
            total_du_fcfa = eleve['total_du']
            self.table.setItem(row, 4, QTableWidgetItem(SoldeService.formater_monnaie_fcfa(total_du_fcfa)))
            
            # Payé
            total_paye = eleve.get('total_paye', 0)
            self.table.setItem(row, 5, QTableWidgetItem(SoldeService.formater_monnaie_fcfa(total_paye)))
            
            # Solde
            solde = eleve.get('solde', SoldeService.calculer_solde(eleve['total_du'], total_paye))
            self.table.setItem(row, 6, QTableWidgetItem(SoldeService.formater_monnaie_fcfa(solde)))
            
            # Statut
            statut = eleve.get('statut', SoldeService.determiner_statut(eleve['total_du'], total_paye))
            item_statut = QTableWidgetItem(statut)
            
            # Couleur de fond selon le statut
            if statut == "Soldé":
                item_statut.setBackground(QBrush(QColor(144, 238, 144)))
            elif statut == "Partiellement payé":
                item_statut.setBackground(QBrush(QColor(255, 200, 100)))
            else:  # Non payé
                item_statut.setBackground(QBrush(QColor(255, 182, 193)))
            
            # Texte foncé pour lisibilité
            item_statut.setForeground(QBrush(QColor("#1B1B1B")))
            
            self.table.setItem(row, 7, item_statut)
        
        self.table.setSortingEnabled(True)  # Réactive le tri après le remplissage
    
    def on_statut_changed(self, index):
        """
        Gère le changement de filtre de statut.
        
        Args:
            index: Index sélectionné dans le combo
        """
        self.apply_filters()
    
    def rafraichir(self):
        """Rafraîchit toutes les données du tableau de bord."""
        self.charger_donnees()
