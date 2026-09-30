"""
Service pour la fiche détaillée d'un élève.
Regroupe les données de l'élève et ses paiements.
"""

from repositories.eleve_repository import EleveRepository
from repositories.paiement_repository import PaiementRepository
from services.solde_service import SoldeService
from services.eleve_service import ValidationError


class FicheEleveService:
    """Service pour la construction des données de la fiche élève."""
    
    def __init__(self):
        """Initialise le service avec les repositories."""
        self.eleve_repository = EleveRepository()
        self.paiement_repository = PaiementRepository()
    
    def obtenir_donnees_fiche(self, eleve_id):
        """
        Récupère toutes les données nécessaires pour la fiche d'un élève.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            dict: Dictionnaire avec toutes les données de la fiche
            
        Raises:
            ValidationError: Si l'élève n'existe pas
        """
        # Récupère l'élève
        eleve = self.eleve_repository.obtenir_par_id(eleve_id)
        if not eleve:
            raise ValidationError("L'élève n'existe pas")
        
        # Récupère les paiements
        paiements = self.paiement_repository.lister_par_eleve(eleve_id)
        
        # Calcule les totaux
        total_du_centimes = eleve['total_du']
        total_paye_centimes = sum(p['montant'] * 100 for p in paiements)
        solde_actuel = SoldeService.calculer_solde(total_du_centimes, total_paye_centimes)
        statut = SoldeService.determiner_statut(total_du_centimes, total_paye_centimes)
        
        # Construit les données de la fiche
        donnees_fiche = {
            'eleve': eleve,
            'total_du': total_du_centimes,
            'total_paye': total_paye_centimes,
            'solde': solde_actuel,
            'statut': statut,
            'paiements': paiements,
            'nb_paiements': len(paiements)
        }
        
        return donnees_fiche
