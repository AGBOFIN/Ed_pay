"""
Widget pour la gestion des élèves.
Affiche la liste des élèves avec recherche en temps réel, filtrage par classe,
export CSV, menu contextuel et gestion complète des paiements et fiches.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QHeaderView, QDialog,
    QLabel, QMenu, QFileDialog
)
from PySide6.QtCore import Qt, QAbstractTableModel, QUrl
from PySide6.QtGui import QColor, QBrush, QDesktopServices, QFont, QAction
from services.eleve_service import EleveService, ValidationError
from services.solde_service import SoldeService
from services.paiement_service import PaiementService
from services.recu_service import RecuService
# Import direct pour éviter l'import via services/__init__.py
from services.recu_pdf import generer_recu_pdf
from services.export_service import ExportService
from ui.eleve_form_dialog import EleveFormDialog
from ui.fiche_eleve_dialog import FicheEleveDialog


class ElevesTableModel(QAbstractTableModel):
    """Modèle de table pour afficher les élèves."""
    
    def __init__(self, eleves=None, parent=None):
        super().__init__(parent)
        self.eleves = eleves or []
        self.headers = ["ID", "Nom", "Prénom", "Classe", "Année scolaire", "Total dû (FCFA)", "Payé (FCFA)", "Solde (FCFA)", "Statut"]
    
    def rowCount(self, parent=None):
        return len(self.eleves)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        eleve = self.eleves[index.row()]
        col = index.column()
        
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
                return SoldeService.formater_monnaie_fcfa(total_du_fcfa)
            elif col == 6:
                return SoldeService.formater_monnaie_fcfa(total_paye)
            elif col == 7:
                solde = SoldeService.calculer_solde(total_du_fcfa, total_paye)
                return SoldeService.formater_monnaie_fcfa(solde)
            elif col == 8:
                return SoldeService.determiner_statut(total_du_fcfa, total_paye)
        
        elif role == Qt.TextAlignmentRole:
            if col in (5, 6, 7):
                return Qt.AlignRight | Qt.AlignVCenter
            elif col in (0, 3, 4, 8):
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        
        elif role == Qt.BackgroundRole and col == 8:
            statut = SoldeService.determiner_statut(total_du_fcfa, total_paye)
            if statut == "Soldé":
                return QBrush(QColor(220, 252, 231))
            elif statut == "Partiellement payé":
                return QBrush(QColor(254, 243, 199))
            else:
                return QBrush(QColor(254, 226, 226))
        
        elif role == Qt.ForegroundRole:
            if col == 8:
                statut = SoldeService.determiner_statut(total_du_fcfa, total_paye)
                if statut == "Soldé":
                    return QBrush(QColor(22, 101, 52))
                elif statut == "Partiellement payé":
                    return QBrush(QColor(146, 64, 14))
                else:
                    return QBrush(QColor(153, 27, 27))
            elif col == 6:
                return QBrush(QColor(5, 150, 105))  # Vert pour montant payé
            elif col == 7:
                solde = SoldeService.calculer_solde(total_du_fcfa, total_paye)
                if solde > 0:
                    return QBrush(QColor(220, 38, 38))  # Rouge pour solde restant
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def set_eleves(self, eleves):
        self.beginResetModel()
        self.eleves = eleves
        self.endResetModel()
    
    def get_eleve_id(self, index):
        if index.isValid() and index.row() < len(self.eleves):
            return self.eleves[index.row()]['id']
        return None


class ElevesWidget(QWidget):
    """Widget principal pour la gestion des élèves."""
    
    def __init__(self, parent=None, main_window=None):
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
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # En-tête
        layout.addLayout(self._creer_entete())
        
        # Barre de recherche et filtres
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)
        
        # Recherche
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Rechercher par nom ou prénom... (Ctrl+F)")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setMinimumWidth(280)
        self.search_edit.textChanged.connect(self.on_search_changed)
        filters_layout.addWidget(self.search_edit)
        
        # Filtre classe
        classe_label = QLabel("Classe :")
        classe_label.setStyleSheet("font-weight: 600; color: #475569;")
        filters_layout.addWidget(classe_label)
        
        self.classe_combo = QComboBox()
        self.classe_combo.addItem("Toutes les classes")
        self.classe_combo.currentIndexChanged.connect(self.on_classe_changed)
        filters_layout.addWidget(self.classe_combo)
        
        filters_layout.addStretch()
        
        # Compteur d'élèves
        self.compteur_label = QLabel("0 élève(s)")
        self.compteur_label.setStyleSheet("color: #64748B; font-weight: 500; font-size: 12px;")
        filters_layout.addWidget(self.compteur_label)
        
        # Bouton export CSV
        self.exporter_btn = QPushButton("📥 Exporter CSV")
        self.exporter_btn.setProperty("variant", "secondary")
        self.exporter_btn.setToolTip("Exporter la sélection courante au format CSV (Excel)")
        self.exporter_btn.clicked.connect(self.exporter_csv)
        filters_layout.addWidget(self.exporter_btn)
        
        layout.addLayout(filters_layout)
        
        # Table des élèves
        self.table = QTableView()
        self.model = ElevesTableModel()
        self.table.setModel(self.model)
        
        # Configuration de la table
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.ouvrir_menu_contextuel)
        
        # Ajustement des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nom
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Prénom
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Classe
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Année
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Total dû
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Payé
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Solde
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Statut
        
        layout.addWidget(self.table)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.ajouter_btn = QPushButton("➕ Ajouter un élève")
        self.ajouter_btn.setToolTip("Ajouter un nouvel élève (Ctrl+N)")
        self.ajouter_btn.clicked.connect(self.on_ajouter)
        buttons_layout.addWidget(self.ajouter_btn)
        
        self.modifier_btn = QPushButton("✏️ Modifier")
        self.modifier_btn.setProperty("variant", "secondary")
        self.modifier_btn.clicked.connect(self.on_modifier)
        self.modifier_btn.setEnabled(False)
        buttons_layout.addWidget(self.modifier_btn)
        
        self.supprimer_btn = QPushButton("🗑️ Supprimer")
        self.supprimer_btn.setProperty("variant", "danger")
        self.supprimer_btn.clicked.connect(self.on_supprimer)
        self.supprimer_btn.setEnabled(False)
        buttons_layout.addWidget(self.supprimer_btn)
        
        buttons_layout.addSpacing(15)
        
        self.paiement_btn = QPushButton("💳 Enregistrer paiement")
        self.paiement_btn.setProperty("variant", "success")
        self.paiement_btn.setToolTip("Enregistrer un nouveau paiement pour l'élève sélectionné (Ctrl+P)")
        self.paiement_btn.clicked.connect(self.on_enregistrer_paiement)
        self.paiement_btn.setEnabled(False)
        buttons_layout.addWidget(self.paiement_btn)
        
        self.fiche_btn = QPushButton("📄 Fiche élève")
        self.fiche_btn.setProperty("variant", "secondary")
        self.fiche_btn.setToolTip("Ouvrir la fiche financière et l'historique complet")
        self.fiche_btn.clicked.connect(self.on_fiche_eleve)
        self.fiche_btn.setEnabled(False)
        buttons_layout.addWidget(self.fiche_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Connexion des signaux
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.on_double_click)
    
    def _creer_entete(self):
        """Crée l'en-tête de la page Élèves."""
        layout = QHBoxLayout()
        
        titre_box = QVBoxLayout()
        titre = QLabel("👥 Gestion des Élèves et Scolarités")
        titre.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A;")
        
        soustitre = QLabel("Inscriptions, suivi des états de compte et édition des fiches financières")
        soustitre.setStyleSheet("font-size: 13px; color: #64748B;")
        
        titre_box.addWidget(titre)
        titre_box.addWidget(soustitre)
        layout.addLayout(titre_box)
        layout.addStretch()
        
        return layout
    
    def charger_donnees(self):
        """Charge les données depuis le service."""
        try:
            classes = self.service.lister_classes()
            self.classe_combo.blockSignals(True)
            current = self.classe_combo.currentText()
            self.classe_combo.clear()
            self.classe_combo.addItem("Toutes les classes")
            self.classe_combo.addItems(classes)
            idx = self.classe_combo.findText(current)
            if idx >= 0:
                self.classe_combo.setCurrentIndex(idx)
            self.classe_combo.blockSignals(False)
            
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
            self.compteur_label.setText(f"{len(eleves)} élève(s) affiché(s)")
        except ValidationError as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def on_search_changed(self, text):
        """Gère le changement de texte de recherche."""
        self.current_search = text if text.strip() else None
        self.apply_filters()
    
    def on_classe_changed(self, index):
        """Gère le changement de filtre de classe."""
        if index <= 0:
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
    
    def ouvrir_menu_contextuel(self, pos):
        """Affiche un menu contextuel au clic droit sur une ligne."""
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        
        self.table.selectRow(index.row())
        
        menu = QMenu(self)
        action_fiche = menu.addAction("📄 Voir la fiche élève")
        action_paiement = menu.addAction("💳 Enregistrer un paiement")
        menu.addSeparator()
        action_modifier = menu.addAction("✏️ Modifier l'élève")
        action_supprimer = menu.addAction("🗑️ Supprimer l'élève")
        
        action_fiche.triggered.connect(self.on_fiche_eleve)
        action_paiement.triggered.connect(self.on_enregistrer_paiement)
        action_modifier.triggered.connect(self.on_modifier)
        action_supprimer.triggered.connect(self.on_supprimer)
        
        menu.exec(self.table.viewport().mapToGlobal(pos))
    
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
                
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_modifier(self):
        """Gère le clic sur le bouton Modifier."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
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
                
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_supprimer(self):
        """Gère le clic sur le bouton Supprimer."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
        eleve = self.service.obtenir_eleve(eleve_id)
        if not eleve:
            QMessageBox.critical(self, "Erreur", "Élève introuvable.")
            return
        
        reponse = QMessageBox.question(
            self,
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer l'élève {eleve['nom']} {eleve['prenom']} ({eleve['classe']}) ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            try:
                self.service.supprimer_eleve(eleve_id)
                QMessageBox.information(self, "Succès", "L'élève a été supprimé avec succès.")
                self.charger_donnees()
                
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_enregistrer_paiement(self):
        """Gère le clic sur le bouton Enregistrer paiement."""
        from ui.paiement_dialog import PaiementDialog
        
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
        eleve = self.service.obtenir_eleve(eleve_id)
        if not eleve:
            QMessageBox.critical(self, "Erreur", "Élève introuvable.")
            return
        
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
                
                reponse = QMessageBox.question(
                    self,
                    "Reçu PDF",
                    "Voulez-vous générer et afficher le reçu PDF maintenant ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reponse == QMessageBox.Yes:
                    try:
                        recu_service = RecuService()
                        donnees_recu = recu_service.obtenir_donnees_recu_par_numero(numero_recu)
                        chemin_pdf = generer_recu_pdf(donnees_recu)
                        
                        QDesktopServices.openUrl(QUrl.fromLocalFile(chemin_pdf))
                        QMessageBox.information(
                            self,
                            "Reçu généré",
                            f"Le reçu a été généré :\n{chemin_pdf}"
                        )
                    except Exception as e:
                        QMessageBox.critical(self, "Erreur", str(e))
                
                self.charger_donnees()
                
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def on_fiche_eleve(self):
        """Gère le clic sur le bouton Fiche élève."""
        self.ouvrir_fiche_eleve()
    
    def on_double_click(self, index):
        """Gère le double-clic sur un élève."""
        self.ouvrir_fiche_eleve()
    
    def ouvrir_fiche_eleve(self):
        """Ouvre la fiche détaillée de l'élève sélectionné."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        index = selected[0]
        eleve_id = self.model.get_eleve_id(index)
        
        dialog = FicheEleveDialog(self, eleve_id=eleve_id, main_window=self.main_window)
        dialog.exec()
        
        self.charger_donnees()
    
    def exporter_csv(self):
        """Exporte la liste courante des élèves au format CSV."""
        if not self.model.eleves:
            QMessageBox.information(self, "Export", "Aucun élève à exporter.")
            return
        
        chemin, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les élèves en CSV",
            "edupaie_eleves.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        if chemin:
            try:
                nb = ExportService.exporter_eleves_csv(self.model.eleves, chemin)
                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"{nb} élève(s) exporté(s) avec succès dans :\n{chemin}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'export", str(e))
