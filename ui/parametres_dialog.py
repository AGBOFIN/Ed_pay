"""
Dialogue de paramètres pour la direction.
Contient des onglets pour Établissement, Année scolaire, Classes, Modes de paiement, Reçus.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QLabel, QLineEdit, QPushButton, QSpinBox,
                               QListWidget, QMessageBox, QFileDialog,
                               QCheckBox, QFormLayout, QWidget)
from PySide6.QtCore import Qt
from services.parametre_service import ParametreService
from services.eleve_service import ValidationError


class ParametresDialog(QDialog):
    """Dialogue de paramètres de l'application."""
    
    def __init__(self, parent=None):
        """Initialise le dialogue de paramètres."""
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.setMinimumSize(600, 500)
        self.service = ParametreService()
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Onglets
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Onglet Établissement
        self.onglet_etablissement = QWidget()
        self.setup_onglet_etablissement()
        self.tabs.addTab(self.onglet_etablissement, "Établissement")
        
        # Onglet Année scolaire
        self.onglet_annee = QWidget()
        self.setup_onglet_annee()
        self.tabs.addTab(self.onglet_annee, "Année scolaire")
        
        # Onglet Classes
        self.onglet_classes = QWidget()
        self.setup_onglet_classes()
        self.tabs.addTab(self.onglet_classes, "Classes")
        
        # Onglet Modes de paiement
        self.onglet_modes = QWidget()
        self.setup_onglet_modes()
        self.tabs.addTab(self.onglet_modes, "Modes de paiement")
        
        # Onglet Reçus
        self.onglet_recus = QWidget()
        self.setup_onglet_recus()
        self.tabs.addTab(self.onglet_recus, "Reçus")
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.enregistrer_btn = QPushButton("Enregistrer")
        self.enregistrer_btn.clicked.connect(self.enregistrer)
        buttons_layout.addWidget(self.enregistrer_btn)
        
        self.annuler_btn = QPushButton("Annuler")
        self.annuler_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.annuler_btn)
        
        layout.addLayout(buttons_layout)
    
    def setup_onglet_etablissement(self):
        """Configure l'onglet Établissement."""
        layout = QFormLayout(self.onglet_etablissement)
        
        self.nom_edit = QLineEdit()
        layout.addRow("Nom de l'établissement * :", self.nom_edit)
        
        self.adresse_edit = QLineEdit()
        layout.addRow("Adresse :", self.adresse_edit)
        
        self.telephone_edit = QLineEdit()
        layout.addRow("Téléphone :", self.telephone_edit)
        
        self.email_edit = QLineEdit()
        layout.addRow("E-mail :", self.email_edit)
        
        self.devise_edit = QLineEdit()
        layout.addRow("Devise affichée :", self.devise_edit)
        
        # Logo
        logo_layout = QHBoxLayout()
        self.logo_edit = QLineEdit()
        self.logo_edit.setReadOnly(True)
        logo_layout.addWidget(self.logo_edit)
        
        self.logo_btn = QPushButton("Parcourir...")
        self.logo_btn.clicked.connect(self.choisir_logo)
        logo_layout.addWidget(self.logo_btn)
        
        layout.addRow("Logo :", logo_layout)
        
        self.pied_page_edit = QLineEdit()
        layout.addRow("Pied de page du reçu :", self.pied_page_edit)
    
    def setup_onglet_annee(self):
        """Configure l'onglet Année scolaire."""
        layout = QFormLayout(self.onglet_annee)
        
        self.annee_edit = QLineEdit()
        layout.addRow("Année scolaire * :", self.annee_edit)
    
    def setup_onglet_classes(self):
        """Configure l'onglet Classes."""
        layout = QVBoxLayout(self.onglet_annee)
        
        # Liste des classes
        layout.addWidget(QLabel("Classes actives :"))
        self.classes_list = QListWidget()
        layout.addWidget(self.classes_list)
        
        # Formulaire d'ajout/modification
        form_layout = QFormLayout()
        
        self.classe_nom_edit = QLineEdit()
        form_layout.addRow("Nom de la classe * :", self.classe_nom_edit)
        
        self.classe_frais_spin = QSpinBox()
        self.classe_frais_spin.setRange(0, 10000000)
        self.classe_frais_spin.setSingleStep(1000)
        self.classe_frais_spin.setSuffix(" FCFA")
        form_layout.addRow("Frais par défaut :", self.classe_frais_spin)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        self.ajouter_classe_btn = QPushButton("Ajouter")
        self.ajouter_classe_btn.clicked.connect(self.ajouter_classe)
        buttons_layout.addWidget(self.ajouter_classe_btn)
        
        self.modifier_classe_btn = QPushButton("Modifier")
        self.modifier_classe_btn.clicked.connect(self.modifier_classe)
        self.modifier_classe_btn.setEnabled(False)
        buttons_layout.addWidget(self.modifier_classe_btn)
        
        self.desactiver_classe_btn = QPushButton("Désactiver")
        self.desactiver_classe_btn.clicked.connect(self.desactiver_classe)
        self.desactiver_classe_btn.setEnabled(False)
        buttons_layout.addWidget(self.desactiver_classe_btn)
        
        layout.addLayout(buttons_layout)
        
        self.classes_list.itemSelectionChanged.connect(self.on_classe_selection_change)
    
    def setup_onglet_modes(self):
        """Configure l'onglet Modes de paiement."""
        layout = QVBoxLayout(self.onglet_modes)
        
        layout.addWidget(QLabel("Modes de paiement actifs :"))
        
        self.mode_especes_cb = QCheckBox("Espèces")
        layout.addWidget(self.mode_especes_cb)
        
        self.mode_cheque_cb = QCheckBox("Chèque")
        layout.addWidget(self.mode_cheque_cb)
        
        self.mode_virement_cb = QCheckBox("Virement")
        layout.addWidget(self.mode_virement_cb)
        
        self.mode_mobile_cb = QCheckBox("Mobile money")
        layout.addWidget(self.mode_mobile_cb)
        
        layout.addStretch()
    
    def setup_onglet_recus(self):
        """Configure l'onglet Reçus."""
        layout = QFormLayout(self.onglet_recus)
        
        self.prefixe_recu_edit = QLineEdit()
        layout.addRow("Préfixe des numéros de reçu * :", self.prefixe_recu_edit)
        
        layout.addRow(QLabel("Note : Le compteur et l'unicité des reçus ne changent jamais."))
    
    def charger_donnees(self):
        """Charge les données existantes."""
        # Établissement
        etablissement = self.service.obtenir_etablissement()
        self.nom_edit.setText(etablissement['nom'])
        self.adresse_edit.setText(etablissement['adresse'])
        self.telephone_edit.setText(etablissement['telephone'])
        self.email_edit.setText(etablissement['email'])
        self.devise_edit.setText(etablissement['devise'])
        self.logo_edit.setText(etablissement['logo'])
        self.pied_page_edit.setText(etablissement['pied_page'])
        
        # Année scolaire
        self.annee_edit.setText(self.service.obtenir_annee_scolaire())
        
        # Classes
        self.charger_classes()
        
        # Modes de paiement
        modes = self.service.obtenir_modes_paiement()
        self.mode_especes_cb.setChecked('espèces' in modes)
        self.mode_cheque_cb.setChecked('chèque' in modes)
        self.mode_virement_cb.setChecked('virement' in modes)
        self.mode_mobile_cb.setChecked('mobile money' in modes)
        
        # Reçus
        self.prefixe_recu_edit.setText(self.service.obtenir_prefixe_recu())
    
    def charger_classes(self):
        """Charge la liste des classes."""
        self.classes_list.clear()
        classes = self.service.lister_classes_actives()
        for classe in classes:
            self.classes_list.addItem(f"{classe['nom']} ({classe['frais_defaut']} FCFA)")
    
    def choisir_logo(self):
        """Ouvre le dialogue pour choisir un logo."""
        fichier, _ = QFileDialog.getOpenFileName(
            self, "Choisir un logo", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if fichier:
            self.logo_edit.setText(fichier)
    
    def on_classe_selection_change(self):
        """Gère le changement de sélection dans la liste des classes."""
        selected = self.classes_list.currentItem()
        self.modifier_classe_btn.setEnabled(selected is not None)
        self.desactiver_classe_btn.setEnabled(selected is not None)
    
    def ajouter_classe(self):
        """Ajoute une nouvelle classe."""
        nom = self.classe_nom_edit.text().strip()
        frais = self.classe_frais_spin.value()
        
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de la classe est obligatoire")
            return
        
        try:
            self.service.ajouter_classe(nom, frais)
            self.charger_classes()
            self.classe_nom_edit.clear()
            self.classe_frais_spin.setValue(0)
            QMessageBox.information(self, "Succès", "La classe a été ajoutée")
        except ValidationError as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def modifier_classe(self):
        """Modifie la classe sélectionnée."""
        QMessageBox.information(self, "Info", "Fonctionnalité à implémenter")
    
    def desactiver_classe(self):
        """Désactive la classe sélectionnée."""
        QMessageBox.information(self, "Info", "Fonctionnalité à implémenter")
    
    def enregistrer(self):
        """Enregistre tous les paramètres."""
        try:
            # Établissement
            self.service.definir_etablissement(
                self.nom_edit.text(),
                self.adresse_edit.text(),
                self.telephone_edit.text(),
                self.email_edit.text(),
                self.devise_edit.text(),
                self.logo_edit.text(),
                self.pied_page_edit.text()
            )
            
            # Année scolaire
            self.service.definir_annee_scolaire(self.annee_edit.text())
            
            # Modes de paiement
            modes = []
            if self.mode_especes_cb.isChecked():
                modes.append('espèces')
            if self.mode_cheque_cb.isChecked():
                modes.append('chèque')
            if self.mode_virement_cb.isChecked():
                modes.append('virement')
            if self.mode_mobile_cb.isChecked():
                modes.append('mobile money')
            
            if len(modes) == 0:
                QMessageBox.warning(self, "Erreur", "Au moins un mode de paiement doit être actif")
                return
            
            self.service.definir_modes_paiement(modes)
            
            # Reçus
            self.service.definir_prefixe_recu(self.prefixe_recu_edit.text())
            
            QMessageBox.information(self, "Succès", "Les paramètres ont été enregistrés")
            self.accept()
            
        except ValidationError as e:
            QMessageBox.critical(self, "Erreur", str(e))
