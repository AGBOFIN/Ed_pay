"""
Tests d'interface complets avec QT_QPA_PLATFORM=offscreen.
Utilise une copie temporaire de la base de données.
"""

import unittest
import os
import shutil
import tempfile
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from ui.main_window import MainWindow
import database.connection as db_connection
import utils.resource_utils as resource_utils
from unittest import mock


class TestUIActions(unittest.TestCase):
    """Tests pour les actions des boutons de l'interface."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise l'application Qt une seule fois."""
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
        
        # Crée une copie temporaire de la base de données
        cls.db_original = os.path.join(os.path.dirname(__file__), '..', 'data', 'edupaie.db')
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_temp = os.path.join(cls.temp_dir, 'edupaie.db')
        shutil.copy2(cls.db_original, cls.db_temp)
        
        # Redirige vers la copie temporaire
        cls._patches = [
            mock.patch.object(db_connection, 'get_database_path', lambda: cls.db_temp),
            mock.patch.object(db_connection, 'ensure_data_dirs', lambda: None),
            mock.patch.object(db_connection, 'copy_initial_database_if_needed', lambda: None),
        ]
        for p in cls._patches:
            p.start()
    
    @classmethod
    def tearDownClass(cls):
        """Nettoie après tous les tests."""
        for p in cls._patches:
            p.stop()
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Initialise la fenêtre principale avant chaque test."""
        self.main_window = MainWindow()
    
    def tearDown(self):
        """Nettoie après chaque test."""
        self.main_window.close()
    
    def test_navigation_complete(self):
        """Teste la navigation complète élèves -> tableau de bord -> élèves."""
        self.main_window.afficher_gestion_eleves()
        self.assertEqual(self.main_window.stack.currentWidget(), self.main_window.eleves_widget)
        
        self.main_window.afficher_tableau_de_bord()
        self.assertEqual(self.main_window.stack.currentWidget(), self.main_window.dashboard_widget)
        
        self.main_window.afficher_gestion_eleves()
        self.assertEqual(self.main_window.stack.currentWidget(), self.main_window.eleves_widget)
    
    def test_boutons_existent(self):
        """Teste que tous les boutons existent."""
        self.main_window.afficher_gestion_eleves()
        
        self.assertIsNotNone(self.main_window.eleves_widget.ajouter_btn)
        self.assertIsNotNone(self.main_window.eleves_widget.modifier_btn)
        self.assertIsNotNone(self.main_window.eleves_widget.supprimer_btn)
        self.assertIsNotNone(self.main_window.eleves_widget.paiement_btn)
        self.assertIsNotNone(self.main_window.eleves_widget.fiche_btn)
    
    def test_qstackedwidget_configuration(self):
        """Teste que QStackedWidget est correctement configuré."""
        self.assertEqual(type(self.main_window.centralWidget()).__name__, 'QStackedWidget')
        self.assertEqual(self.main_window.stack.count(), 2)
        self.assertIsNotNone(self.main_window.dashboard_widget)
        self.assertIsNotNone(self.main_window.eleves_widget)


if __name__ == '__main__':
    unittest.main()
