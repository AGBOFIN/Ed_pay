"""
Test pour vérifier les calculs de solde après paiement.
Utilise une copie temporaire de la base de données.
"""

import unittest
import os
import shutil
import tempfile
from datetime import datetime
from PySide6.QtWidgets import QApplication
from services.paiement_service import PaiementService
from services.fiche_eleve_service import FicheEleveService
from services.eleve_service import EleveService
from repositories.eleve_repository import EleveRepository
from repositories.paiement_repository import PaiementRepository
from services.eleve_service import ValidationError
from unittest import mock
from tests.database_helpers import (
    create_encrypted_test_database,
    database_connection_patches,
)


class TestCalculSolde(unittest.TestCase):
    """Tests pour les calculs de solde."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise l'application Qt une seule fois."""
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
        
        # Crée une copie temporaire de la base de données
        cls.db_original = os.path.join(os.path.dirname(__file__), '..', 'data', 'edupaie-seed.db')
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_plain = os.path.join(cls.temp_dir, 'edupaie-plain.db')
        cls.db_temp = os.path.join(cls.temp_dir, 'edupaie-encrypted.db')
        shutil.copy2(cls.db_original, cls.db_plain)
        cls.key_temp = create_encrypted_test_database(cls.db_plain, cls.db_temp)
        os.remove(cls.db_plain)
        
        # Redirige vers la copie temporaire
        cls._patches = database_connection_patches(cls.db_temp, cls.key_temp)
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
        self.paiement_service = PaiementService()
        self.fiche_service = FicheEleveService()
        self.eleve_service = EleveService()
        self.eleve_repo = EleveRepository()
        self.paiement_repo = PaiementRepository()
    
    def test_paiement_50000_solde_250000(self):
        """Teste qu'un paiement de 50 000 FCFA sur un solde de 250 000 donne solde_apres = 200 000."""
        # Crée un élève neuf avec total_du = 250 000
        eleve_id = self.eleve_service.ajouter_eleve(
            "Test", "Élève", "6ème", "2025-2026", 250000
        )
        
        # Vérifie que l'élève a été créé
        eleve = self.eleve_repo.obtenir_par_id(eleve_id)
        self.assertIsNotNone(eleve, "L'élève doit être créé")
        self.assertEqual(eleve['total_du'], 250000, "total_du doit être 250 000")
        
        # Vérifie qu'il n'y a pas de paiements
        total_paye_initial = self.paiement_repo.total_paye_par_eleve(eleve_id)
        self.assertEqual(total_paye_initial, 0, "total_paye initial doit être 0")
        
        # Enregistre un paiement de 50 000 FCFA
        date = datetime.now().strftime("%Y-%m-%d")
        numero_recu, solde_apres = self.paiement_service.enregistrer_paiement(
            eleve_id, 50000, date, "espèces"
        )
        
        # Vérifie que solde_apres = 200 000
        self.assertEqual(solde_apres, 200000, f"solde_apres doit être 200 000, mais est {solde_apres}")
        
        # Vérifie la fiche élève
        donnees_fiche = self.fiche_service.obtenir_donnees_fiche(eleve_id)
        self.assertEqual(donnees_fiche['total_paye'], 50000, "total_paye doit être 50 000")
        self.assertEqual(donnees_fiche['solde'], 200000, "solde doit être 200 000")
        self.assertEqual(donnees_fiche['statut'], "Partiellement payé", "statut doit être 'Partiellement payé'")
        
        # Vérifie qu'un paiement de 250 000 supplémentaire est refusé
        with self.assertRaises(ValidationError) as context:
            self.paiement_service.enregistrer_paiement(
                eleve_id, 250000, date, "espèces"
            )
        self.assertIn("dépasse le solde", str(context.exception), "Le paiement excessif doit être refusé")


if __name__ == '__main__':
    unittest.main()
