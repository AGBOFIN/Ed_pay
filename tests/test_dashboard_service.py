"""
Tests unitaires pour le service de tableau de bord.
"""

import unittest
from services.dashboard_service import DashboardService
from services.solde_service import SoldeService


class TestDashboardService(unittest.TestCase):
    """Tests pour DashboardService."""
    
    def setUp(self):
        """Initialise le service avant chaque test."""
        self.dashboard_service = DashboardService()
    
    def test_obtenir_indicateurs(self):
        """Teste la récupération des indicateurs globaux."""
        indicateurs = self.dashboard_service.obtenir_indicateurs()
        
        # Vérifie que toutes les clés sont présentes
        self.assertIn('nb_eleves', indicateurs)
        self.assertIn('total_encaisse', indicateurs)
        self.assertIn('total_restant_du', indicateurs)
        self.assertIn('nb_eleves_non_soldes', indicateurs)
        
        # Vérifie que les valeurs sont des nombres positifs ou nuls
        self.assertGreaterEqual(indicateurs['nb_eleves'], 0)
        self.assertGreaterEqual(indicateurs['total_encaisse'], 0)
        self.assertGreaterEqual(indicateurs['total_restant_du'], 0)
        self.assertGreaterEqual(indicateurs['nb_eleves_non_soldes'], 0)
        
        # Le nombre d'élèves non soldés ne peut pas dépasser le nombre total
        self.assertLessEqual(indicateurs['nb_eleves_non_soldes'], indicateurs['nb_eleves'])
    
    def test_obtenir_liste_eleves_avec_statuts(self):
        """Teste la récupération de la liste des élèves avec statuts."""
        eleves = self.dashboard_service.obtenir_liste_eleves_avec_statuts()
        
        # Vérifie que la liste n'est pas vide (base de test peuplée)
        self.assertGreater(len(eleves), 0)
        
        # Vérifie que chaque élève a les champs requis
        for eleve in eleves:
            self.assertIn('id', eleve)
            self.assertIn('nom', eleve)
            self.assertIn('prenom', eleve)
            self.assertIn('classe', eleve)
            self.assertIn('total_du', eleve)
            self.assertIn('total_paye', eleve)
            self.assertIn('solde', eleve)
            self.assertIn('statut', eleve)
            
            # Vérifie que le statut est valide
            self.assertIn(eleve['statut'], ["Soldé", "Partiellement payé", "Non payé"])
            
            # Vérifie la cohérence du solde
            solde_calcule = SoldeService.calculer_solde(eleve['total_du'], eleve['total_paye'])
            self.assertEqual(eleve['solde'], solde_calcule)
            
            # Vérifie la cohérence du statut
            statut_calcule = SoldeService.determiner_statut(eleve['total_du'], eleve['total_paye'])
            self.assertEqual(eleve['statut'], statut_calcule)
    
    def test_obtenir_liste_eleves_filtree_par_statut_tous(self):
        """Teste le filtrage par statut 'Tous'."""
        eleves = self.dashboard_service.obtenir_liste_eleves_filtree_par_statut("Tous")
        eleves_complets = self.dashboard_service.obtenir_liste_eleves_avec_statuts()
        
        # Le filtre 'Tous' doit retourner tous les élèves
        self.assertEqual(len(eleves), len(eleves_complets))
    
    def test_obtenir_liste_eleves_filtree_par_statut_solde(self):
        """Teste le filtrage par statut 'Soldé'."""
        eleves = self.dashboard_service.obtenir_liste_eleves_filtree_par_statut("Soldé")
        
        # Vérifie que tous les élèves filtrés sont soldés
        for eleve in eleves:
            self.assertEqual(eleve['statut'], "Soldé")
            self.assertEqual(eleve['solde'], 0)
    
    def test_obtenir_liste_eleves_filtree_par_statut_partiel(self):
        """Teste le filtrage par statut 'Partiellement payé'."""
        eleves = self.dashboard_service.obtenir_liste_eleves_filtree_par_statut("Partiellement payé")
        
        # Vérifie que tous les élèves filtrés sont partiellement payés
        for eleve in eleves:
            self.assertEqual(eleve['statut'], "Partiellement payé")
            # Note: le solde peut être négatif si les paiements dépassent le total_du
            # Dans ce cas, on vérifie seulement qu'il y a eu des paiements
            self.assertGreater(eleve['total_paye'], 0)
    
    def test_obtenir_liste_eleves_filtree_par_statut_non_paye(self):
        """Teste le filtrage par statut 'Non payé'."""
        eleves = self.dashboard_service.obtenir_liste_eleves_filtree_par_statut("Non payé")
        
        # Vérifie que tous les élèves filtrés sont non payés
        for eleve in eleves:
            self.assertEqual(eleve['statut'], "Non payé")
            self.assertEqual(eleve['total_paye'], 0)
            self.assertGreater(eleve['solde'], 0)
    
    def test_coherence_indicateurs(self):
        """Teste la cohérence entre les indicateurs et la liste des élèves."""
        indicateurs = self.dashboard_service.obtenir_indicateurs()
        eleves = self.dashboard_service.obtenir_liste_eleves_avec_statuts()
        
        # Le nombre d'élèves doit correspondre
        self.assertEqual(indicateurs['nb_eleves'], len(eleves))
        
        # Le total encaissé doit correspondre à la somme des paiements
        total_paye_calcul = sum(e['total_paye'] for e in eleves)
        self.assertEqual(indicateurs['total_encaisse'], total_paye_calcul)
        
        # Le total restant dû doit correspondre à la somme des soldes
        total_restant_du_calcul = sum(e['solde'] for e in eleves)
        self.assertEqual(indicateurs['total_restant_du'], total_restant_du_calcul)
        
        # Le nombre d'élèves non soldés doit correspondre aux élèves dont le statut n'est pas "Soldé"
        nb_eleves_non_soldes_calcul = len([e for e in eleves if e['statut'] != "Soldé"])
        self.assertEqual(indicateurs['nb_eleves_non_soldes'], nb_eleves_non_soldes_calcul)
    
    def test_aucun_solde_negatif(self):
        """Vérifie qu'aucun élève n'a de solde négatif dans le jeu de test."""
        eleves = self.dashboard_service.obtenir_liste_eleves_avec_statuts()
        for eleve in eleves:
            self.assertGreaterEqual(eleve['solde'], 0, 
                f"L'élève {eleve['nom']} {eleve['prenom']} a un solde négatif : {eleve['solde']}")
    
    def test_trigger_refuse_paiement_excessif(self):
        """Vérifie que le trigger SQL refuse un paiement qui dépasse le solde."""
        import sqlite3
        from database.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Tente d'insérer un paiement qui dépasse le solde
            cursor.execute("""
                INSERT INTO paiement (eleve_id, montant, date, mode, numero_recu, solde_apres)
                VALUES (1, 999999, '2025-09-01', 'espèces', 'REC-2026-99999', -999999)
            """)
            self.fail("Le trigger aurait dû rejeter ce paiement")
        except sqlite3.IntegrityError as e:
            # Vérifie que l'erreur mentionne le solde
            self.assertIn("solde", str(e).lower())
        finally:
            conn.close()


if __name__ == '__main__':
    unittest.main()
