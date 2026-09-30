"""
Service pour la gestion des élèves.
Contient la logique métier et les validations.
"""

import sqlite3
import re
from repositories.eleve_repository import EleveRepository
from services.solde_service import SoldeService


class ValidationError(Exception):
    """Exception levée lors d'une erreur de validation métier."""
    pass


class EleveService:
    """Service pour les opérations métier sur les élèves."""
    
    def __init__(self):
        """Initialise le service avec le repository."""
        self.repository = EleveRepository()
    
    def valider_donnees_eleve(self, nom, prenom, classe, annee_scolaire, total_du):
        """
        Valide les données d'un élève.
        
        Args:
            nom: Nom de l'élève
            prenom: Prénom de l'élève
            classe: Classe de l'élève
            annee_scolaire: Année scolaire
            total_du: Montant total dû
            
        Raises:
            ValidationError: Si les données ne sont pas valides
        """
        # Validation du nom
        if not nom or not nom.strip():
            raise ValidationError("Le nom est obligatoire")
        if len(nom.strip()) < 2:
            raise ValidationError("Le nom doit contenir au moins 2 caractères")
        
        # Validation du prénom
        if not prenom or not prenom.strip():
            raise ValidationError("Le prénom est obligatoire")
        if len(prenom.strip()) < 2:
            raise ValidationError("Le prénom doit contenir au moins 2 caractères")
        
        # Validation de la classe
        if not classe or not classe.strip():
            raise ValidationError("La classe est obligatoire")
        if len(classe.strip()) < 2:
            raise ValidationError("La classe doit contenir au moins 2 caractères")
        
        # Validation de l'année scolaire (format YYYY-YYYY)
        if not annee_scolaire or not annee_scolaire.strip():
            raise ValidationError("L'année scolaire est obligatoire")
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, annee_scolaire.strip()):
            raise ValidationError("L'année scolaire doit être au format YYYY-YYYY (ex: 2025-2026)")
        
        # Validation du total dû
        try:
            total_du_float = float(total_du)
            if total_du_float < 0:
                raise ValidationError("Le total dû ne peut pas être négatif")
        except (ValueError, TypeError):
            raise ValidationError("Le total dû doit être un nombre")
    
    def ajouter_eleve(self, nom, prenom, classe, annee_scolaire, total_du):
        """
        Ajoute un nouvel élève après validation.
        
        Args:
            nom: Nom de l'élève
            prenom: Prénom de l'élève
            classe: Classe de l'élève
            annee_scolaire: Année scolaire
            total_du: Montant total dû
            
        Returns:
            int: L'ID de l'élève créé
            
        Raises:
            ValidationError: Si les données ne sont pas valides
        """
        # Validation des données
        self.valider_donnees_eleve(nom, prenom, classe, annee_scolaire, total_du)
        
        # Nettoyage des données
        nom = nom.strip()
        prenom = prenom.strip()
        classe = classe.strip()
        annee_scolaire = annee_scolaire.strip()
        total_du = float(total_du)
        
        try:
            return self.repository.ajouter(nom, prenom, classe, annee_scolaire, total_du)
        except sqlite3.Error as e:
            raise ValidationError(f"Erreur lors de l'ajout de l'élève : {str(e)}")
    
    def modifier_eleve(self, eleve_id, nom, prenom, classe, annee_scolaire, total_du):
        """
        Modifie un élève existant après validation.
        
        Args:
            eleve_id: ID de l'élève à modifier
            nom: Nouveau nom
            prenom: Nouveau prénom
            classe: Nouvelle classe
            annee_scolaire: Nouvelle année scolaire
            total_du: Nouveau total dû
            
        Raises:
            ValidationError: Si les données ne sont pas valides ou si l'élève n'existe pas
        """
        # Validation des données
        self.valider_donnees_eleve(nom, prenom, classe, annee_scolaire, total_du)
        
        # Vérifie que l'élève existe
        eleve = self.repository.obtenir_par_id(eleve_id)
        if not eleve:
            raise ValidationError("L'élève n'existe pas")
        
        # Nettoyage des données
        nom = nom.strip()
        prenom = prenom.strip()
        classe = classe.strip()
        annee_scolaire = annee_scolaire.strip()
        total_du = float(total_du)
        
        try:
            self.repository.modifier(eleve_id, nom, prenom, classe, annee_scolaire, total_du)
        except sqlite3.Error as e:
            raise ValidationError(f"Erreur lors de la modification de l'élève : {str(e)}")
    
    def supprimer_eleve(self, eleve_id):
        """
        Supprime un élève après vérification.
        
        Args:
            eleve_id: ID de l'élève à supprimer
            
        Raises:
            ValidationError: Si l'élève a des paiements ou n'existe pas
        """
        # Vérifie que l'élève existe
        eleve = self.repository.obtenir_par_id(eleve_id)
        if not eleve:
            raise ValidationError("L'élève n'existe pas")
        
        # Vérifie que l'élève n'a pas de paiements
        if self.repository.a_des_paiements(eleve_id):
            raise ValidationError(
                "Impossible de supprimer cet élève car il a des paiements enregistrés. "
                "Supprimer un élève avec des paiements ferait perdre l'historique des reçus."
            )
        
        try:
            self.repository.supprimer(eleve_id)
        except sqlite3.Error as e:
            raise ValidationError(f"Erreur lors de la suppression de l'élève : {str(e)}")
    
    def obtenir_eleve(self, eleve_id):
        """
        Récupère un élève par son ID.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            dict: Dictionnaire avec les informations de l'élève, ou None si non trouvé
        """
        return self.repository.obtenir_par_id(eleve_id)
    
    def lister_eleves(self, recherche=None, classe=None):
        """
        Liste les élèves avec recherche et filtre optionnels.
        
        Args:
            recherche: Terme de recherche (nom ou prénom)
            classe: Filtre par classe
            
        Returns:
            list: Liste de dictionnaires représentant les élèves avec total_paye
        """
        try:
            eleves = self.repository.lister(recherche, classe)
            # total_du est déjà en francs CFA (entier)
            return eleves
        except sqlite3.Error as e:
            raise ValidationError(f"Erreur lors de la liste des élèves : {str(e)}")
    
    def lister_classes(self):
        """
        Liste toutes les classes distinctes.
        
        Returns:
            list: Liste des noms de classes
        """
        try:
            return self.repository.lister_classes()
        except sqlite3.Error as e:
            raise ValidationError(f"Erreur lors de la liste des classes : {str(e)}")
