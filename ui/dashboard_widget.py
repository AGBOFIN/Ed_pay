"""
Widget pour le tableau de bord EduPaie.
Affiche les indicateurs financiers globaux, le taux de recouvrement,
ainsi que la liste interactive des élèves avec filtres, recherche et export.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QComboBox, QHeaderView, QFrame, QLineEdit,
    QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QColor, QBrush, QFont
from services.dashboard_service import DashboardService
from services.solde_service import SoldeService
from services.export_service import ExportService


class DashboardTableModel(QAbstractTableModel):
    """Modèle de table pour afficher les élèves dans le tableau de bord."""
    
    def __init__(self, eleves=None, parent=None):
        super().__init__(parent)
        self.eleves = eleves or []
        self.headers = ["ID", "Nom", "Prénom", "Classe", "Total dû (FCFA)", "Payé (FCFA)", "Solde (FCFA)", "Statut"]
    
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
            statut = eleve.get('statut', SoldeService.determiner_statut(total_du_fcfa, total_paye_fcfa))
            if statut == "Soldé":
                return QBrush(QColor(220, 252, 231))  # Soft Emerald
            elif statut == "Partiellement payé":
                return QBrush(QColor(254, 243, 199))  # Soft Amber
            else:
                return QBrush(QColor(254, 226, 226))  # Soft Rose
        
        elif role == Qt.ForegroundRole and col == 7:
            statut = eleve.get('statut', SoldeService.determiner_statut(total_du_fcfa, total_paye_fcfa))
            if statut == "Soldé":
                return QBrush(QColor(22, 101, 52))
            elif statut == "Partiellement payé":
                return QBrush(QColor(146, 64, 14))
            else:
                return QBrush(QColor(153, 27, 27))
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def set_eleves(self, eleves):
        self.beginResetModel()
        self.eleves = eleves
        self.endResetModel()


class DashboardWidget(QWidget):
    """Widget principal pour le tableau de bord avec KPI modernes et table interactive."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_service = DashboardService()
        self.derniers_eleves_charges = []
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
        
        # En-tête du tableau de bord
        layout.addLayout(self._creer_entete_dashboard())
        
        # Section des cartes d'indicateurs
        cartes_layout = self._creer_section_cartes()
        layout.addLayout(cartes_layout)
        
        # Section du tableau des élèves
        tableau_layout = self._creer_section_tableau()
        layout.addLayout(tableau_layout)
    
    def _creer_entete_dashboard(self):
        """Crée l'en-tête moderne avec titre et raccourcis."""
        layout = QHBoxLayout()
        
        titre_box = QVBoxLayout()
        titre = QLabel("📊 Tableau de Bord Financier")
        titre.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A;")
        
        soustitre = QLabel("Vue globale des inscriptions, encaissements et recouvrements scolaires")
        soustitre.setStyleSheet("font-size: 13px; color: #64748B;")
        
        titre_box.addWidget(titre)
        titre_box.addWidget(soustitre)
        layout.addLayout(titre_box)
        layout.addStretch()
        
        # Bouton d'actualisation rapide
        self.actualiser_btn = QPushButton("🔄 Actualiser")
        self.actualiser_btn.setProperty("variant", "secondary")
        self.actualiser_btn.setToolTip("Rafraîchir les calculs et indicateurs (F5)")
        self.actualiser_btn.clicked.connect(self.rafraichir)
        layout.addWidget(self.actualiser_btn)
        
        return layout
    
    def _creer_section_cartes(self):
        """Crée la section des cartes d'indicateurs avec taux de recouvrement."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Carte 1 : Nombre d'élèves
        self.nb_eleves_card = self._creer_carte("Nombre d'élèves", "0", "#2563EB", "👥", "Inscriptions actives")
        layout.addWidget(self.nb_eleves_card)
        
        # Carte 2 : Total encaissé
        self.total_encaisse_card = self._creer_carte("Total encaissé", "0 FCFA", "#059669", "💰", "Montant perçu en caisse")
        layout.addWidget(self.total_encaisse_card)
        
        # Carte 3 : Total restant dû
        self.total_restant_du_card = self._creer_carte("Total restant dû", "0 FCFA", "#DC2626", "⏳", "Reste à recouvrer")
        layout.addWidget(self.total_restant_du_card)
        
        # Carte 4 : Élèves non soldés
        self.nb_non_soldes_card = self._creer_carte("Élèves non soldés", "0", "#D97706", "⚠️", "Comptes avec reliquat")
        layout.addWidget(self.nb_non_soldes_card)

        # Carte 5 : Taux de recouvrement
        self.taux_recouvrement_card = self._creer_carte("Taux de recouvrement", "0 %", "#7C3AED", "📈", "Performance globale")
        layout.addWidget(self.taux_recouvrement_card)
        
        return layout
    
    def _creer_carte(self, titre, valeur, couleur, icone="📌", sous_texte=""):
        """Crée une carte d'indicateur moderne avec accent de couleur."""
        carte = QFrame()
        carte.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-top: 4px solid {couleur};
                border-radius: 8px;
                padding: 12px 14px;
            }}
        """)
        carte_layout = QVBoxLayout(carte)
        carte_layout.setSpacing(6)
        carte_layout.setContentsMargins(8, 8, 8, 8)
        
        # Ligne supérieure : Titre + Icône
        top_layout = QHBoxLayout()
        titre_label = QLabel(titre)
        titre_label.setStyleSheet("font-size: 12px; color: #475569; font-weight: 700; text-transform: uppercase;")
        top_layout.addWidget(titre_label)
        top_layout.addStretch()
        
        icon_label = QLabel(icone)
        icon_label.setStyleSheet("font-size: 16px;")
        top_layout.addWidget(icon_label)
        carte_layout.addLayout(top_layout)
        
        # Valeur principale
        valeur_label = QLabel(valeur)
        valeur_label.setStyleSheet(f"font-size: 22px; color: {couleur}; font-weight: bold; margin: 4px 0;")
        carte_layout.addWidget(valeur_label)
        
        # Sous-texte / sous-titre
        if sous_texte:
            sub_label = QLabel(sous_texte)
            sub_label.setStyleSheet("font-size: 11px; color: #94A3B8;")
            carte_layout.addWidget(sub_label)
            carte.sub_label = sub_label
        
        # Stocke la référence pour mise à jour
        carte.valeur_label = valeur_label
        carte.couleur = couleur
        
        return carte
    
    def _creer_separation(self):
        """Crée une ligne de séparation discrète."""
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Plain)
        frame.setStyleSheet("color: #E2E8F0; background-color: #E2E8F0; max-height: 1px;")
        return frame
    
    def _creer_section_tableau(self):
        """Crée la section du tableau des élèves avec filtres, recherche et export."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Barre de filtres et recherche
        filtres_layout = QHBoxLayout()
        filtres_layout.setSpacing(10)
        
        # Champ de recherche rapide
        self.recherche_edit = QLineEdit()
        self.recherche_edit.setPlaceholderText("🔍 Rechercher un élève (nom ou prénom)...")
        self.recherche_edit.setClearButtonEnabled(True)
        self.recherche_edit.setMinimumWidth(260)
        self.recherche_edit.textChanged.connect(self.apply_filters)
        filtres_layout.addWidget(self.recherche_edit)
        
        # Filtre par statut
        statut_label = QLabel("Statut :")
        statut_label.setStyleSheet("font-weight: 600; color: #475569;")
        filtres_layout.addWidget(statut_label)
        
        self.statut_combo = QComboBox()
        self.statut_combo.addItems(["Tous", "Soldé", "Partiellement payé", "Non payé"])
        self.statut_combo.currentIndexChanged.connect(self.on_statut_changed)
        filtres_layout.addWidget(self.statut_combo)
        
        filtres_layout.addStretch()
        
        # Indicateur de nombre d'élèves filtrés
        self.compteur_label = QLabel("0 élève(s)")
        self.compteur_label.setStyleSheet("color: #64748B; font-weight: 500; font-size: 12px;")
        filtres_layout.addWidget(self.compteur_label)
        
        # Bouton Exporter CSV
        self.exporter_btn = QPushButton("📥 Exporter CSV")
        self.exporter_btn.setProperty("variant", "secondary")
        self.exporter_btn.setToolTip("Exporter ce tableau vers Excel / CSV")
        self.exporter_btn.clicked.connect(self.exporter_tableau_csv)
        filtres_layout.addWidget(self.exporter_btn)
        
        layout.addLayout(filtres_layout)
        
        # Table des élèves
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Classe", "Total dû (FCFA)", "Payé (FCFA)", "Solde (FCFA)", "Statut"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setToolTip("Double-cliquez sur un élève pour ouvrir sa fiche détaillée")
        self.table.itemDoubleClicked.connect(self.on_table_double_clicked)
        
        # Configuration des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nom
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Prénom
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
            indicateurs = self.dashboard_service.obtenir_indicateurs()
            self.mettre_a_jour_cartes(indicateurs)
            self.apply_filters()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données : {str(e)}")
    
    def mettre_a_jour_cartes(self, indicateurs):
        """Met à jour les cartes avec les indicateurs et calcule le taux de recouvrement."""
        # Nombre d'élèves
        self.nb_eleves_card.valeur_label.setText(str(indicateurs['nb_eleves']))
        
        # Total encaissé
        self.total_encaisse_card.valeur_label.setText(SoldeService.formater_monnaie_fcfa(indicateurs['total_encaisse']))
        
        # Total restant dû
        self.total_restant_du_card.valeur_label.setText(SoldeService.formater_monnaie_fcfa(indicateurs['total_restant_du']))
        
        # Élèves non soldés
        self.nb_non_soldes_card.valeur_label.setText(str(indicateurs['nb_eleves_non_soldes']))

        # Taux de recouvrement
        total_global = indicateurs['total_encaisse'] + indicateurs['total_restant_du']
        if total_global > 0:
            taux = (indicateurs['total_encaisse'] / total_global) * 100
            self.taux_recouvrement_card.valeur_label.setText(f"{taux:.1f} %")
        else:
            self.taux_recouvrement_card.valeur_label.setText("N/A")
    
    def apply_filters(self):
        """Applique les filtres de statut et de recherche textuelle."""
        statut = self.statut_combo.currentText()
        terme = getattr(self, 'recherche_edit', None)
        recherche_texte = terme.text().strip().lower() if terme else ""
        
        try:
            eleves = self.dashboard_service.obtenir_liste_eleves_filtree_par_statut(statut)
            
            # Filtre supplémentaire par terme de recherche si présent
            if recherche_texte:
                eleves = [
                    e for e in eleves
                    if recherche_texte in e['nom'].lower() or recherche_texte in e['prenom'].lower()
                ]
            
            self.derniers_eleves_charges = eleves
            self.compteur_label.setText(f"{len(eleves)} élève(s) affiché(s)")
            self.mettre_a_jour_tableau(eleves)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du filtrage : {str(e)}")
    
    def mettre_a_jour_tableau(self, eleves):
        """Met à jour le tableau avec la liste des élèves."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(eleves))
        
        for row, eleve in enumerate(eleves):
            # ID (Centré)
            item_id = QTableWidgetItem(str(eleve['id']))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_id)
            
            # Nom
            item_nom = QTableWidgetItem(eleve['nom'])
            item_nom.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.table.setItem(row, 1, item_nom)
            
            # Prénom
            self.table.setItem(row, 2, QTableWidgetItem(eleve['prenom']))
            
            # Classe (Centré)
            item_classe = QTableWidgetItem(eleve['classe'])
            item_classe.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, item_classe)
            
            # Total dû (Aligné à droite)
            total_du_fcfa = eleve['total_du']
            item_total = QTableWidgetItem(SoldeService.formater_monnaie_fcfa(total_du_fcfa))
            item_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 4, item_total)
            
            # Payé (Aligné à droite, vert)
            total_paye = eleve.get('total_paye', 0)
            item_paye = QTableWidgetItem(SoldeService.formater_monnaie_fcfa(total_paye))
            item_paye.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_paye.setForeground(QBrush(QColor("#059669")))
            self.table.setItem(row, 5, item_paye)
            
            # Solde (Aligné à droite)
            solde = eleve.get('solde', SoldeService.calculer_solde(eleve['total_du'], total_paye))
            item_solde = QTableWidgetItem(SoldeService.formater_monnaie_fcfa(solde))
            item_solde.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if solde > 0:
                item_solde.setForeground(QBrush(QColor("#DC2626")))
                item_solde.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.table.setItem(row, 6, item_solde)
            
            # Statut
            statut = eleve.get('statut', SoldeService.determiner_statut(eleve['total_du'], total_paye))
            item_statut = QTableWidgetItem(statut)
            item_statut.setTextAlignment(Qt.AlignCenter)
            item_statut.setFont(QFont("Segoe UI", 9, QFont.Bold))
            
            # Couleurs modernes pour le statut
            if statut == "Soldé":
                item_statut.setBackground(QBrush(QColor(220, 252, 231)))
                item_statut.setForeground(QBrush(QColor(22, 101, 52)))
            elif statut == "Partiellement payé":
                item_statut.setBackground(QBrush(QColor(254, 243, 199)))
                item_statut.setForeground(QBrush(QColor(146, 64, 14)))
            else:  # Non payé
                item_statut.setBackground(QBrush(QColor(254, 226, 226)))
                item_statut.setForeground(QBrush(QColor(153, 27, 27)))
            
            self.table.setItem(row, 7, item_statut)
        
        self.table.setSortingEnabled(True)
    
    def on_table_double_clicked(self, item):
        """Ouvre la fiche détaillée d'un élève lors d'un double-clic sur le tableau de bord."""
        if not item:
            return
        row = item.row()
        item_id = self.table.item(row, 0)
        if not item_id:
            return
        try:
            eleve_id = int(item_id.text())
            from ui.fiche_eleve_dialog import FicheEleveDialog
            dialog = FicheEleveDialog(self, eleve_id=eleve_id)
            dialog.exec()
            self.rafraichir()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la fiche élève : {str(e)}")
    
    def exporter_tableau_csv(self):
        """Exporte les élèves affichés dans un fichier CSV compatible Excel."""
        if not self.derniers_eleves_charges:
            QMessageBox.information(self, "Export", "Aucun élève à exporter.")
            return
        
        chemin, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter la liste des élèves",
            "edupaie_tableau_de_bord.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        if chemin:
            try:
                nb = ExportService.exporter_eleves_csv(self.derniers_eleves_charges, chemin)
                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"La liste de {nb} élève(s) a été exportée avec succès dans :\n{chemin}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'export", str(e))
    
    def on_statut_changed(self, index):
        """Gère le changement de filtre de statut."""
        self.apply_filters()
    
    def rafraichir(self):
        """Rafraîchit toutes les données du tableau de bord."""
        self.charger_donnees()
