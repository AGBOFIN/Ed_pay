"""
Service pour le tableau de bord.
Assemble les indicateurs globaux pour le dashboard.
"""

from repositories.dashboard_repository import DashboardRepository
from repositories.eleve_repository import EleveRepository
from services.solde_service import SoldeService
from services.exceptions import ValidationError


class DashboardService:
    """Service pour le tableau de bord."""
    
    def __init__(self):
        """Initialise le service avec les repositories."""
        self.dashboard_repository = DashboardRepository()
        self.eleve_repository = EleveRepository()
    
    def obtenir_indicateurs(self):
        """
        Récupère tous les indicateurs du tableau de bord.
        
        Returns:
            dict: Dictionnaire avec les indicateurs suivants :
                - nb_eleves: nombre total d'élèves
                - total_encaisse: montant total encaissé (en francs CFA)
                - total_restant_du: montant total restant dû (en francs CFA)
                - nb_eleves_non_soldes: nombre d'élèves non soldés
        """
        # Récupère les indicateurs de base depuis le repository
        indicateurs = self.dashboard_repository.obtenir_indicateurs_synthetiques()
        
        # Calcule le nombre d'élèves non soldés en utilisant SoldeService (une seule source de vérité)
        eleves = self.obtenir_liste_eleves_avec_statuts()
        eleves_non_soldes = [e for e in eleves if e['statut'] != "Soldé"]
        indicateurs['nb_eleves_non_soldes'] = len(eleves_non_soldes)
        
        return indicateurs
    
    def obtenir_liste_eleves_avec_statuts(self):
        """
        Récupère la liste de tous les élèves avec leurs statuts de paiement.
        
        Returns:
            list: Liste de dictionnaires avec données de l'élève + statut
        """
        eleves = self.eleve_repository.lister()
        
        # Ajoute le statut à chaque élève
        for eleve in eleves:
            total_du = eleve['total_du']
            total_paye = eleve.get('total_paye', 0)
            solde = SoldeService.calculer_solde(total_du, total_paye)
            statut = SoldeService.determiner_statut(total_du, total_paye)
            
            eleve['solde'] = solde
            eleve['statut'] = statut
        
        return eleves
    
    def obtenir_liste_eleves_filtree_par_statut(self, statut):
        """
        Récupère la liste des élèves filtrée par statut.

        Args:
            statut: Statut de filtrage ("Tous", "Soldé", "Partiellement payé", "Non payé")

        Returns:
            list: Liste filtrée d'élèves
        """
        eleves = self.obtenir_liste_eleves_avec_statuts()

        if statut == "Tous":
            return eleves

        return [eleve for eleve in eleves if eleve['statut'] == statut]
