"""
Service pour la construction des données de reçus.
Récupère les données du paiement et de l'élève depuis la base.
"""

import sqlite3
from repositories.paiement_repository import PaiementRepository
from repositories.eleve_repository import EleveRepository
from services.solde_service import SoldeService
from services.exceptions import ValidationError


class RecuService:
    """Service pour la construction des données de reçus."""
    
    # Nom de l'établissement (constante de configuration)
    NOM_ETABLISSEMENT = "Ecole Primaire Saint-Exupery"
    
    def __init__(self):
        """Initialise le service avec les repositories."""
        self.paiement_repository = PaiementRepository()
        self.eleve_repository = EleveRepository()
    
    def obtenir_donnees_recu(self, paiement_id):
        """
        Récupère toutes les données nécessaires pour générer un reçu.
        
        Args:
            paiement_id: ID du paiement
            
        Returns:
            dict: Dictionnaire avec toutes les données du reçu
            
        Raises:
            ValidationError: Si le paiement n'existe pas
        """
        from database.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT p.id, p.eleve_id, p.montant, p.date, p.mode, p.numero_recu, p.solde_apres
                FROM paiement p
                WHERE p.id = ?
                """,
                (paiement_id,)
            )
            paiement = cursor.fetchone()
            
            if not paiement:
                raise ValidationError("Le paiement n'existe pas")
            
            paiement_dict = dict(paiement)
            
            # Récupère l'élève
            eleve = self.eleve_repository.obtenir_par_id(paiement_dict['eleve_id'])
            if not eleve:
                raise ValidationError("L'élève associé au paiement n'existe pas")
            
            # Construit les données du reçu
            donnees_recu = {
                'etablissement': self.NOM_ETABLISSEMENT,
                'numero_recu': paiement_dict['numero_recu'],
                'date_paiement': paiement_dict['date'],
                'eleve_nom': eleve['nom'],
                'eleve_prenom': eleve['prenom'],
                'eleve_classe': eleve['classe'],
                'eleve_annee_scolaire': eleve['annee_scolaire'],
                'montant_paye': paiement_dict['montant'],
                'mode_paiement': paiement_dict['mode'],
                'total_du': eleve['total_du'],
                'solde_apres': paiement_dict['solde_apres'],  # Valeur stockée, pas recalculée
            }
            
            return donnees_recu
        finally:
            conn.close()
    
    def obtenir_donnees_recu_par_numero(self, numero_recu):
        """
        Récupère les données du reçu par numéro de reçu.
        
        Args:
            numero_recu: Numéro du reçu
            
        Returns:
            dict: Dictionnaire avec toutes les données du reçu
            
        Raises:
            ValidationError: Si le reçu n'existe pas
        """
        from database.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT p.id, p.eleve_id, p.montant, p.date, p.mode, p.numero_recu, p.solde_apres
                FROM paiement p
                WHERE p.numero_recu = ?
                """,
                (numero_recu,)
            )
            paiement = cursor.fetchone()
            
            if not paiement:
                raise ValidationError("Le reçu n'existe pas")
            
            paiement_dict = dict(paiement)
            
            # Récupère l'élève
            eleve = self.eleve_repository.obtenir_par_id(paiement_dict['eleve_id'])
            if not eleve:
                raise ValidationError("L'élève associé au reçu n'existe pas")
            
            # Construit les données du reçu
            donnees_recu = {
                'etablissement': self.NOM_ETABLISSEMENT,
                'numero_recu': paiement_dict['numero_recu'],
                'date_paiement': paiement_dict['date'],
                'eleve_nom': eleve['nom'],
                'eleve_prenom': eleve['prenom'],
                'eleve_classe': eleve['classe'],
                'eleve_annee_scolaire': eleve['annee_scolaire'],
                'montant_paye': paiement_dict['montant'],
                'mode_paiement': paiement_dict['mode'],
                'total_du': eleve['total_du'],
                'solde_apres': paiement_dict['solde_apres'],  # Valeur stockée
            }
            
            return donnees_recu
        finally:
            conn.close()
