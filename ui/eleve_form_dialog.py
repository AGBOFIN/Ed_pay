"""
Dialogue de formulaire pour l'ajout et la modification d'élèves.
Offre une saisie rapide et assistée pour la secrétaire.
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox,
    QDialogButtonBox, QMessageBox, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt
from datetime import datetime


class EleveFormDialog(QDialog):
    """Dialogue pour ajouter ou modifier un élève."""
    
    def __init__(self, parent=None, eleve_data=None, classes_disponibles=None):
        """
        Initialise le dialogue.

        Args:
            parent: Widget parent
            eleve_data: Dictionnaire avec les données de l'élève (pour modification)
            classes_disponibles: Liste de dictionnaires {'nom': str, 'frais_defaut': int}
        """
        super().__init__(parent)
        self.eleve_data = eleve_data
        self.classes_disponibles = classes_disponibles or []
        self.classes_map = {c['nom']: c['frais_defaut'] for c in self.classes_disponibles}
        self.setup_ui()
        
        # Pré-remplissage en mode modification
        if eleve_data:
            self.setWindowTitle("Modifier un élève - EduPaie")
            self.remplir_champs(eleve_data)
        else:
            self.setWindowTitle("Ajouter un élève - EduPaie")
            # Pré-remplissage intelligent de l'année scolaire en cours
            annee_actuelle = datetime.now().year
            # Si nous sommes entre septembre et décembre, année = YYYY-(YYYY+1)
            # Sinon (janvier - août), année = (YYYY-1)-YYYY
            mois = datetime.now().month
            if mois >= 8:
                def_annee = f"{annee_actuelle}-{annee_actuelle + 1}"
            else:
                def_annee = f"{annee_actuelle - 1}-{annee_actuelle}"
            self.annee_edit.setText(def_annee)
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.setMinimumWidth(440)
        
        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(16)
        root_layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête informatif
        header = QLabel("📝 Informations administratives de l'élève")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E3A8A;")
        root_layout.addWidget(header)
        
        sub = QLabel("Tous les champs marqués d'un astérisque (*) sont obligatoires.")
        sub.setStyleSheet("font-size: 12px; color: #64748B; margin-bottom: 6px;")
        root_layout.addWidget(sub)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        layout = QFormLayout(form_frame)
        layout.setSpacing(12)
        layout.setLabelAlignment(Qt.AlignRight)
        
        # Champ nom
        self.nom_edit = QLineEdit()
        self.nom_edit.setPlaceholderText("Nom de famille (ex: KOUASSI)")
        layout.addRow("Nom * :", self.nom_edit)
        
        # Champ prénom
        self.prenom_edit = QLineEdit()
        self.prenom_edit.setPlaceholderText("Prénom(s) (ex: Jean-Marc)")
        layout.addRow("Prénom * :", self.prenom_edit)
        
        # Champ classe
        self.classe_combo = QComboBox()
        self.classe_combo.setEditable(True)
        self.classe_combo.setPlaceholderText("Sélectionner ou saisir une classe")
        if self.classes_disponibles:
            for classe in self.classes_disponibles:
                self.classe_combo.addItem(f"{classe['nom']} ({classe['frais_defaut']} FCFA)", classe['nom'])
        self.classe_combo.currentIndexChanged.connect(self.on_classe_change)
        layout.addRow("Classe *:", self.classe_combo)

        # Champ année scolaire
        self.annee_edit = QLineEdit()
        self.annee_edit.setPlaceholderText("Ex: 2025-2026")
        self.annee_edit.setInputMask("0000-0000")
        layout.addRow("Année scolaire * :", self.annee_edit)
        
        # Champ total dû
        self.total_du_spin = QSpinBox()
        self.total_du_spin.setRange(0, 999999999)
        self.total_du_spin.setSingleStep(5000)
        self.total_du_spin.setSuffix(" FCFA")
        self.total_du_spin.setValue(150000)
        layout.addRow("Total dû * :", self.total_du_spin)
        
        root_layout.addWidget(form_frame)
        
        # Boutons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        self.buttons.button(QDialogButtonBox.Ok).setText("Enregistrer")
        self.buttons.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        root_layout.addWidget(self.buttons)
    
    def on_classe_change(self, index):
        """
        Gère le changement de classe pour pré-remplir les frais par défaut.
        
        Args:
            index: Index de la classe sélectionnée
        """
        if index >= 0:
            classe_nom = self.classe_combo.itemData(index)
            if classe_nom and classe_nom in self.classes_map:
                # Pré-remplit les frais par défaut
                self.total_du_spin.setValue(self.classes_map[classe_nom])
    
    def remplir_champs(self, eleve_data):
        """Remplit les champs avec les données de l'élève."""
        self.nom_edit.setText(eleve_data.get('nom', ''))
        self.prenom_edit.setText(eleve_data.get('prenom', ''))
        
        classe = eleve_data.get('classe', '')
        # Cherche la classe dans le combo box par itemData
        for i in range(self.classe_combo.count()):
            if self.classe_combo.itemData(i) == classe:
                self.classe_combo.setCurrentIndex(i)
                break
        else:
            # Si non trouvée, affiche simplement le nom
            self.classe_combo.setEditText(classe)
        
        self.annee_edit.setText(eleve_data.get('annee_scolaire', ''))
        self.total_du_spin.setValue(int(eleve_data.get('total_du', 0)))
    
    def get_donnees(self):
        """
        Récupère les données du formulaire.

        Returns:
            dict: Dictionnaire avec les données du formulaire
        """
        # Récupère le nom de la classe (itemData si sélectionné, sinon text)
        classe_nom = self.classe_combo.currentData()
        if classe_nom is None:
            classe_nom = self.classe_combo.currentText()
            # Nettoie le nom de classe si l'utilisateur a saisi manuellement
            classe_nom = classe_nom.split(' (')[0] if ' (' in classe_nom else classe_nom

        return {
            'nom': self.nom_edit.text(),
            'prenom': self.prenom_edit.text(),
            'classe': classe_nom,
            'annee_scolaire': self.annee_edit.text(),
            'total_du': self.total_du_spin.value()
        }
    
    def validate(self):
        """Valide le formulaire."""
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
