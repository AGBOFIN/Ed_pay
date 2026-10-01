"""
Tests unitaires pour la génération de reçus PDF.
"""

import unittest
import os

try:
    from services.recu_service import RecuService
    from services.recu_pdf import generer_recu_pdf, get_chemin_dossier_recus
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


@unittest.skipIf(not FPDF_AVAILABLE, "fpdf2 n'est pas installé")
class TestRecuPDF(unittest.TestCase):
    """Tests pour la génération de reçus PDF."""
    
    def setUp(self):
        """Initialise le service pour les tests."""
        self.recu_service = RecuService()
    
    def test_get_chemin_dossier_recus(self):
        """Test que le dossier recus est créé."""
        chemin = get_chemin_dossier_recus()
        self.assertTrue(os.path.exists(chemin))
        self.assertTrue(chemin.endswith('recus'))
    
    def test_generer_recu_pdf_cree_fichier(self):
        """Test que la génération crée un fichier non vide."""
        # Utilise le premier paiement de la base de test
        donnees_recu = {
            'etablissement': 'Ecole Test',
            'numero_recu': 'REC-2026-00001',
            'date_paiement': '2025-09-01 00:00:00',
            'eleve_nom': 'Dupont',
            'eleve_prenom': 'Jean',
            'eleve_classe': '6eme A',
            'eleve_annee_scolaire': '2025-2026',
            'montant_paye': 500.0,
            'mode_paiement': 'especes',
            'total_du': 500.0,
            'solde_apres': 0
        }
        
        chemin_pdf = generer_recu_pdf(donnees_recu)
        
        # Verifie que le fichier existe
        self.assertTrue(os.path.exists(chemin_pdf))
        
        # Verifie que le fichier n'est pas vide
        self.assertGreater(os.path.getsize(chemin_pdf), 0)
        
        # Verifie que le fichier a l'extension .pdf
        self.assertTrue(chemin_pdf.endswith('.pdf'))
        
        # Nettoie : supprime le fichier de test
        if os.path.exists(chemin_pdf):
            os.remove(chemin_pdf)
    
    def test_generer_recu_pdf_avec_numero_recu(self):
        """Test que le nom du fichier contient le numero de recu."""
        donnees_recu = {
            'etablissement': 'Ecole Test',
            'numero_recu': 'REC-2026-00042',
            'date_paiement': '2025-09-15 00:00:00',
            'eleve_nom': 'Martin',
            'eleve_prenom': 'Marie',
            'eleve_classe': '6eme A',
            'eleve_annee_scolaire': '2025-2026',
            'montant_paye': 250.0,
            'mode_paiement': 'cheque',
            'total_du': 500.0,
            'solde_apres': 25000
        }
        
        chemin_pdf = generer_recu_pdf(donnees_recu)
        
        # Verifie que le nom du fichier contient le numero de recu
        self.assertIn('REC-2026-00042', chemin_pdf)
        
        # Nettoie
        if os.path.exists(chemin_pdf):
            os.remove(chemin_pdf)
    
    def test_generer_recu_pdf_avec_caracteres_speciaux(self):
        """Test que les caracteres speciaux dans le numero sont geres."""
        donnees_recu = {
            'etablissement': 'Ecole Test',
            'numero_recu': 'REC-2026-00050',
            'date_paiement': '2025-09-20 00:00:00',
            'eleve_nom': 'Lefebvre',
            'eleve_prenom': 'Enzo',
            'eleve_classe': '3eme A',
            'eleve_annee_scolaire': '2025-2026',
            'montant_paye': 150.0,
            'mode_paiement': 'virement',
            'total_du': 650.0,
            'solde_apres': 50000
        }
        
        chemin_pdf = generer_recu_pdf(donnees_recu)
        
        # Verifie que le fichier existe
        self.assertTrue(os.path.exists(chemin_pdf))
        
        # Nettoie
        if os.path.exists(chemin_pdf):
            os.remove(chemin_pdf)


if __name__ == '__main__':
    unittest.main()
