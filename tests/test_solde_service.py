"""
Tests unitaires pour le service de calcul de solde.
"""

import unittest
from services.solde_service import SoldeService


class TestSoldeService(unittest.TestCase):
    """Tests pour SoldeService."""
    
    def test_calculer_solde_non_paye(self):
        """Test le calcul du solde pour un élève non payé."""
        total_du = 150000  # 150 000 FCFA
        total_paye = 0
        
        solde = SoldeService.calculer_solde(total_du, total_paye)
        
        self.assertEqual(solde, 150000)
    
    def test_calculer_solde_partiellement_paye(self):
        """Test le calcul du solde pour un élève partiellement payé."""
        total_du = 150000  # 150 000 FCFA
        total_paye = 50000  # 50 000 FCFA
        
        solde = SoldeService.calculer_solde(total_du, total_paye)
        
        self.assertEqual(solde, 100000)
    
    def test_calculer_solde_solde(self):
        """Test le calcul du solde pour un élève soldé."""
        total_du = 150000  # 150 000 FCFA
        total_paye = 150000  # 150 000 FCFA
        
        solde = SoldeService.calculer_solde(total_du, total_paye)
        
        self.assertEqual(solde, 0)
    
    def test_calculer_solde_total_du_zero(self):
        """Test le calcul du solde quand total_du est 0."""
        total_du = 0
        total_paye = 0
        
        solde = SoldeService.calculer_solde(total_du, total_paye)
        
        self.assertEqual(solde, 0)
    
    def test_determiner_statut_non_paye(self):
        """Test la détermination du statut pour un élève non payé."""
        total_du = 150000  # 150 000 FCFA
        total_paye = 0
        
        statut = SoldeService.determiner_statut(total_du, total_paye)
        
        self.assertEqual(statut, "Non payé")
    
    def test_determiner_statut_partiellement_paye(self):
        """Test la détermination du statut pour un élève partiellement payé."""
        total_du = 150000  # 150 000 FCFA
        total_paye = 50000  # 50 000 FCFA
        
        statut = SoldeService.determiner_statut(total_du, total_paye)
        
        self.assertEqual(statut, "Partiellement payé")
    
    def test_determiner_statut_solde(self):
        """Test la détermination du statut pour un élève soldé."""
        total_du = 150000  # 150 000 FCFA
        total_paye = 150000  # 150 000 FCFA
        
        statut = SoldeService.determiner_statut(total_du, total_paye)
        
        self.assertEqual(statut, "Soldé")
    
    def test_determiner_statut_total_du_zero(self):
        """Test la détermination du statut quand total_du est 0."""
        total_du = 0
        total_paye = 0
        
        statut = SoldeService.determiner_statut(total_du, total_paye)
        
        self.assertEqual(statut, "Soldé")
    
    def test_determiner_statut_plusieurs_paiements(self):
        """Test la détermination du statut avec plusieurs paiements."""
        total_du = 200000  # 200 000 FCFA
        total_paye = 200000  # 200 000 FCFA (plusieurs paiements cumulés)
        
        statut = SoldeService.determiner_statut(total_du, total_paye)
        
        self.assertEqual(statut, "Soldé")
    
    def test_determiner_statut_plusieurs_paiements_partiels(self):
        """Test la détermination du statut avec plusieurs paiements partiels."""
        total_du = 200000  # 200 000 FCFA
        total_paye = 100000  # 100 000 FCFA (plusieurs paiements cumulés)
        
        statut = SoldeService.determiner_statut(total_du, total_paye)
        
        self.assertEqual(statut, "Partiellement payé")
    
    def test_formater_monnaie_fcfa(self):
        """Test le formatage de monnaie en FCFA."""
        montant = 150000
        
        formate = SoldeService.formater_monnaie_fcfa(montant)
        
        self.assertEqual(formate, "150 000 FCFA")
    
    def test_formater_monnaie_fcfa_grand_montant(self):
        """Test le formatage de monnaie pour un grand montant."""
        montant = 1500000
        
        formate = SoldeService.formater_monnaie_fcfa(montant)
        
        self.assertEqual(formate, "1 500 000 FCFA")


if __name__ == '__main__':
    unittest.main()
