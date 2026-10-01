"""
Dialogue de formulaire pour l'enregistrement de paiements.
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QDialogButtonBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIntValidator
from datetime import datetime
from services.paiement_service import PaiementService
from services.solde_service import SoldeService
from services.eleve_service import EleveService


class PaiementDialog(QDialog):
    """Dialogue pour enregistrer un paiement."""
    
    def __init__(self, parent=None, eleve_id=None, eleve_data=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Widget parent
            eleve_id: ID de l'élève
            eleve_data: Dictionnaire avec les données de l'élève
        """
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.eleve_data = eleve_data
        self.service = PaiementService()
        self.eleve_service = EleveService()
        
        self.setup_ui()
        self.remplir_donnees()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.setMinimumWidth(450)
        
        layout = QFormLayout(self)
        
        # Informations de l'élève (lecture seule)
        if self.eleve_data:
            info_label = QLabel(f"Élève : {self.eleve_data['nom']} {self.eleve_data['prenom']}")
            info_label.setStyleSheet("font-weight: bold; color: #333;")
            layout.addRow(info_label)
            
            # Affiche le solde restant
            total_du_fcfa = self.eleve_data['total_du']
            total_paye_fcfa = self.eleve_data.get('total_paye', 0)
            solde_actuel = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa)
            solde_formate = SoldeService.formater_monnaie_fcfa(solde_actuel)
            
            solde_label = QLabel(f"Solde restant : {solde_formate}")
            solde_label.setStyleSheet("color: #0066cc; font-weight: bold;")
            layout.addRow(solde_label)
            
            layout.addRow(QLabel(""))  # Espace
        
        # Champ montant
        self.montant_spin = QSpinBox()
        self.montant_spin.setRange(1, 999999999)
        self.montant_spin.setSingleStep(1000)
        self.montant_spin.setSuffix(" FCFA")
        self.montant_spin.setValue(10000)
        layout.addRow("Montant *:", self.montant_spin)
        
        # Champ date
        from PySide6.QtWidgets import QDateEdit
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMaximumDate(QDate.currentDate())
        layout.addRow("Date *:", self.date_edit)
        
        # Champ mode
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(PaiementService.MODES_PAIEMENT)
        layout.addRow("Mode *:", self.mode_combo)
        
        # Boutons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
    
    def remplir_donnees(self):
        """Remplit les champs avec les données si disponibles."""
        if self.eleve_data:
            # Le solde maximum ne peut pas dépasser le solde actuel
            total_du_fcfa = self.eleve_data['total_du']
            total_paye_fcfa = self.eleve_data.get('total_paye', 0)
            solde_actuel = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa)
            
            # Limite le montant au solde restant
            self.montant_spin.setMaximum(solde_actuel)
    
    def get_donnees(self):
        """
        Récupère les données du formulaire.
        
        Returns:
            dict: Dictionnaire avec les données du formulaire
        """
        qdate = self.date_edit.date()
        date_str = qdate.toString("yyyy-MM-dd")
        
        return {
            'montant': self.montant_spin.value(),
            'date': date_str,
            'mode': self.mode_combo.currentText()
        }
    
    def validate(self):
        """
        Valide le formulaire.
        
        Returns:
            bool: True si le formulaire est valide, False sinon
        """
        donnees = self.get_donnees()
        
        if donnees['montant'] <= 0:
            QMessageBox.warning(self, "Validation", "Le montant doit être strictement positif.")
            self.montant_spin.setFocus()
            return False
        
        # Vérifie que le montant ne dépasse pas le solde
        if self.eleve_data:
            total_du_fcfa = self.eleve_data['total_du']
            total_paye_fcfa = self.eleve_data.get('total_paye', 0)
            solde_actuel = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa)
            montant_fcfa = donnees['montant']
            
            if montant_fcfa > solde_actuel:
                solde_formate = SoldeService.formater_monnaie_fcfa(solde_actuel)
                QMessageBox.warning(
                    self, "Validation",
                    f"Le montant dépasse le solde restant ({solde_formate})."
                )
                self.montant_spin.setFocus()
                return False
        
        return True
    
    def accept(self):
        """Surcharge de accept pour valider avant de fermer."""
        if self.validate():
            super().accept()
