"""
Service pour le calcul du solde et du statut de paiement.
Fonctions pures sans accès à la base de données.
Les montants sont en francs CFA (entiers).
"""


class SoldeService:
    """Service pour les calculs de solde et statut."""
    
    @staticmethod
    def calculer_solde(total_du, total_paye):
        """
        Calcule le solde restant à payer.
        
        Args:
            total_du: Montant total dû en francs CFA (entier)
            total_paye: Montant total payé en francs CFA (entier)
            
        Returns:
            int: Solde restant en francs CFA (entier, peut être négatif si trop payé)
        """
        return total_du - total_paye
    
    @staticmethod
    def determiner_statut(total_du, total_paye):
        """
        Détermine le statut de paiement d'un élève.
        
        Args:
            total_du: Montant total dû en francs CFA (entier)
            total_paye: Montant total payé en francs CFA (entier)
            
        Returns:
            str: Statut de paiement ("Soldé", "Partiellement payé", "Non payé")
        """
        solde = SoldeService.calculer_solde(total_du, total_paye)
        
        # Si le solde est 0 (ou si total_du est 0), l'élève est soldé
        if solde == 0:
            return "Soldé"
        
        # Si le solde est positif et qu'il y a eu au moins un paiement
        if total_paye > 0:
            return "Partiellement payé"
        
        # Sinon, aucun paiement
        return "Non payé"
    
    @staticmethod
    def formater_monnaie_fcfa(montant):
        """
        Formate un montant en francs CFA avec séparateur de milliers.
        
        Args:
            montant: Montant en francs CFA (entier)
            
        Returns:
            str: Montant formaté (ex: "150 000 FCFA")
        """
        return f"{montant:,} FCFA".replace(",", " ")
