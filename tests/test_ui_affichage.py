"""
Tests d'affichage de l'interface utilisateur avec QT_QPA_PLATFORM=offscreen.
Vérifie que les tableaux affichent correctement toutes les données.
"""

import unittest
import os
from PySide6.QtWidgets import QApplication
from ui.dashboard_widget import DashboardWidget
from ui.eleves_widget import ElevesWidget


class TestUIAffichage(unittest.TestCase):
    """Tests pour l'affichage de l'UI."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise l'application Qt une seule fois."""
        # Configure le platform offscreen pour les tests
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def setUp(self):
        """Initialise les widgets avant chaque test."""
        self.dashboard = DashboardWidget()
        self.eleves_widget = ElevesWidget()
    
    def tearDown(self):
        """Nettoie après chaque test."""
        self.dashboard.close()
        self.eleves_widget.close()
    
    def test_dashboard_affiche_20_lignes_completes(self):
        """Vérifie que le tableau de bord affiche 20 lignes complètes."""
        # Attend que les données soient chargées
        import time
        time.sleep(0.1)
        
        table = self.dashboard.table
        row_count = table.rowCount()
        
        # Vérifie qu'il y a 20 lignes
        self.assertEqual(row_count, 20, "Le tableau doit afficher 20 élèves")
        
        # Vérifie que chaque ligne a toutes ses cellules non vides
        for row in range(row_count):
            for col in range(8):  # 8 colonnes
                item = table.item(row, col)
                self.assertIsNotNone(item, f"Cellule ({row}, {col}) ne doit pas être None")
                text = item.text()
                self.assertIsNot(text, "", f"Cellule ({row}, {col}) ne doit pas être vide")
    
    def test_dashboard_en_tetes_contiennent_fcfa(self):
        """Vérifie que les en-têtes du tableau de bord contiennent FCFA."""
        table = self.dashboard.table
        headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]
        
        # Vérifie que les en-têtes de montants contiennent FCFA
        self.assertIn("FCFA", headers[4], "En-tête Total dû doit contenir FCFA")
        self.assertIn("FCFA", headers[5], "En-tête Payé doit contenir FCFA")
        self.assertIn("FCFA", headers[6], "En-tête Solde doit contenir FCFA")
        
        # Vérifie qu'il n'y a plus de €
        for header in headers:
            self.assertNotIn("€", header, f"En-tête '{header}' ne doit pas contenir €")
    
    def test_eleves_widget_affiche_20_lignes_completes(self):
        """Vérifie que la liste des élèves affiche 20 lignes complètes."""
        # Attend que les données soient chargées
        import time
        time.sleep(0.1)
        
        model = self.eleves_widget.table.model()
        row_count = model.rowCount()
        
        # Vérifie qu'il y a 20 lignes
        self.assertEqual(row_count, 20, "Le tableau doit afficher 20 élèves")
        
        # Vérifie que chaque ligne a toutes ses cellules non vides
        for row in range(row_count):
            for col in range(9):  # 9 colonnes
                index = model.index(row, col)
                text = model.data(index)
                self.assertIsNot(text, "", f"Cellule ({row}, {col}) ne doit pas être vide")
    
    def test_eleves_widget_en_tetes_contiennent_fcfa(self):
        """Vérifie que les en-têtes de la liste des élèves contiennent FCFA."""
        from PySide6.QtCore import Qt
        model = self.eleves_widget.table.model()
        headers = []
        for col in range(model.columnCount()):
            header = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            headers.append(header)
        
        # Vérifie que les en-têtes de montants contiennent FCFA
        self.assertIn("FCFA", headers[5], "En-tête Total dû doit contenir FCFA")
        self.assertIn("FCFA", headers[6], "En-tête Payé doit contenir FCFA")
        self.assertIn("FCFA", headers[7], "En-tête Solde doit contenir FCFA")
        
        # Vérifie qu'il n'y a plus de €
        for header in headers:
            if header:
                self.assertNotIn("€", header, f"En-tête '{header}' ne doit pas contenir €")


if __name__ == '__main__':
    unittest.main()
