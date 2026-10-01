"""
Dialogue de formulaire pour l'ajout et la modification d'élèves.
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox,
    QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt


class EleveFormDialog(QDialog):
    """Dialogue pour ajouter ou modifier un élève."""
    
    def __init__(self, parent=None, eleve_data=None, classes_disponibles=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Widget parent
            eleve_data: Dictionnaire avec les données de l'élève (pour modification)
            classes_disponibles: Liste des classes disponibles
        """
        super().__init__(parent)
        self.eleve_data = eleve_data
        self.classes_disponibles = classes_disponibles or []
        self.setup_ui()
        
        # Pré-remplissage en mode modification
        if eleve_data:
            self.setWindowTitle("Modifier un élève")
            self.remplir_champs(eleve_data)
        else:
            self.setWindowTitle("Ajouter un élève")
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # Champ nom
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom de l'élève")
        layout.addRow("Nom *:", self.nom_edit)
        
        # Champ prénom
        self.prenom_edit = QLineEdit()
        self.prenom_edit.setPlaceholderText("Prénom de l'élève")
        layout.addRow("Prénom *:", self.prenom_edit)
        
        # Champ classe
        self.classe_combo = QComboBox()
        self.classe_combo.setEditable(True)
        self.classe_combo.setPlaceholderText("Classe")
        if self.classes_disponibles:
            self.classe_combo.addItems(self.classes_disponibles)
        layout.addRow("Classe *:", self.classe_combo)
        
        # Champ année scolaire
        self.annee_edit = QLineEdit()
        self.annee_edit.setPlaceholderText("Ex: 2025-2026")
        self.annee_edit.setInputMask("0000-0000")
        layout.addRow("Année scolaire *:", self.annee_edit)
        
        # Champ total dû
        self.total_du_spin = QSpinBox()
        self.total_du_spin.setRange(0, 999999999)
        self.total_du_spin.setSingleStep(1000)
        self.total_du_spin.setSuffix(" FCFA")
        self.total_du_spin.setValue(150000)
        layout.addRow("Total dû *:", self.total_du_spin)
        
        # Boutons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
    
    def remplir_champs(self, eleve_data):
        """
        Remplit les champs avec les données de l'élève.
        
        Args:
            eleve_data: Dictionnaire avec les données de l'élève
        """
        self.nom_edit.setText(eleve_data.get('nom', ''))
        self.prenom_edit.setText(eleve_data.get('prenom', ''))
        
        classe = eleve_data.get('classe', '')
        index = self.classe_combo.findText(classe)
        if index >= 0:
            self.classe_combo.setCurrentIndex(index)
        else:
            self.classe_combo.setEditText(classe)
        
        self.annee_edit.setText(eleve_data.get('annee_scolaire', ''))
        self.total_du_spin.setValue(int(eleve_data.get('total_du', 0)))
    
    def get_donnees(self):
        """
        Récupère les données du formulaire.
        
        Returns:
            dict: Dictionnaire avec les données du formulaire
        """
        return {
            'nom': self.nom_edit.text(),
            'prenom': self.prenom_edit.text(),
            'classe': self.classe_combo.currentText(),
            'annee_scolaire': self.annee_edit.text(),
            'total_du': self.total_du_spin.value()
        }
    
    def validate(self):
        """
        Valide le formulaire.
        
        Returns:
            bool: True si le formulaire est valide, False sinon
        """
        donnees = self.get_donnees()
        
        if not donnees['nom'].strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire.")
            self.nom_edit.setFocus()
            return False
        
        if len(donnees['nom'].strip()) < 2:
            QMessageBox.warning(self, "Validation", "Le nom doit contenir au moins 2 caractères.")
            self.nom_edit.setFocus()
            return False
        
        if not donnees['prenom'].strip():
            QMessageBox.warning(self, "Validation", "Le prénom est obligatoire.")
            self.prenom_edit.setFocus()
            return False
        
        if len(donnees['prenom'].strip()) < 2:
            QMessageBox.warning(self, "Validation", "Le prénom doit contenir au moins 2 caractères.")
            self.prenom_edit.setFocus()
            return False
        
        if not donnees['classe'].strip():
            QMessageBox.warning(self, "Validation", "La classe est obligatoire.")
            self.classe_combo.setFocus()
            return False
        
        if len(donnees['classe'].strip()) < 2:
            QMessageBox.warning(self, "Validation", "La classe doit contenir au moins 2 caractères.")
            self.classe_combo.setFocus()
            return False
        
        if not donnees['annee_scolaire'].strip():
            QMessageBox.warning(self, "Validation", "L'année scolaire est obligatoire.")
            self.annee_edit.setFocus()
            return False
        
        # Vérification du format YYYY-YYYY
        annee = donnees['annee_scolaire'].strip()
        if len(annee) != 9 or annee[4] != '-':
            QMessageBox.warning(
                self, "Validation",
                "L'année scolaire doit être au format YYYY-YYYY (ex: 2025-2026)."
            )
            self.annee_edit.setFocus()
            return False
        
        return True
    
    def accept(self):
        """Surcharge de accept pour valider avant de fermer."""
        if self.validate():
            super().accept()
