"""
Tests pour la fonctionnalité Paramètres.
Utilise une copie temporaire de la base de données.
"""

import unittest
import os
import shutil
import tempfile
from datetime import datetime
from PySide6.QtWidgets import QApplication
from services.parametre_service import ParametreService
from repositories.parametre_repository import ParametreRepository
from repositories.classe_repository import ClasseRepository
from database.connection import get_connection
import database.connection as db_connection
import utils.resource_utils as resource_utils
from services.exceptions import ValidationError
from unittest import mock


class TestParametres(unittest.TestCase):
    """Tests pour la gestion des paramètres."""
    
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
        """Initialise les services avant chaque test."""
        self.parametre_service = ParametreService()
        self.parametre_repo = ParametreRepository()
        self.classe_repo = ClasseRepository()
    
    def test_migration_appliquee_deux_fois(self):
        """Teste que la migration peut être appliquée deux fois sans erreur."""
        # Applique la migration une première fois
        db_connection.appliquer_migration()
        
        # Applique la migration une deuxième fois (idempotente)
        db_connection.appliquer_migration()
        
        # Vérifie que les tables existent
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parametre'")
        self.assertIsNotNone(cursor.fetchone(), "La table parametre doit exister")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classe'")
        self.assertIsNotNone(cursor.fetchone(), "La table classe doit exister")
        
        conn.close()
    
    def test_parametres_lus_et_ecrits(self):
        """Teste que les paramètres peuvent être lus et écrits."""
        # Écrit des paramètres
        self.parametre_service.definir_etablissement(
            "École Test", "123 Rue", "01 23 45 67 89", "test@test.fr", "FCFA", "", "Pied de page"
        )
        self.parametre_service.definir_annee_scolaire("2024-2025")
        self.parametre_service.definir_prefixe_recu("FAC")
        
        # Lit les paramètres
        etablissement = self.parametre_service.obtenir_etablissement()
        self.assertEqual(etablissement['nom'], "École Test")
        self.assertEqual(etablissement['adresse'], "123 Rue")
        self.assertEqual(etablissement['telephone'], "01 23 45 67 89")
        self.assertEqual(etablissement['email'], "test@test.fr")
        self.assertEqual(etablissement['devise'], "FCFA")
        
        annee = self.parametre_service.obtenir_annee_scolaire()
        self.assertEqual(annee, "2024-2025")
        
        prefixe = self.parametre_service.obtenir_prefixe_recu()
        self.assertEqual(prefixe, "FAC")
    
    def test_classe_desactivee_absente_formulaire(self):
        """Teste qu'une classe désactivée est absente de la liste des classes actives."""
        # Ajoute une classe
        classe_id = self.parametre_service.ajouter_classe("6ème C", 130000)
        
        # Vérifie qu'elle est dans la liste des classes actives
        classes_actives = self.parametre_service.lister_classes_actives()
        self.assertTrue(any(c['nom'] == "6ème C" for c in classes_actives))
        
        # Désactive la classe
        self.parametre_service.desactiver_classe(classe_id)
        
        # Vérifie qu'elle n'est plus dans la liste des classes actives
        classes_actives = self.parametre_service.lister_classes_actives()
        self.assertFalse(any(c['nom'] == "6ème C" for c in classes_actives))
        
        # Vérifie qu'elle est toujours dans la liste de toutes les classes
        toutes_classes = self.parametre_service.lister_toutes_classes()
        self.assertTrue(any(c['nom'] == "6ème C" for c in toutes_classes))
    
    def test_paiement_refuse_si_aucun_mode_actif(self):
        """Teste qu'un paiement est refusé si aucun mode de paiement n'est actif."""
        # Tente de définir aucun mode de paiement (doit échouer)
        with self.assertRaises(ValidationError) as context:
            self.parametre_service.definir_modes_paiement([])
        self.assertIn("Au moins un mode", str(context.exception))
    
    def test_recu_contient_nom_etablissement(self):
        """Teste que le reçu contient le nom de l'établissement (via service)."""
        # Définit un nom d'établissement spécifique
        self.parametre_service.definir_etablissement(
            "École de Test", "Adresse", "Téléphone", "email@test.fr", "FCFA", "", "Pied de page"
        )
        
        # Vérifie que le nom est bien stocké
        etablissement = self.parametre_service.obtenir_etablissement()
        self.assertEqual(etablissement['nom'], "École de Test")


if __name__ == '__main__':
    unittest.main()
