"""
Dialogue de fiche détaillée d'un élève avec historique des paiements et réimpression de reçus.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QHeaderView, QDialogButtonBox,
    QFrame
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QBrush, QDesktopServices, QFont
from services.fiche_eleve_service import FicheEleveService
from services.solde_service import SoldeService
from services.paiement_service import PaiementService
from services.recu_service import RecuService
from services.recu_pdf import generer_recu_pdf


class FicheEleveDialog(QDialog):
    """Dialogue pour afficher la fiche détaillée d'un élève."""
    
    def __init__(self, parent=None, eleve_id=None, main_window=None):
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
        self.setWindowTitle("Fiche Financière de l'Élève - EduPaie")
        self.setMinimumSize(850, 620)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section identité de l'élève
        identite_layout = self._creer_section_identite()
        layout.addLayout(identite_layout)
        
        # Tableau des paiements
        table_layout = self._creer_section_paiements()
        layout.addLayout(table_layout)
        
        # Boutons d'action
        buttons_layout = self._creer_section_boutons()
        layout.addLayout(buttons_layout)
        
        # Bouton de fermeture
        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.button(QDialogButtonBox.Close).setText("Fermer")
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
    
    def _creer_section_identite(self):
        """Crée la section moderne d'identité de l'élève."""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 16px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(12)
        
        # Ligne supérieure : Avatar + Nom + Statut
        top_row = QHBoxLayout()
        
        self.avatar_label = QLabel("👤")
        self.avatar_label.setStyleSheet("""
            font-size: 28px;
            background-color: #EFF6FF;
            border-radius: 20px;
            padding: 6px;
        """)
        top_row.addWidget(self.avatar_label)
        
        titre_box = QVBoxLayout()
        self.nom_prenom_label = QLabel("Chargement...")
        self.nom_prenom_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A;")
        titre_box.addWidget(self.nom_prenom_label)
        
        self.info_label = QLabel("Classe & Année scolaire")
        self.info_label.setStyleSheet("font-size: 13px; color: #64748B;")
        titre_box.addWidget(self.info_label)
        top_row.addLayout(titre_box)
        
        top_row.addStretch()
        
        self.statut_label = QLabel("Statut")
        self.statut_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            padding: 6px 14px;
            border-radius: 16px;
            background-color: #E2E8F0;
            color: #334155;
        """)
        top_row.addWidget(self.statut_label)
        
        container_layout.addLayout(top_row)
        
        # Cartes métriques financières
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(10)
        
        self.card_total_du = self._creer_mini_carte("Total dû", "0 FCFA", "#2563EB")
        self.total_du_label = self.card_total_du.findChild(QLabel, "valeur")
        metrics_layout.addWidget(self.card_total_du)
        
        self.card_total_paye = self._creer_mini_carte("Total encaissé", "0 FCFA", "#059669")
        self.total_paye_label = self.card_total_paye.findChild(QLabel, "valeur")
        metrics_layout.addWidget(self.card_total_paye)
        
        self.card_solde = self._creer_mini_carte("Solde restant", "0 FCFA", "#DC2626")
        self.solde_label = self.card_solde.findChild(QLabel, "valeur")
        metrics_layout.addWidget(self.card_solde)
        
        container_layout.addLayout(metrics_layout)
        
        root = QVBoxLayout()
        root.addWidget(container)
        return root
    
    def _creer_mini_carte(self, titre, valeur, couleur):
        """Crée une mini carte financière."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-left: 4px solid {couleur};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setSpacing(2)
        lay.setContentsMargins(4, 4, 4, 4)
        
        t = QLabel(titre)
        t.setStyleSheet("font-size: 11px; color: #64748B; font-weight: bold; text-transform: uppercase;")
        lay.addWidget(t)
        
        v = QLabel(valeur)
        v.setObjectName("valeur")
        v.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {couleur};")
        lay.addWidget(v)
        
        return frame
    
    def _creer_separation(self):
        """Crée une ligne de séparation."""
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Plain)
        frame.setStyleSheet("color: #E2E8F0; background-color: #E2E8F0; max-height: 1px;")
        return frame
    
    def _creer_section_paiements(self):
        """Crée la section du tableau des paiements."""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        titre_layout = QHBoxLayout()
        titre_label = QLabel("📜 Historique Chronologique des Règlements")
        titre_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E293B;")
        titre_layout.addWidget(titre_label)
        titre_layout.addStretch()
        
        layout.addLayout(titre_layout)
        
        # Table des paiements
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Date", "Montant (FCFA)", "Mode de versement", "N° Reçu officiel", "Solde après (FCFA)"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Configuration des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Message si aucun paiement
        self.message_label = QLabel("ℹ️ Aucun paiement n'a encore été enregistré pour cet élève.")
        self.message_label.setStyleSheet("""
            font-size: 13px;
            color: #64748B;
            padding: 24px;
            background-color: #F8FAFC;
            border: 1px dashed #CBD5E1;
            border-radius: 8px;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setVisible(False)
        layout.addWidget(self.message_label)
        
        return layout
    
    def _creer_section_boutons(self):
        """Crée la section des boutons d'action."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.voir_recu_btn = QPushButton("🖨️ Voir / Ré-imprimer le reçu PDF")
        self.voir_recu_btn.setProperty("variant", "secondary")
        self.voir_recu_btn.setToolTip("Ouvrir et ré-imprimer le reçu PDF officiel du versement sélectionné")
        self.voir_recu_btn.clicked.connect(self.on_voir_recu)
        self.voir_recu_btn.setEnabled(False)
        layout.addWidget(self.voir_recu_btn)
        
        self.enregistrer_paiement_btn = QPushButton("➕ Enregistrer un paiement")
        self.enregistrer_paiement_btn.setProperty("variant", "success")
        self.enregistrer_paiement_btn.setToolTip("Ajouter un nouveau versement pour cet élève")
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
        self.info_label.setText(f"Classe : <b>{eleve['classe']}</b>  •  Année scolaire : <b>{eleve['annee_scolaire']}</b>")
        
        # Statistiques financières
        total_du_fcfa = self.donnees_fiche['total_du']
        self.total_du_label.setText(SoldeService.formater_monnaie_fcfa(total_du_fcfa))
        
        total_paye_fcfa = self.donnees_fiche['total_paye']
        self.total_paye_label.setText(SoldeService.formater_monnaie_fcfa(total_paye_fcfa))
        
        solde_fcfa = self.donnees_fiche['solde']
        self.solde_label.setText(SoldeService.formater_monnaie_fcfa(solde_fcfa))
        
        statut = self.donnees_fiche['statut']
        self.statut_label.setText(f"● {statut}")
        
        # Style du statut
        if statut == "Soldé":
            self.statut_label.setStyleSheet("font-size: 13px; font-weight: bold; padding: 6px 14px; border-radius: 16px; background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC;")
            self.enregistrer_paiement_btn.setEnabled(False)
            self.enregistrer_paiement_btn.setToolTip("Ce compte est déjà entièrement soldé.")
        elif statut == "Partiellement payé":
            self.statut_label.setStyleSheet("font-size: 13px; font-weight: bold; padding: 6px 14px; border-radius: 16px; background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D;")
            self.enregistrer_paiement_btn.setEnabled(True)
        else:  # Non payé
            self.statut_label.setStyleSheet("font-size: 13px; font-weight: bold; padding: 6px 14px; border-radius: 16px; background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5;")
            self.enregistrer_paiement_btn.setEnabled(True)
    
    def mettre_a_jour_paiements(self):
        """Met à jour le tableau des paiements avec formatage FCFA exact."""
        paiements = self.donnees_fiche['paiements']
        
        if not paiements:
            self.table.setVisible(False)
            self.message_label.setVisible(True)
            return
        
        self.table.setVisible(True)
        self.message_label.setVisible(False)
        self.table.setRowCount(len(paiements))
        
        for row, paiement in enumerate(paiements):
            # Date (Centré)
            date_formatee = self._formater_date(paiement['date'])
            item_date = QTableWidgetItem(date_formatee)
            item_date.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_date)
            
            # Montant (Aligné à droite, format monnaie FCFA)
            montant = paiement['montant']
            item_montant = QTableWidgetItem(SoldeService.formater_monnaie_fcfa(int(montant)))
            item_montant.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_montant.setFont(QFont("Segoe UI", 9, QFont.Bold))
            item_montant.setForeground(QBrush(QColor("#059669")))
            self.table.setItem(row, 1, item_montant)
            
            # Mode (Centré)
            item_mode = QTableWidgetItem(paiement['mode'].capitalize())
            item_mode.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_mode)
            
            # Numéro de reçu
            item_recu = QTableWidgetItem(paiement['numero_recu'])
            item_recu.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.table.setItem(row, 3, item_recu)
            
            # Solde après (Aligné à droite)
            solde_apres_fcfa = paiement['solde_apres']
            item_solde = QTableWidgetItem(SoldeService.formater_monnaie_fcfa(int(solde_apres_fcfa)))
            item_solde.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 4, item_solde)
    
    def mettre_a_jour_statistiques(self):
        """Met à jour les statistiques après chargement."""
        pass
    
    def _formater_date(self, date_str):
        """Formate une date pour l'affichage DD/MM/YYYY."""
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
        else:
            date_part = date_str
        
        try:
            annee, mois, jour = date_part.split('-')
            return f"{jour}/{mois}/{annee}"
        except Exception:
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
            
            QDesktopServices.openUrl(QUrl.fromLocalFile(chemin_pdf))
            QMessageBox.information(
                self,
                "Reçu généré",
                f"Le reçu a été ouvert avec succès :\n{chemin_pdf}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du reçu : {str(e)}")
    
    def on_enregistrer_paiement(self):
        """Gère le clic sur le bouton Enregistrer un paiement."""
        from ui.paiement_dialog import PaiementDialog
        
        eleve = self.donnees_fiche['eleve']
        eleve['total_paye'] = self.donnees_fiche['total_paye']
        
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
                
                reponse = QMessageBox.question(
                    self,
                    "Reçu PDF",
                    "Voulez-vous générer et ouvrir le reçu PDF maintenant ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reponse == QMessageBox.Yes:
                    try:
                        donnees_recu = self.recu_service.obtenir_donnees_recu_par_numero(numero_recu)
                        chemin_pdf = generer_recu_pdf(donnees_recu)
                        QDesktopServices.openUrl(QUrl.fromLocalFile(chemin_pdf))
                    except Exception as e:
                        QMessageBox.critical(self, "Erreur", str(e))
                
                self.charger_donnees()
                
                if self.main_window:
                    self.main_window.rafraichir_tableau_de_bord()
            except ValidationError as e:
                QMessageBox.critical(self, "Erreur", str(e))
