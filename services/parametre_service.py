"""
Service pour la gestion des paramètres de l'établissement.
Contient la logique métier pour les paramètres.
"""

from repositories.parametre_repository import ParametreRepository
from repositories.classe_repository import ClasseRepository
from services.exceptions import ValidationError


class ParametreService:
    """Service pour la gestion des paramètres."""
    
    def __init__(self):
        """Initialise le service avec les repositories."""
        self.parametre_repo = ParametreRepository()
        self.classe_repo = ClasseRepository()
    
    def obtenir_etablissement(self):
        """
        Récupère les informations de l'établissement.
        
        Returns:
            dict: Dictionnaire avec les informations de l'établissement
        """
        return {
            'nom': self.parametre_repo.obtenir('etablissement_nom') or 'École Exemple',
            'adresse': self.parametre_repo.obtenir('etablissement_adresse') or '',
            'telephone': self.parametre_repo.obtenir('etablissement_telephone') or '',
            'email': self.parametre_repo.obtenir('etablissement_email') or '',
            'devise': self.parametre_repo.obtenir('etablissement_devise') or 'FCFA',
            'logo': self.parametre_repo.obtenir('etablissement_logo') or '',
            'pied_page': self.parametre_repo.obtenir('etablissement_pied_page') or ''
        }
    
    def definir_etablissement(self, nom, adresse, telephone, email, devise, logo, pied_page):
        """
        Définit les informations de l'établissement.
        
        Args:
            nom: Nom de l'établissement
            adresse: Adresse
            telephone: Téléphone
            email: E-mail
            devise: Devise affichée
            logo: Chemin du logo
            pied_page: Pied de page du reçu
        """
        if not nom or not nom.strip():
            raise ValidationError("Le nom de l'établissement est obligatoire")
        
        self.parametre_repo.definir('etablissement_nom', nom.strip())
        self.parametre_repo.definir('etablissement_adresse', adresse.strip())
        self.parametre_repo.definir('etablissement_telephone', telephone.strip())
        self.parametre_repo.definir('etablissement_email', email.strip())
        self.parametre_repo.definir('etablissement_devise', devise.strip())
        self.parametre_repo.definir('etablissement_logo', logo.strip())
        self.parametre_repo.definir('etablissement_pied_page', pied_page.strip())
    
    def obtenir_annee_scolaire(self):
        """
        Récupère l'année scolaire actuelle.
        
        Returns:
            str: Année scolaire
        """
        return self.parametre_repo.obtenir('annee_scolaire') or '2025-2026'
    
    def definir_annee_scolaire(self, annee):
        """
        Définit l'année scolaire.
        
        Args:
            annee: Année scolaire (format XXXX-XXXX)
        """
        if not annee or not annee.strip():
            raise ValidationError("L'année scolaire est obligatoire")
        
        self.parametre_repo.definir('annee_scolaire', annee.strip())
    
    def obtenir_prefixe_recu(self):
        """
        Récupère le préfixe des numéros de reçu.
        
        Returns:
            str: Préfixe des reçus
        """
        return self.parametre_repo.obtenir('recu_prefixe') or 'REC'
    
    def definir_prefixe_recu(self, prefixe):
        """
        Définit le préfixe des numéros de reçu.
        
        Args:
            prefixe: Préfixe des reçus
        """
        if not prefixe or not prefixe.strip():
            raise ValidationError("Le préfixe des reçus est obligatoire")
        
        self.parametre_repo.definir('recu_prefixe', prefixe.strip())
    
    def obtenir_modes_paiement(self):
        """
        Récupère les modes de paiement actifs.
        
        Returns:
            list: Liste des modes de paiement actifs
        """
        modes = self.parametre_repo.obtenir('paiement_modes')
        if modes:
            return modes.split(',')
        return ['espèces', 'chèque', 'virement', 'mobile money']
    
    def definir_modes_paiement(self, modes):
        """
        Définit les modes de paiement actifs.
        
        Args:
            modes: Liste des modes de paiement
        """
        if not modes or len(modes) == 0:
            raise ValidationError("Au moins un mode de paiement doit être actif")
        
        self.parametre_repo.definir('paiement_modes', ','.join(modes))
    
    def lister_classes_actives(self):
        """
        Liste toutes les classes actives.
        
        Returns:
            list: Liste des classes actives
        """
        return self.classe_repo.lister_actives()
    
    def lister_toutes_classes(self):
        """
        Liste toutes les classes.
        
        Returns:
            list: Liste de toutes les classes
        """
        return self.classe_repo.lister_toutes()
    
    def ajouter_classe(self, nom, frais_defaut):
        """
        Ajoute une nouvelle classe.
        
        Args:
            nom: Nom de la classe
            frais_defaut: Frais par défaut en FCFA
            
        Returns:
            int: ID de la classe créée
        """
        if not nom or not nom.strip():
            raise ValidationError("Le nom de la classe est obligatoire")
        
        if frais_defaut < 0:
            raise ValidationError("Les frais par défaut doivent être positifs ou nuls")
        
        # Vérifie que le nom n'existe pas déjà
        classe_existante = self.classe_repo.obtenir_par_nom(nom.strip())
        if classe_existante:
            raise ValidationError("Une classe avec ce nom existe déjà")
        
        return self.classe_repo.ajouter(nom.strip(), frais_defaut)
    
    def modifier_classe(self, classe_id, nom, frais_defaut):
        """
        Modifie une classe.
        
        Args:
            classe_id: ID de la classe
            nom: Nouveau nom de la classe
            frais_defaut: Nouveaux frais par défaut en FCFA
        """
        if not nom or not nom.strip():
            raise ValidationError("Le nom de la classe est obligatoire")
        
        if frais_defaut < 0:
            raise ValidationError("Les frais par défaut doivent être positifs ou nuls")
        
        self.classe_repo.modifier(classe_id, nom.strip(), frais_defaut)
    
    def desactiver_classe(self, classe_id):
        """
        Désactive une classe.
        
        Args:
            classe_id: ID de la classe
        """
        if self.classe_repo.est_utilisee(classe_id):
            raise ValidationError("Impossible de désactiver une classe utilisée par des élèves")
        
        self.classe_repo.desactiver(classe_id)
    
    def obtenir_frais_defaut_classe(self, nom_classe):
        """
        Récupère les frais par défaut d'une classe.
        
        Args:
            nom_classe: Nom de la classe
            
        Returns:
            int: Frais par défaut en FCFA, ou 0 si non trouvé
        """
        classe = self.classe_repo.obtenir_par_nom(nom_classe)
        if classe:
            return classe['frais_defaut']
        return 0
