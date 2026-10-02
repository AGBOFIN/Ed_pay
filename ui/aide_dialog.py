"""
Dialogue d'aide, de guide d'utilisation et de raccourcis clavier pour EduPaie.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QWidget, QTextBrowser, QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt


class AideDialog(QDialog):
    """Fenêtre d'aide et guide utilisateur intégrée."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guide d'utilisation & Aide - EduPaie")
        self.setMinimumSize(680, 520)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # En-tête
        header_layout = QHBoxLayout()
        icon_label = QLabel("🎓")
        icon_label.setStyleSheet("font-size: 36px; padding-right: 10px;")
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title = QLabel("EduPaie - Guide d'utilisation")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E3A8A;")
        subtitle = QLabel("Logiciel de gestion des paiements et scolarités")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Onglets
        tabs = QTabWidget()

        # Onglet 1 : Prise en main rapide
        guide_widget = QTextBrowser()
        guide_widget.setOpenExternalLinks(True)
        guide_widget.setHtml("""
            <div style="font-family: sans-serif; line-height: 1.6; color: #1E293B;">
                <h3 style="color: #2563EB; margin-bottom: 8px;">1. Comment enregistrer un paiement ?</h3>
                <p>Deux façons simples :</p>
                <ul>
                    <li><b>Depuis la Gestion des Élèves :</b> sélectionnez l'élève dans la liste, puis cliquez sur <b>"Enregistrer paiement"</b> (ou double-cliquez pour ouvrir sa fiche).</li>
                    <li><b>Depuis le Tableau de Bord :</b> double-cliquez sur n'importe quel élève pour ouvrir sa fiche détaillée, puis cliquez sur <b>"Enregistrer un paiement"</b>.</li>
                </ul>
                <p>💡 Le logiciel vérifie automatiquement que le montant ne dépasse pas le solde restant.</p>

                <h3 style="color: #2563EB; margin-bottom: 8px;">2. Génération et réimpression des reçus PDF</h3>
                <p>À chaque paiement validé, l'application vous propose d'ouvrir et imprimer le reçu officiel.</p>
                <p>Pour ré-imprimer un ancien reçu : ouvrez la <b>Fiche élève</b>, cliquez sur le paiement souhaité dans l'historique, puis cliquez sur <b>"Voir / Ré-imprimer le reçu"</b>.</p>

                <h3 style="color: #2563EB; margin-bottom: 8px;">3. Exportation vers Microsoft Excel (CSV)</h3>
                <p>Dans la fenêtre <b>Gestion des élèves</b> ou sur le <b>Tableau de bord</b>, cliquez sur <b>"Exporter CSV"</b> pour enregistrer la liste complète avec les soldes et statuts.</p>
            </div>
        """)
        tabs.addTab(guide_widget, "📖 Prise en main")

        # Onglet 2 : Raccourcis clavier
        raccourcis_widget = QTextBrowser()
        raccourcis_widget.setHtml("""
            <div style="font-family: sans-serif; line-height: 1.6; color: #1E293B;">
                <h3 style="color: #2563EB; margin-bottom: 12px;">Raccourcis clavier utiles</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #F1F5F9;">
                        <th style="padding: 8px; border: 1px solid #E2E8F0; text-align: left;">Raccourci</th>
                        <th style="padding: 8px; border: 1px solid #E2E8F0; text-align: left;">Action</th>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>Ctrl + 1</b> ou <b>Alt + T</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Afficher le Tableau de bord</td>
                    </tr>
                    <tr style="background-color: #F8FAFC;">
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>Ctrl + 2</b> ou <b>Alt + E</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Afficher la Gestion des élèves</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>Ctrl + P</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Ouvrir la liste pour choisir l'élève du paiement</td>
                    </tr>
                    <tr style="background-color: #F8FAFC;">
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>Ctrl + N</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Ajouter un nouvel élève</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>F5</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Actualiser les données</td>
                    </tr>
                    <tr style="background-color: #F8FAFC;">
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>F1</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Ouvrir cette aide</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>Double-clic sur un élève</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Ouvrir sa fiche financière complète</td>
                    </tr>
                    <tr style="background-color: #F8FAFC;">
                        <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>Clic droit sur un élève</b></td>
                        <td style="padding: 8px; border: 1px solid #E2E8F0;">Menu contextuel (Paiement, Fiche, Modifier...)</td>
                    </tr>
                </table>
            </div>
        """)
        tabs.addTab(raccourcis_widget, "⌨️ Raccourcis clavier")

        # Onglet 3 : À propos
        apropos_widget = QTextBrowser()
        apropos_widget.setHtml("""
            <div style="font-family: sans-serif; line-height: 1.6; color: #1E293B;">
                <h3 style="color: #2563EB;">EduPaie v1.2</h3>
                <p>Application de gestion des paiements scolaires avec calcul automatisé des soldes et émission de reçus officiels PDF numérotés.</p>
                <p><b>Devise :</b> Francs CFA (XOF / XAF)</p>
                <p><b>Base de données :</b> SQLite locale; les données ne sont pas chiffrées par l'application.</p>
                <p><b>Sécurité des données :</b> Les données sont stockées localement dans <code>data/edupaie.db</code>. Protégez l'accès à ce fichier avec les permissions Windows et faites-en régulièrement une copie de sauvegarde.</p>
                <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 15px 0;">
                <p style="font-size: 12px; color: #64748B;">Développé avec Python 3, PySide6 et FPDF2. Conçu spécialement pour la simplicité d'utilisation.</p>
            </div>
        """)
        tabs.addTab(apropos_widget, "ℹ️ À propos")

        layout.addWidget(tabs)

        # Bouton fermer
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
