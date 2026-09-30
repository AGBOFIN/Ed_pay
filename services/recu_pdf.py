"""
Service pour la génération de reçus PDF.
Utilise fpdf2 pour créer des reçus lisibles et professionnels.
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from services.solde_service import SoldeService
from utils.resource_utils import get_recus_dir, ensure_data_dirs


class RecuPDF:
    """Générateur de reçus PDF."""
    
    def __init__(self):
        """Initialise le générateur."""
        self.pdf = None
    
    def generer_recu(self, donnees_recu, chemin_sortie):
        """
        Génère un reçu PDF à partir des données fournies.
        
        Args:
            donnees_recu: Dictionnaire avec les données du reçu
            chemin_sortie: Chemin complet du fichier PDF à créer
            
        Returns:
            str: Chemin du fichier PDF créé
            
        Raises:
            Exception: Si la génération échoue
        """
        if FPDF is None:
            raise Exception("fpdf n'est pas installé. Installez-le avec : pip install fpdf2")
        
        # Crée le PDF en format A4
        self.pdf = FPDF('P', 'mm', 'A4')
        self.pdf.add_page()
        
        # Configuration des polices (Helvetica supporte le latin-1)
        self.pdf.set_font('Helvetica', '', 12)
        
        # Entête : nom de l'établissement
        self.pdf.set_font('Helvetica', 'B', 18)
        self.pdf.cell(0, 10, donnees_recu['etablissement'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(5)
        
        # Titre : REÇU
        self.pdf.set_font('Helvetica', 'B', 16)
        self.pdf.cell(0, 10, f"REÇU N° {donnees_recu['numero_recu']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)
        
        # Date du paiement
        self.pdf.set_font('Helvetica', '', 12)
        date_formatee = self._formater_date(donnees_recu['date_paiement'])
        self.pdf.cell(0, 8, f"Date du paiement : {date_formatee}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(5)
        
        # Ligne de separation
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(10)
        
        # Informations de l'élève
        self.pdf.set_font('Helvetica', 'B', 14)
        self.pdf.cell(0, 8, "Élève :", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(3)
        
        self.pdf.set_font('Helvetica', '', 12)
        self.pdf.cell(0, 8, f"Nom : {donnees_recu['eleve_nom']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 8, f"Prénom : {donnees_recu['eleve_prenom']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 8, f"Classe : {donnees_recu['eleve_classe']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 8, f"Année scolaire : {donnees_recu['eleve_annee_scolaire']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)
        
        # Détails du paiement
        self.pdf.set_font('Helvetica', 'B', 14)
        self.pdf.cell(0, 8, "Paiement :", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(3)
        
        self.pdf.set_font('Helvetica', '', 12)
        montant_fcfa = donnees_recu['montant_paye']
        self.pdf.cell(0, 8, f"Montant payé : {SoldeService.formater_monnaie_fcfa(montant_fcfa)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 8, f"Mode de paiement : {donnees_recu['mode_paiement']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)
        
        # Ligne de separation
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(10)
        
        # Récapitulatif financier
        self.pdf.set_font('Helvetica', 'B', 14)
        self.pdf.cell(0, 8, "Récapitulatif :", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(3)
        
        self.pdf.set_font('Helvetica', '', 12)
        total_du_fcfa = donnees_recu['total_du']
        solde_apres_fcfa = donnees_recu['solde_apres']
        
        self.pdf.cell(0, 8, f"Total dû : {SoldeService.formater_monnaie_fcfa(total_du_fcfa)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 8, f"Solde restant après ce paiement : {SoldeService.formater_monnaie_fcfa(solde_apres_fcfa)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(20)
        
        # Zone de signature
        self.pdf.set_font('Helvetica', 'I', 10)
        self.pdf.cell(0, 8, "Signature :", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(30)
        self.pdf.line(10, self.pdf.get_y(), 60, self.pdf.get_y())
        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.cell(50, 8, "La comptabilité", new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        # Sauvegarde le PDF
        self.pdf.output(chemin_sortie)
        
        return chemin_sortie
    
    def _formater_date(self, date_str):
        """
        Formate une date de la base pour l'affichage.
        
        Args:
            date_str: Date au format YYYY-MM-DD HH:MM:SS
            
        Returns:
            str: Date au format DD/MM/YYYY
        """
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
        else:
            date_part = date_str
        
        try:
            annee, mois, jour = date_part.split('-')
            return f"{jour}/{mois}/{annee}"
        except:
            return date_str


def get_chemin_dossier_recus():
    """
    Retourne le chemin du dossier des reçus.
    Crée le dossier s'il n'existe pas.
    
    En PyInstaller, le dossier est à côté de l'exécutable (data/recus).
    
    Returns:
        str: Chemin du dossier recus
    """
    # Assure que les dossiers de données existent
    ensure_data_dirs()
    
    # Utilise le chemin depuis resource_utils
    return get_recus_dir()


def generer_recu_pdf(donnees_recu):
    """
    Génère un reçu PDF et retourne le chemin du fichier.
    
    Args:
        donnees_recu: Dictionnaire avec les données du reçu
        
    Returns:
        str: Chemin du fichier PDF créé
        
    Raises:
        Exception: Si la génération échoue
    """
    # Nettoie le numéro de reçu pour le nom de fichier
    numero_recu = donnees_recu['numero_recu'].replace('/', '-').replace('\\', '-')
    nom_fichier = f"{numero_recu}.pdf"
    
    # Obtient le chemin du dossier et crée le nom de fichier complet
    recus_dir = get_chemin_dossier_recus()
    chemin_sortie = os.path.join(recus_dir, nom_fichier)
    
    try:
        # Génère le PDF
        générateur = RecuPDF()
        chemin = générateur.generer_recu(donnees_recu, chemin_sortie)
        
        # Vérifie que le fichier a été créé
        if not os.path.exists(chemin) or os.path.getsize(chemin) == 0:
            raise Exception("Le fichier PDF n'a pas été créé correctement")
        
        return chemin
    except PermissionError:
        raise Exception("Dossier inaccessible ou fichier deja ouvert. Verifiez les permissions.")
    except OSError as e:
        raise Exception(f"Erreur d'acces au dossier : {str(e)}")
    except Exception as e:
        raise Exception(f"Erreur lors de la generation du PDF : {str(e)}")
