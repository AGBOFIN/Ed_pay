"""
Tests unitaires pour le service d'enregistrement de paiements.
"""

import unittest
from datetime import datetime, timedelta
from services.paiement_service import PaiementService, ValidationError


class TestPaiementService(unittest.TestCase):
    """Tests pour PaiementService."""
    
    def setUp(self):
        """Initialise le service pour les tests."""
        self.service = PaiementService()
    
    def test_valider_montant_negatif(self):
        """Test la validation d'un montant négatif."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(1, -50, "2025-09-15", "espèces")
        self.assertIn("strictement positif", str(context.exception))
    
    def test_valider_montant_zero(self):
        """Test la validation d'un montant nul."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(1, 0, "2025-09-15", "espèces")
        self.assertIn("strictement positif", str(context.exception))
    
    def test_valider_montant_non_numerique(self):
        """Test la validation d'un montant non numérique."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(1, "abc", "2025-09-15", "espèces")
        self.assertIn("nombre", str(context.exception))
    
    def test_valider_date_future(self):
        """Test la validation d'une date future."""
        date_future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(1, 50, date_future, "espèces")
        self.assertIn("futur", str(context.exception))
    
    def test_valider_date_invalide(self):
        """Test la validation d'une date invalide."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(1, 50, "2025-13-32", "espèces")
        self.assertIn("format", str(context.exception))
    
    def test_valider_mode_invalide(self):
        """Test la validation d'un mode de paiement invalide."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(1, 50, "2025-09-15", "carte bancaire")
        self.assertIn("mode", str(context.exception).lower())
    
    def test_valider_mode_vide(self):
        """Test la validation d'un mode vide."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(1, 50, "2025-09-15", "")
        self.assertIn("mode", str(context.exception).lower())
    
    def test_valider_eleve_inexistant(self):
        """Test la validation d'un élève inexistant."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(99999, 50, "2025-09-15", "espèces")
        self.assertIn("n'existe pas", str(context.exception))
    
    def test_valider_eleve_vide(self):
        """Test la validation d'un élève vide."""
        with self.assertRaises(ValidationError) as context:
            self.service.valider_donnees_paiement(None, 50, "2025-09-15", "espèces")
        self.assertIn("obligatoire", str(context.exception))
    
    def test_modes_paiement(self):
        """Test que les modes de paiement sont corrects."""
        modes_attendus = ['espèces', 'chèque', 'virement', 'mobile money']
        self.assertEqual(self.service.MODES_PAIEMENT, modes_attendus)
    
    def test_valider_montant_valide(self):
        """Test la validation d'un montant valide."""
        # Ne doit pas lever d'exception
        try:
            self.service.valider_donnees_paiement(1, 50, "2025-09-15", "espèces")
        except ValidationError as e:
            if "n'existe pas" not in str(e):
                self.fail(f"Validation inattendue : {e}")
    
    def test_valider_date_valide(self):
        """Test la validation d'une date valide (passée ou aujourd'hui)."""
        date_passee = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        date_aujourdhui = datetime.now().strftime("%Y-%m-%d")
        
        # Ne doit pas lever d'exception pour la date passée
        try:
            self.service.valider_donnees_paiement(1, 50, date_passee, "espèces")
        except ValidationError as e:
            if "n'existe pas" not in str(e):
                self.fail(f"Validation inattendue pour date passée : {e}")
        
        # Ne doit pas lever d'exception pour la date d'aujourd'hui
        try:
            self.service.valider_donnees_paiement(1, 50, date_aujourdhui, "espèces")
        except ValidationError as e:
            if "n'existe pas" not in str(e):
                self.fail(f"Validation inattendue pour date aujourd'hui : {e}")
    
    def test_valider_mode_valide(self):
        """Test la validation des modes valides."""
        modes_valides = ['espèces', 'chèque', 'virement', 'mobile money']
        
        for mode in modes_valides:
            try:
                self.service.valider_donnees_paiement(1, 50, "2025-09-15", mode)
            except ValidationError as e:
                if "n'existe pas" not in str(e):
                    self.fail(f"Validation inattendue pour mode {mode} : {e}")


if __name__ == '__main__':
    unittest.main()
