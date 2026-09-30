"""
Service pour l'enregistrement des paiements.
Contient la logique métier et les validations.
"""

import sqlite3
from datetime import datetime
from repositories.paiement_repository import PaiementRepository
from repositories.eleve_repository import EleveRepository
from services.solde_service import SoldeService
from services.eleve_service import ValidationError


class PaiementService:
    """Service pour les opérations métier sur les paiements."""
    
    MODES_PAIEMENT = ['espèces', 'chèque', 'virement', 'mobile money']
    
    def __init__(self):
        """Initialise le service avec les repositories."""
        self.paiement_repository = PaiementRepository()
        self.eleve_repository = EleveRepository()
    
    def valider_donnees_paiement(self, eleve_id, montant, date, mode):
        """
        Valide les données d'un paiement.
        
        Args:
            eleve_id: ID de l'élève
            montant: Montant du paiement
            date: Date du paiement
            mode: Mode de paiement
            
        Raises:
            ValidationError: Si les données ne sont pas valides
        """
        # Validation de l'élève
        if not eleve_id:
            raise ValidationError("L'élève est obligatoire")
        
        eleve = self.eleve_repository.obtenir_par_id(eleve_id)
        if not eleve:
            raise ValidationError("L'élève n'existe pas")
        
        # Validation du montant
        try:
            montant_float = float(montant)
            if montant_float <= 0:
                raise ValidationError("Le montant doit être strictement positif")
        except (ValueError, TypeError):
            raise ValidationError("Le montant doit être un nombre")
        
        # Validation de la date
        if not date:
            raise ValidationError("La date est obligatoire")
        
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_aujourdhui = datetime.now()
            
            if date_obj > date_aujourdhui:
                raise ValidationError("La date ne peut pas être dans le futur")
        except ValueError:
            raise ValidationError("La date doit être au format YYYY-MM-DD")
        
        # Validation du mode
        if not mode or mode not in self.MODES_PAIEMENT:
            raise ValidationError(f"Le mode doit être l'un de : {', '.join(self.MODES_PAIEMENT)}")
    
    def enregistrer_paiement(self, eleve_id, montant, date, mode):
        """
        Enregistre un paiement pour un élève avec validation et vérification du solde.
        
        Args:
            eleve_id: ID de l'élève
            montant: Montant du paiement en francs CFA (entier)
            date: Date du paiement (format YYYY-MM-DD)
            mode: Mode de paiement
            
        Returns:
            tuple: (numero_recu, solde_apres)
            
        Raises:
            ValidationError: Si les données ne sont pas valides ou si le solde devient négatif
        """
        # Validation des données
        self.valider_donnees_paiement(eleve_id, montant, date, mode)
        
        # Le montant est déjà en francs CFA (entier)
        montant_fcfa = int(montant)
        
        # Obtention de la connexion pour la transaction
        from database.connection import get_connection
        conn = get_connection()
        
        try:
            # Début de la transaction avec BEGIN IMMEDIATE (verrou immédiat)
            conn.execute("BEGIN IMMEDIATE")
            
            # Récupère le total_du de l'élève (relecture dans la transaction)
            total_du_fcfa = self.paiement_repository.obtenir_total_du_eleve(conn, eleve_id)
            
            # Récupère le total déjà payé (relecture dans la transaction)
            total_paye_fcfa = self.paiement_repository.obtenir_total_paye_eleve(conn, eleve_id)
            
            # Calcule le solde actuel
            solde_actuel = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa)
            
            # Vérifie que le paiement ne dépasse pas le solde
            if montant_fcfa > solde_actuel:
                solde_max_formate = SoldeService.formater_monnaie_fcfa(solde_actuel)
                raise ValidationError(
                    f"Le paiement dépasse le solde restant. "
                    f"Solde maximum acceptable : {solde_max_formate}"
                )
            
            # Calcule le nouveau solde après ce paiement
            nouveau_solde = SoldeService.calculer_solde(total_du_fcfa, total_paye_fcfa + montant_fcfa)
            
            # Génère le numéro de reçu (compteur par année)
            annee = datetime.now().year
            numero_recu = self.paiement_repository.incrementer_sequence_recu(conn, str(annee))
            
            # Insère le paiement avec solde_apres
            date_str = f"{date} 00:00:00"
            self.paiement_repository.inserer_paiement(
                conn, eleve_id, montant_fcfa, date_str, mode, numero_recu, nouveau_solde
            )
            
            # Commit de la transaction
            conn.commit()
            
            return numero_recu, nouveau_solde
            
        except sqlite3.IntegrityError as e:
            # Rollback en cas d'erreur de contrainte (y compris trigger)
            conn.rollback()
            raise ValidationError(f"Erreur lors de l'enregistrement du paiement : {str(e)}")
        except sqlite3.Error as e:
            # Rollback en cas d'erreur SQL (autre que IntegrityError)
            conn.rollback()
            raise ValidationError(f"Erreur lors de l'enregistrement du paiement : {str(e)}")
        except ValidationError:
            # Rollback en cas d'erreur de validation
            conn.rollback()
            raise
        except Exception as e:
            # Rollback en cas d'erreur inattendue
            conn.rollback()
            raise ValidationError(f"Erreur inattendue lors de l'enregistrement : {str(e)}")
        finally:
            conn.close()
