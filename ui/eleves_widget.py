"""
Widget pour la gestion des élèves.
Affiche la liste des élèves avec recherche et filtres.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QHeaderView, QDialog
)
from PySide6.QtCore import Qt, QAbstractTableModel, QUrl
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush, QDesktopServices
from services.eleve_service import EleveService, ValidationError
from services.solde_service import SoldeService
from services.paiement_service import PaiementService
from services.recu_service import RecuService
from services.recu_pdf import generer_recu_pdf
from ui.eleve_form_dialog import EleveFormDialog
from ui.fiche_eleve_dialog import FicheEleveDialog


class ElevesTableModel(QAbstractTableModel):
    """Modèle de table pour afficher les élèves."""
    
    def __init__(self, eleves=None, parent=None):
        """
        Initialise le modèle.
        
        Args:
            eleves: Liste de dictionnaires représentant les élèves
            parent: Widget parent
        """
        super().__init__(parent)
        self.eleves = eleves or []
        self.headers = ["ID", "Nom", "Prénom", "Classe", "Année scolaire", "Total dû (FCFA)", "Payé (FCFA)", "Solde (FCFA)", "Statut"]
    
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
        
        # total_du est déjà en francs CFA (entier)
        total_du_fcfa = eleve['total_du']
        total_paye = eleve.get('total_paye', 0)
        
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
                return eleve['annee_scolaire']
            elif col == 5:
                # Total dû en FCFA
                return SoldeService.formater_monnaie_fcfa(total_du_fcfa)
            elif col == 6:
                # Payé en FCFA
                return SoldeService.formater_monnaie_fcfa(total_paye)
            elif col == 7:
                # Solde en FCFA
                solde = SoldeService.calculer_solde(total_du_fcfa, total_paye)
                return SoldeService.formater_monnaie_fcfa(solde)
            elif col == 8:
                # Statut
                return SoldeService.determiner_statut(total_du_fcfa, total_paye)
        
        elif role == Qt.BackgroundRole and col == 8:
            # Couleur de fond pour la colonne statut
            statut = SoldeService.determiner_statut(total_du_fcfa, total_paye)
            
            if statut == "Soldé":
                return QBrush(QColor(144, 238, 144))  # Vert clair
            elif statut == "Partiellement payé":
                return QBrush(QColor(255, 200, 100))  # Orange
            else:  # Non payé
                return QBrush(QColor(255, 182, 193))  # Rouge clair
        
        elif role == Qt.ForegroundRole and col == 8:
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
    
    def get_eleve_id(self, index):
        """
        Récupère l'ID de l'élève à un index donné.
        
        Args:
            index: Index dans la table
            
        Returns:
            int: ID de l'élève
        """
        if index.isValid() and index.row() < len(self.eleves):
            return self.eleves[index.row()]['id']
        return None


class ElevesWidget(QWidget):
    """Widget principal pour la gestion des élèves."""
    
    def __init__(self, parent=None, main_window=None):
        """
        Initialise le widget.
        
        Args:
            parent: Widget parent
            main_window: Référence à la fenêtre principale pour le rafraîchissement
        """
        super().__init__(parent)
        self.service = EleveService()
        self.current_classe_filter = None
        self.current_search = None
        self.main_window = main_window
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Barre de recherche et filtres
        filters_layout = QHBoxLayout()
        
        # Recherche
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher par nom ou prénom...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        filters_layout.addWidget(self.search_edit)
        
        # Filtre classe
        self.classe_combo = QComboBox()
        self.classe_combo.addItem("Toutes les classes")
        self.classe_combo.currentIndexChanged.connect(self.on_classe_changed)
        filters_layout.addWidget(self.classe_combo)
        
        layout.addLayout(filters_layout)
        
        # Table des élèves
        self.table = QTableView()
        self.model = ElevesTableModel()
        self.table.setModel(self.model)
        
        # Configuration de la table
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        # Ajustement des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nom
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Prénom
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Classe
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Année
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Total dû
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Payé
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Solde
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Statut
        
        layout.addWidget(self.table)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.ajouter_btn = QPushButton("Ajouter")
        self.ajouter_btn.clicked.connect(self.on_ajouter)
        buttons_layout.addWidget(self.ajouter_btn)
        
        self.modifier_btn = QPushButton("Modifier")
        self.modifier_btn.clicked.connect(self.on_modifier)
        self.modifier_btn.setEnabled(False)
        buttons_layout.addWidget(self.modifier_btn)
        
        self.supprimer_btn = QPushButton("Supprimer")
        self.supprimer_btn.clicked.connect(self.on_supprimer)
        self.supprimer_btn.setEnabled(False)
        buttons_layout.addWidget(self.supprimer_btn)
        
        self.paiement_btn = QPushButton("Enregistrer paiement")
        self.paiement_btn.clicked.connect(self.on_enregistrer_paiement)
        self.paiement_btn.setEnabled(False)
        buttons_layout.addWidget(self.paiement_btn)
        
        self.fiche_btn = QPushButton("Fiche élève")
        self.fiche_btn.clicked.connect(self.on_fiche_eleve)
        self.fiche_btn.setEnabled(False)
        buttons_layout.addWidget(self.fiche_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Connexion du signal de sélection
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Connexion du signal de double-clic
        self.table.doubleClicked.connect(self.on_double_click)
    
    def charger_donnees(self):
        """Charge les données depuis le service."""
        try:
            # Charge les classes pour le filtre
            classes = self.service.lister_classes()
            self.classe_combo.clear()
            self.classe_combo.addItem("Toutes les classes")
            self.classe_combo.addItems(classes)
            
            # Charge les élèves
            self.apply_filters()
        except ValidationError as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def apply_filters(self):
        """Applique les filtres de recherche et de classe."""
        try:
            eleves = self.service.lister_eleves(
                recherche=self.current_search,
                classe=self.current_classe_filter
            )
            self.model.set_eleves(eleves)
        except ValidationError as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def on_search_changed(self, text):
        """
        Gère le changement de texte de recherche.
        
        Args:
            text: Nouveau texte de recherche
        """
        self.current_search = text if text.strip() else None
        self.apply_filters()
    
    def on_classe_changed(self, index):
        """
        Gère le changement de filtre de classe.
        
        Args:
            index: Index sélectionné dans le combo
        """
        if index == 0:
            self.current_classe_filter = None
        else:
            self.current_classe_filter = self.classe_combo.currentText()
        self.apply_filters()
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans la table."""
        has_selection = self.table.selectionModel().hasSelection()
        self.modifier_btn.setEnabled(has_selection)
        self.supprimer_btn.setEnabled(has_selection)
        self.paiement_btn.setEnabled(has_selection)
        self.fiche_btn.setEnabled(has_selection)
    
    def on_ajouter(self):
        """Gère le clic sur le bouton Ajouter."""
        classes = self.service.lister_classes()
        dialog = EleveFormDialog(self, classes_disponibles=classes)
        
        if dialog.exec() == QDialog.Accepted:
            donnees = dialog.get_donnees()
            try:
                self.service.ajouter_eleve(
                    donnees['nom'],
                    donnees['prenom'],
                    donnees['classe'],
                    donnees['annee_scolaire'],
                    donnees['total_du']
                )
                QMessageBox.information(self, "Succès", "L'élève a été ajouté avec succès.")
                self.charger_donnees()
                
                # Rafraîchit le tableau de bord
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_modifier(self):
        """Gère le clic sur le bouton Modifier."""
        # Récupère l'élève sélectionné
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
        # Récupère les données de l'élève
        eleve = self.service.obtenir_eleve(eleve_id)
        if not eleve:
            QMessageBox.critical(self, "Erreur", "Élève introuvable.")
            return
        
        classes = self.service.lister_classes()
        dialog = EleveFormDialog(self, eleve_data=eleve, classes_disponibles=classes)
        
        if dialog.exec() == QDialog.Accepted:
            donnees = dialog.get_donnees()
            try:
                self.service.modifier_eleve(
                    eleve_id,
                    donnees['nom'],
                    donnees['prenom'],
                    donnees['classe'],
                    donnees['annee_scolaire'],
                    donnees['total_du']
                )
                QMessageBox.information(self, "Succès", "L'élève a été modifié avec succès.")
                self.charger_donnees()
                
                # Rafraîchit le tableau de bord
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_supprimer(self):
        """Gère le clic sur le bouton Supprimer."""
        # Récupère l'élève sélectionné
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
        # Récupère les données de l'élève pour l'affichage
        eleve = self.service.obtenir_eleve(eleve_id)
        if not eleve:
            QMessageBox.critical(self, "Erreur", "Élève introuvable.")
            return
        
        # Confirmation
        reponse = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer l'élève {eleve['nom']} {eleve['prenom']} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            try:
                self.service.supprimer_eleve(eleve_id)
                QMessageBox.information(self, "Succès", "L'élève a été supprimé avec succès.")
                self.charger_donnees()
                
                # Rafraîchit le tableau de bord
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_enregistrer_paiement(self):
        """Gère le clic sur le bouton Enregistrer paiement."""
        from ui.paiement_dialog import PaiementDialog
        
        # Récupère l'élève sélectionné
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
        # Récupère les données de l'élève
        eleve = self.service.obtenir_eleve(eleve_id)
        if not eleve:
            QMessageBox.critical(self, "Erreur", "Élève introuvable.")
            return
        
        # Ouvre le dialogue de paiement
        paiement_service = PaiementService()
        dialog = PaiementDialog(self, eleve_id=eleve_id, eleve_data=eleve)
        
        if dialog.exec() == QDialog.Accepted:
            donnees = dialog.get_donnees()
            try:
                numero_recu, solde_apres = paiement_service.enregistrer_paiement(
                    eleve_id,
                    donnees['montant'],
                    donnees['date'],
                    donnees['mode']
                )
                solde_formate = SoldeService.formater_monnaie_fcfa(solde_apres)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Paiement enregistré avec succès !\n\n"
                    f"Numéro de reçu : {numero_recu}\n"
                    f"Solde restant : {solde_formate}"
                )
                
                # Propose de générer le reçu PDF
                reponse = QMessageBox.question(
                    self,
                    "Reçu",
                    "Voulez-vous générer le reçu PDF maintenant ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reponse == QMessageBox.Yes:
                    try:
                        recu_service = RecuService()
                        donnees_recu = recu_service.obtenir_donnees_recu_par_numero(numero_recu)
                        chemin_pdf = generer_recu_pdf(donnees_recu)
                        
                        # Ouvre le PDF avec l'application par défaut
                        QDesktopServices.openUrl(QUrl.fromLocalFile(chemin_pdf))
                        
                        QMessageBox.information(
                            self,
                            "Reçu généré",
                            f"Le reçu a été généré :\n{chemin_pdf}"
                        )
                    except Exception as e:
                        QMessageBox.critical(self, "Erreur", str(e))
                
                self.charger_donnees()
                
                # Rafraîchit le tableau de bord
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_fiche_eleve(self):
        """Gère le clic sur le bouton Fiche élève."""
        self.ouvrir_fiche_eleve()
    
    def on_double_click(self, index):
        """
        Gère le double-clic sur un élève.
        
        Args:
            index: Index de la cellule cliquée
        """
        self.ouvrir_fiche_eleve()
    
    def ouvrir_fiche_eleve(self):
        """Ouvre la fiche détaillée de l'élève sélectionné."""
        # Récupère l'élève sélectionné
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
        # Ouvre la fiche élève
        dialog = FicheEleveDialog(self, eleve_id=eleve_id, main_window=self.main_window)
        dialog.exec()
        
        # Rafraîchit les données après fermeture de la fiche
        self.charger_donnees()
