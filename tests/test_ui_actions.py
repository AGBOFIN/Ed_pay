"""
Tests d'interface pour les actions des boutons avec QT_QPA_PLATFORM=offscreen.
Teste la navigation et l'existence des boutons sans modifier la base de données.
"""

import unittest
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


class TestUIActions(unittest.TestCase):
    """Tests pour les actions des boutons de l'interface."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise l'application Qt une seule fois."""
        # Configure le platform offscreen pour les tests
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    @classmethod
    def tearDownClass(cls):
        """Nettoie après tous les tests."""
        pass
    
    def setUp(self):
        """Initialise la fenêtre principale avant chaque test."""
        self.main_window = MainWindow()
    
    def tearDown(self):
        """Nettoie après chaque test."""
        self.main_window.close()
    
    def test_navigation_menu_eleves(self):
        """Teste la navigation vers le menu Élèves."""
        # Appelle la méthode pour afficher la gestion des élèves
        self.main_window.afficher_gestion_eleves()
        
        # Vérifie que le widget de gestion des élèves est affiché
        self.assertIsNotNone(self.main_window.eleves_widget)
        self.assertEqual(self.main_window.centralWidget(), self.main_window.eleves_widget)
    
    def test_navigation_tableau_de_bord(self):
        """Teste la navigation vers le tableau de bord."""
        # Appelle la méthode pour afficher le tableau de bord
        self.main_window.afficher_tableau_de_bord()
        
        # Vérifie que le widget du tableau de bord est affiché
        self.assertIsNotNone(self.main_window.dashboard_widget)
        self.assertEqual(self.main_window.centralWidget(), self.main_window.dashboard_widget)
    
    def test_bouton_ajouter_eleve(self):
        """Teste que le bouton Ajouter existe et est connecté."""
        # Navigue vers la gestion des élèves
        self.main_window.afficher_gestion_eleves()
        
        # Vérifie que le bouton existe
        self.assertIsNotNone(self.main_window.eleves_widget.ajouter_btn)
        self.assertTrue(self.main_window.eleves_widget.ajouter_btn.isEnabled())
    
    def test_bouton_modifier_eleve(self):
        """Teste que le bouton Modifier existe."""
        # Navigue vers la gestion des élèves
        self.main_window.afficher_gestion_eleves()
        
        # Vérifie que le bouton existe
        self.assertIsNotNone(self.main_window.eleves_widget.modifier_btn)
        # Désactivé par défaut si aucune sélection
        self.assertFalse(self.main_window.eleves_widget.modifier_btn.isEnabled())
    
    def test_bouton_fiche_eleve(self):
        """Teste que le bouton Fiche élève existe."""
        # Navigue vers la gestion des élèves
        self.main_window.afficher_gestion_eleves()
        
        # Vérifie que le bouton existe
        self.assertIsNotNone(self.main_window.eleves_widget.fiche_btn)
        # Désactivé par défaut si aucune sélection
        self.assertFalse(self.main_window.eleves_widget.fiche_btn.isEnabled())
    
    def test_navigation_aller_retour(self):
        """Teste la navigation aller-retour entre les écrans."""
        # Va au tableau de bord
        self.main_window.afficher_tableau_de_bord()
        self.assertEqual(self.main_window.centralWidget(), self.main_window.dashboard_widget)
        
        # Va aux élèves
        self.main_window.afficher_gestion_eleves()
        self.assertEqual(self.main_window.centralWidget(), self.main_window.eleves_widget)
        
        # Revient au tableau de bord
        self.main_window.afficher_tableau_de_bord()
        self.assertEqual(self.main_window.centralWidget(), self.main_window.dashboard_widget)
        
        # Revient aux élèves
        self.main_window.afficher_gestion_eleves()
        self.assertEqual(self.main_window.centralWidget(), self.main_window.eleves_widget)


if __name__ == '__main__':
    unittest.main()
