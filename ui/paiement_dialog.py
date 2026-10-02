"""
Dialogue de formulaire pour l'enregistrement de paiements.
Fournit une saisie rapide avec boutons de raccourci de montant (totalité, 50%)
et calcul dynamique en temps réel du solde restant.
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QDialogButtonBox, QMessageBox, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
from services.paiement_service import PaiementService
from services.solde_service import SoldeService
from services.eleve_service import EleveService


class PaiementDialog(QDialog):
    """Dialogue moderne pour enregistrer un paiement."""
    
    def __init__(self, parent=None, eleve_id=None, eleve_data=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.eleve_data = eleve_data
        self.service = PaiementService()
        self.eleve_service = EleveService()
        self.solde_actuel = 0
        
        self.setup_ui()
        self.remplir_donnees()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.setWindowTitle("Enregistrer un paiement - EduPaie")
        self.setMinimumWidth(480)
        
        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(14)
        root_layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = QLabel("💳 Enregistrement d'un Versement Scolaire")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A8A;")
        root_layout.addWidget(header)
        
        # Carte récapitulative de l'élève
        if self.eleve_data:
            total_du_fcfa = self.eleve_data['total_du']
            total_paye_fcfa = self.eleve_data.get('total_paye', 0)
            self.solde_actuel = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa)
            
            recap_frame = QFrame()
            recap_frame.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            recap_layout = QVBoxLayout(recap_frame)
            
            nom_label = QLabel(f"👤 <b>Élève :</b> {self.eleve_data['nom']} {self.eleve_data['prenom']} ({self.eleve_data.get('classe', '')})")
            nom_label.setStyleSheet("font-size: 13px; color: #1E293B;")
            recap_layout.addWidget(nom_label)
            
            stats_layout = QHBoxLayout()
            du_txt = QLabel(f"Total dû : <b>{SoldeService.formater_monnaie_fcfa(total_du_fcfa)}</b>")
            paye_txt = QLabel(f"Déjà versé : <b style='color:#059669;'>{SoldeService.formater_monnaie_fcfa(total_paye_fcfa)}</b>")
            stats_layout.addWidget(du_txt)
            stats_layout.addWidget(paye_txt)
            recap_layout.addLayout(stats_layout)
            
            self.solde_label = QLabel(f"Solde actuel restant : <b style='color:#DC2626; font-size:14px;'>{SoldeService.formater_monnaie_fcfa(self.solde_actuel)}</b>")
            recap_layout.addWidget(self.solde_label)
            
            root_layout.addWidget(recap_frame)
        
        # Formulaire de paiement
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Champ montant
        self.montant_spin = QSpinBox()
        self.montant_spin.setRange(1, 999999999)
        self.montant_spin.setSingleStep(5000)
        self.montant_spin.setSuffix(" FCFA")
        self.montant_spin.setValue(min(25000, self.solde_actuel if self.solde_actuel > 0 else 10000))
        self.montant_spin.valueChanged.connect(self.actualiser_previsualisation_solde)
        form_layout.addRow("Montant versé * :", self.montant_spin)
        
        # Raccourcis de montant rapide
        if self.eleve_data and self.solde_actuel > 0:
            shortcuts_layout = QHBoxLayout()
            shortcuts_layout.setSpacing(6)
            
            btn_tout = QPushButton("Payer tout le solde")
            btn_tout.setProperty("variant", "secondary")
            btn_tout.setStyleSheet("font-size: 11px; padding: 4px 8px;")
            btn_tout.clicked.connect(lambda: self.montant_spin.setValue(self.solde_actuel))
            shortcuts_layout.addWidget(btn_tout)
            
            if self.solde_actuel >= 20000:
                btn_moitie = QPushButton("50% du solde")
                btn_moitie.setProperty("variant", "secondary")
                btn_moitie.setStyleSheet("font-size: 11px; padding: 4px 8px;")
                btn_moitie.clicked.connect(lambda: self.montant_spin.setValue(self.solde_actuel // 2))
                shortcuts_layout.addWidget(btn_moitie)
            
            shortcuts_layout.addStretch()
            form_layout.addRow("", shortcuts_layout)
        
        # Champ date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMaximumDate(QDate.currentDate())
        form_layout.addRow("Date de paiement * :", self.date_edit)
        
        # Champ mode
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(PaiementService.MODES_PAIEMENT)
        form_layout.addRow("Mode de paiement * :", self.mode_combo)
        
        root_layout.addWidget(form_frame)
        
        # Indicateur dynamique du solde après paiement
        self.apercu_solde_label = QLabel()
        self.apercu_solde_label.setStyleSheet("""
            padding: 8px 12px;
            border-radius: 6px;
            background-color: #F1F5F9;
            color: #334155;
            font-size: 13px;
        """)
        root_layout.addWidget(self.apercu_solde_label)
        self.actualiser_previsualisation_solde()
        
        # Boutons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        self.buttons.button(QDialogButtonBox.Ok).setText("Valider le paiement")
        self.buttons.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        root_layout.addWidget(self.buttons)
    
    def remplir_donnees(self):
        """Remplit les champs avec les données si disponibles."""
        if self.eleve_data:
            total_du_fcfa = self.eleve_data['total_du']
            total_paye_fcfa = self.eleve_data.get('total_paye', 0)
            solde = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa)
            self.solde_actuel = solde
            if solde > 0:
                self.montant_spin.setMaximum(solde)
                self.montant_spin.setValue(min(self.montant_spin.value(), solde))
        self.actualiser_previsualisation_solde()
    
    def actualiser_previsualisation_solde(self):
        """Met à jour l'affichage prévisionnel du solde restant."""
        if not self.eleve_data:
            self.apercu_solde_label.setVisible(False)
            return
        
        montant = self.montant_spin.value()
        solde_previsionnel = max(0, self.solde_actuel - montant)
        
        if solde_previsionnel == 0:
            self.apercu_solde_label.setText(
                "✨ <b>Excellent !</b> Ce paiement soldera intégralement le compte de l'élève."
            )
            self.apercu_solde_label.setStyleSheet("""
                padding: 8px 12px;
                border-radius: 6px;
                background-color: #DCFCE7;
                color: #166534;
                font-size: 13px;
                border: 1px solid #86EFAC;
            """)
        else:
            txt = SoldeService.formater_monnaie_fcfa(solde_previsionnel)
            self.apercu_solde_label.setText(
                f"ℹ️ Solde restant après ce versement : <b>{txt}</b>"
            )
            self.apercu_solde_label.setStyleSheet("""
                padding: 8px 12px;
                border-radius: 6px;
                background-color: #F8FAFC;
                color: #334155;
                font-size: 13px;
                border: 1px solid #E2E8F0;
            """)
    
    def get_donnees(self):
        """Récupère les données du formulaire."""
        qdate = self.date_edit.date()
        date_str = qdate.toString("yyyy-MM-dd")
        
        return {
            'montant': self.montant_spin.value(),
            'date': date_str,
            'mode': self.mode_combo.currentText()
        }
    
    def validate(self):
        """Valide le formulaire."""
        donnees = self.get_donnees()
        
        if donnees['montant'] <= 0:
            QMessageBox.warning(self, "Validation", "Le montant doit être strictement positif.")
            self.montant_spin.setFocus()
            return False
        
        if self.eleve_data:
            total_du_fcfa = self.eleve_data['total_du']
            total_paye_fcfa = self.eleve_data.get('total_paye', 0)
            solde = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa)
            montant_fcfa = donnees['montant']
            
            if montant_fcfa > solde:
                solde_formate = SoldeService.formater_monnaie_fcfa(solde)
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
