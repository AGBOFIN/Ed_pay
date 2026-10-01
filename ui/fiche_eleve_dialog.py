"""
Dialogue de fiche détaillée d'un élève avec historique des paiements.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QHeaderView, QDialogButtonBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QBrush, QDesktopServices
from services.fiche_eleve_service import FicheEleveService
from services.solde_service import SoldeService
from services.paiement_service import PaiementService
from services.recu_service import RecuService
from services.recu_pdf import generer_recu_pdf


class FicheEleveDialog(QDialog):
    """Dialogue pour afficher la fiche détaillée d'un élève."""
    
    def __init__(self, parent=None, eleve_id=None, main_window=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Widget parent
            eleve_id: ID de l'élève
            main_window: Référence à la fenêtre principale pour le rafraîchissement
        """
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.fiche_service = FicheEleveService()
        self.paiement_service = PaiementService()
        self.recu_service = RecuService()
        self.main_window = main_window
        
        self.donnees_fiche = None
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.setWindowTitle("Fiche Élève")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Section identité de l'élève
        identite_layout = self._creer_section_identite()
        layout.addLayout(identite_layout)
        
        # Ligne de séparation
        layout.addWidget(self._creer_separation())
        
        # Tableau des paiements
        table_layout = self._creer_section_paiements()
        layout.addLayout(table_layout)
        
        # Boutons d'action
        buttons_layout = self._creer_section_boutons()
        layout.addLayout(buttons_layout)
        
        # Bouton de fermeture
        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
    
    def _creer_section_identite(self):
        """Crée la section d'identité de l'élève."""
        layout = QVBoxLayout()
        
        # Nom et prénom
        self.nom_prenom_label = QLabel()
        self.nom_prenom_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(self.nom_prenom_label)
        
        # Classe et année scolaire
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(self.info_label)
        
        # Statistiques financières
        stats_layout = QHBoxLayout()
        
        self.total_du_label = QLabel()
        self.total_du_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.total_du_label)
        
        self.total_paye_label = QLabel()
        self.total_paye_label.setStyleSheet("font-size: 14px; color: #0066cc;")
        stats_layout.addWidget(self.total_paye_label)
        
        self.solde_label = QLabel()
        self.solde_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.solde_label)
        
        self.statut_label = QLabel()
        self.statut_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px 10px; border-radius: 4px;")
        stats_layout.addWidget(self.statut_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        layout.addStretch()
        return layout
    
    def _creer_separation(self):
        """Crée une ligne de séparation."""
        from PySide6.QtWidgets import QFrame
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        return frame
    
    def _creer_section_paiements(self):
        """Crée la section du tableau des paiements."""
        layout = QVBoxLayout()
        
        # Titre
        titre_label = QLabel("Historique des paiements")
        titre_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(titre_label)
        
        # Table des paiements
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Montant (FCFA)", "Mode", "N° Reçu", "Solde après (FCFA)"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Configuration des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Montant
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Mode
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # N° Reçu
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Solde après
        
        layout.addWidget(self.table)
        
        # Message si aucun paiement
        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-style: italic; color: #999; padding: 20px;")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setText("Aucun paiement enregistré")
        self.message_label.setVisible(False)
        layout.addWidget(self.message_label)
        
        return layout
    
    def _creer_section_boutons(self):
        """Crée la section des boutons d'action."""
        layout = QHBoxLayout()
        
        self.voir_recu_btn = QPushButton("Voir / Ré-imprimer le reçu")
        self.voir_recu_btn.clicked.connect(self.on_voir_recu)
        self.voir_recu_btn.setEnabled(False)
        layout.addWidget(self.voir_recu_btn)
        
        self.enregistrer_paiement_btn = QPushButton("Enregistrer un paiement")
        self.enregistrer_paiement_btn.clicked.connect(self.on_enregistrer_paiement)
        layout.addWidget(self.enregistrer_paiement_btn)
        
        layout.addStretch()
        return layout
    
    def charger_donnees(self):
        """Charge les données de la fiche depuis le service."""
        try:
            self.donnees_fiche = self.fiche_service.obtenir_donnees_fiche(self.eleve_id)
            self.mettre_a_jour_identite()
            self.mettre_a_jour_paiements()
            self.mettre_a_jour_statistiques()
        except ValidationError as e:
            QMessageBox.critical(self, "Erreur", str(e))
            self.reject()
    
    def mettre_a_jour_identite(self):
        """Met à jour la section d'identité de l'élève."""
        eleve = self.donnees_fiche['eleve']
        
        # Nom et prénom
        self.nom_prenom_label.setText(f"{eleve['nom']} {eleve['prenom']}")
        
        # Classe et année scolaire
        self.info_label.setText(f"Classe : {eleve['classe']} - Année scolaire : {eleve['annee_scolaire']}")
        
        # Statistiques financières
        total_du_fcfa = self.donnees_fiche['total_du']
        self.total_du_label.setText(f"Total dû : {SoldeService.formater_monnaie_fcfa(total_du_fcfa)}")
        
        total_paye_fcfa = self.donnees_fiche['total_paye']
        self.total_paye_label.setText(f"Payé : {SoldeService.formater_monnaie_fcfa(total_paye_fcfa)}")
        
        solde_fcfa = self.donnees_fiche['solde']
        self.solde_label.setText(f"Solde : {SoldeService.formater_monnaie_fcfa(solde_fcfa)}")
        
        statut = self.donnees_fiche['statut']
        self.statut_label.setText(statut)
        
        # Couleur de fond selon le statut
        if statut == "Soldé":
            self.statut_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px 10px; border-radius: 4px; background-color: #90EE90;")
        elif statut == "Partiellement payé":
            self.statut_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px 10px; border-radius: 4px; background-color: #FFC864;")
        else:  # Non payé
            self.statut_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px 10px; border-radius: 4px; background-color: #FFB6B6;")
    
    def mettre_a_jour_paiements(self):
        """Met à jour le tableau des paiements."""
        paiements = self.donnees_fiche['paiements']
        
        if not paiements:
            self.table.setVisible(False)
            self.message_label.setVisible(True)
            return
        
        self.table.setVisible(True)
        self.message_label.setVisible(False)
        self.table.setRowCount(len(paiements))
        
        for row, paiement in enumerate(paiements):
            # Date
            date_formatee = self._formater_date(paiement['date'])
            self.table.setItem(row, 0, QTableWidgetItem(date_formatee))
            
            # Montant
            montant = paiement['montant']
            self.table.setItem(row, 1, QTableWidgetItem(f"{montant:.2f}"))
            
            # Mode
            self.table.setItem(row, 2, QTableWidgetItem(paiement['mode']))
            
            # Numéro de reçu
            self.table.setItem(row, 3, QTableWidgetItem(paiement['numero_recu']))
            
            # Solde après
            solde_apres_fcfa = paiement['solde_apres']
            self.table.setItem(row, 4, QTableWidgetItem(SoldeService.formater_monnaie_fcfa(solde_apres_fcfa)))
    
    def mettre_a_jour_statistiques(self):
        """Met à jour les statistiques après chargement."""
        # Les statistiques sont déjà mises à jour dans mettre_a_jour_identite
        pass
    
    def _formater_date(self, date_str):
        """Formate une date pour l'affichage."""
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
        else:
            date_part = date_str
        
        try:
            annee, mois, jour = date_part.split('-')
            return f"{jour}/{mois}/{annee}"
        except:
            return date_str
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans le tableau."""
        has_selection = self.table.selectionModel().hasSelection()
        self.voir_recu_btn.setEnabled(has_selection)
    
    def on_voir_recu(self):
        """Gère le clic sur le bouton Voir / Ré-imprimer le reçu."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        
        row = selected[0].row()
        paiement = self.donnees_fiche['paiements'][row]
        
        try:
            donnees_recu = self.recu_service.obtenir_donnees_recu_par_numero(paiement['numero_recu'])
            chemin_pdf = generer_recu_pdf(donnees_recu)
            
            # Ouvre le PDF
            QDesktopServices.openUrl(QUrl.fromLocalFile(chemin_pdf))
            
            QMessageBox.information(
                self,
                "Reçu généré",
                f"Le reçu a été généré :\n{chemin_pdf}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du reçu : {str(e)}")
    
    def on_enregistrer_paiement(self):
        """Gère le clic sur le bouton Enregistrer un paiement."""
        from ui.paiement_dialog import PaiementDialog
        
        eleve = self.donnees_fiche['eleve']
        
        dialog = PaiementDialog(self, eleve_id=self.eleve_id, eleve_data=eleve)
        
        if dialog.exec() == QDialog.Accepted:
            donnees = dialog.get_donnees()
            try:
                numero_recu, solde_apres = self.paiement_service.enregistrer_paiement(
                    self.eleve_id,
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
                
                # Rafraîchit les données
                self.charger_donnees()
                
                # Rafraîchit le tableau de bord
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
