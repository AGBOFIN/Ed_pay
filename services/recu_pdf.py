"""
Service pour la génération de reçus PDF professionnels et certifiés.
Utilise fpdf2 pour créer des reçus clairs, soignés et faciles à imprimer en A4.
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from services.solde_service import SoldeService
from services.parametre_service import ParametreService
from utils.resource_utils import get_recus_dir, ensure_data_dirs


class RecuPDF:
    """Générateur de reçus scolaires officiels au format PDF."""
    
    def __init__(self):
        self.pdf = None
    
    def generer_recu(self, donnees_recu, chemin_sortie):
        """
        Génère un reçu PDF à partir des données fournies.
        
        Args:
            donnees_recu: Dictionnaire avec les données du reçu
            chemin_sortie: Chemin complet du fichier PDF à créer
            
        Returns:
            str: Chemin du fichier PDF créé
        """
        if FPDF is None:
            raise Exception("fpdf2 n'est pas installé. Installez-le avec : pip install fpdf2")
        
        # Crée le PDF en format A4 portrait
        self.pdf = FPDF('P', 'mm', 'A4')
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        
        # Bordure de page décorative élégante
        self.pdf.set_draw_color(37, 99, 235)  # Bleu primaire #2563EB
        self.pdf.set_line_width(0.8)
        self.pdf.rect(10, 10, 190, 277)
        self.pdf.set_line_width(0.2)
        self.pdf.rect(12, 12, 186, 273)

        parametre_service = ParametreService()
        etablissement = parametre_service.obtenir_etablissement()
        nom_etablissement = etablissement.get(
            'nom',
            donnees_recu.get('etablissement', 'ÉTABLISSEMENT SCOLAIRE'),
        )

        self.pdf.set_y(18)
        self.pdf.set_font('Helvetica', 'B', 18)
        self.pdf.set_text_color(30, 58, 138)  # Bleu marine profond
        self.pdf.cell(0, 10, nom_etablissement, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(5)

        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.set_text_color(100, 116, 139)  # Slate
        self.pdf.cell(0, 6, "Service de Gestion Financière et du Recouvrement Scolaire", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(4)
        
        # Bandeau officiel du reçu
        self.pdf.set_fill_color(239, 246, 255)  # Bleu très clair
        self.pdf.set_draw_color(191, 219, 254)
        self.pdf.rect(20, self.pdf.get_y(), 170, 20, style='FD')
        
        self.pdf.set_y(self.pdf.get_y() + 2)
        self.pdf.set_font('Helvetica', 'B', 15)
        self.pdf.set_text_color(37, 99, 235)
        self.pdf.cell(0, 8, f"REÇU DE PAIEMENT N° {donnees_recu['numero_recu']}", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        date_formatee = self._formater_date(donnees_recu['date_paiement'])
        self.pdf.set_font('Helvetica', 'I', 10)
        self.pdf.set_text_color(71, 85, 105)
        self.pdf.cell(0, 6, f"Délivré le : {date_formatee}", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(12)
        
        # Section 1 : Informations de l'élève
        self.pdf.set_font('Helvetica', 'B', 12)
        self.pdf.set_text_color(30, 41, 59)
        self.pdf.cell(0, 8, "1. IDENTITÉ DE L'ÉLÈVE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.pdf.set_draw_color(226, 232, 240)
        self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
        self.pdf.ln(4)
        
        self.pdf.set_font('Helvetica', '', 11)
        self.pdf.set_text_color(15, 23, 42)
        
        col_w = 85
        self.pdf.set_x(20)
        self.pdf.cell(col_w, 7, f"Nom : {donnees_recu['eleve_nom']}", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.pdf.cell(col_w, 7, f"Prénom : {donnees_recu['eleve_prenom']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.pdf.set_x(20)
        self.pdf.cell(col_w, 7, f"Classe : {donnees_recu['eleve_classe']}", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.pdf.cell(col_w, 7, f"Année scolaire : {donnees_recu['eleve_annee_scolaire']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)
        
        # Section 2 : Détails du versement effectué
        self.pdf.set_font('Helvetica', 'B', 12)
        self.pdf.set_text_color(30, 41, 59)
        self.pdf.cell(0, 8, "2. DÉTAILS DU VERSEMENT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
        self.pdf.ln(4)
        
        montant_fcfa = int(donnees_recu['montant_paye'])
        montant_txt = SoldeService.formater_monnaie_fcfa(montant_fcfa)
        mode = str(donnees_recu['mode_paiement']).capitalize()
        
        self.pdf.set_fill_color(248, 250, 252)
        self.pdf.set_x(20)
        self.pdf.set_font('Helvetica', 'B', 11)
        self.pdf.cell(90, 8, "Montant encaissé :", border=1, fill=True)
        self.pdf.set_text_color(5, 150, 105)  # Vert
        self.pdf.set_font('Helvetica', 'B', 12)
        self.pdf.cell(80, 8, f"  {montant_txt}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.pdf.set_text_color(15, 23, 42)
        self.pdf.set_font('Helvetica', '', 11)
        self.pdf.set_x(20)
        self.pdf.cell(90, 8, "Mode de règlement :", border=1)
        self.pdf.cell(80, 8, f"  {mode}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)
        
        # Section 3 : Situation du compte après paiement
        self.pdf.set_font('Helvetica', 'B', 12)
        self.pdf.set_text_color(30, 41, 59)
        self.pdf.cell(0, 8, "3. SITUATION FINANCIÈRE APRÈS CE PAIEMENT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.line(20, self.pdf.get_y(), 190, self.pdf.get_y())
        self.pdf.ln(4)
        
        total_du_fcfa = int(donnees_recu['total_du'])
        solde_apres_fcfa = int(donnees_recu['solde_apres'])
        total_du_txt = SoldeService.formater_monnaie_fcfa(total_du_fcfa)
        solde_txt = SoldeService.formater_monnaie_fcfa(solde_apres_fcfa)
        
        self.pdf.set_fill_color(248, 250, 252)
        self.pdf.set_x(20)
        self.pdf.cell(90, 8, "Scolarité totale annuelle :", border=1)
        self.pdf.cell(80, 8, f"  {total_du_txt}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.pdf.set_x(20)
        self.pdf.set_font('Helvetica', 'B', 11)
        self.pdf.cell(90, 8, "Solde restant dû :", border=1, fill=True)
        if solde_apres_fcfa == 0:
            self.pdf.set_text_color(5, 150, 105)
            solde_affiche = f"  {solde_txt}  (COMPTE SOLDÉ)"
        else:
            self.pdf.set_text_color(220, 38, 38)
            solde_affiche = f"  {solde_txt}"
        self.pdf.cell(80, 8, solde_affiche, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(18)
        
        # Cadre Signatures
        self.pdf.set_text_color(71, 85, 105)
        self.pdf.set_font('Helvetica', 'I', 10)
        
        sig_y = self.pdf.get_y()
        self.pdf.set_x(25)
        self.pdf.cell(65, 6, "Signature de l'élève / du parent :", align='C')
        self.pdf.set_x(120)
        self.pdf.cell(65, 6, "Pour l'Établissement (La Comptabilité) :", align='C')
        
        # Lignes de signature
        self.pdf.set_y(sig_y + 25)
        self.pdf.set_draw_color(148, 163, 184)
        self.pdf.line(25, self.pdf.get_y(), 90, self.pdf.get_y())
        self.pdf.line(120, self.pdf.get_y(), 185, self.pdf.get_y())
        
        self.pdf.set_y(sig_y + 28)
        self.pdf.set_font('Helvetica', '', 9)
        self.pdf.set_x(25)
        self.pdf.cell(65, 5, "Mention « Reçu »", align='C')
        self.pdf.set_x(120)
        self.pdf.cell(65, 5, "Cachet officiel & Signature", align='C')
        
        # Bas de page officiel
        self.pdf.set_y(270)
        self.pdf.set_font('Helvetica', 'I', 8)
        self.pdf.set_text_color(148, 163, 184)
        self.pdf.cell(0, 4, "Ce reçu tient lieu de pièce comptable justificative. Conservez-le précieusement.", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 4, "EduPaie - Système Informatisé de Gestion des Scolarités", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Sauvegarde le PDF
        self.pdf.output(chemin_sortie)
        return chemin_sortie
    
    def _formater_date(self, date_str):
        """Formate une date pour l'affichage DD/MM/YYYY."""
        if ' ' in str(date_str):
            date_part = str(date_str).split(' ')[0]
        else:
            date_part = str(date_str)
        
        try:
            annee, mois, jour = date_part.split('-')
            return f"{jour}/{mois}/{annee}"
        except Exception:
            return str(date_str)


def get_chemin_dossier_recus():
    """Retourne le chemin du dossier des reçus."""
    ensure_data_dirs()
    return get_recus_dir()


def generer_recu_pdf(donnees_recu):
    """
    Génère un reçu PDF et retourne le chemin du fichier créé.
    
    Args:
        donnees_recu: Dictionnaire avec les données du reçu
        
    Returns:
        str: Chemin du fichier PDF créé
    """
    numero_recu = str(donnees_recu['numero_recu']).replace('/', '-').replace('\\', '-')
    nom_fichier = f"{numero_recu}.pdf"
    
    recus_dir = get_chemin_dossier_recus()
    chemin_sortie = os.path.join(recus_dir, nom_fichier)
    
    try:
        generateur = RecuPDF()
        chemin = generateur.generer_recu(donnees_recu, chemin_sortie)
        
        if not os.path.exists(chemin) or os.path.getsize(chemin) == 0:
            raise Exception("Le fichier PDF n'a pas été créé correctement")
        
        return chemin
    except PermissionError:
        raise Exception("Dossier inaccessible ou fichier déjà ouvert. Vérifiez les permissions.")
    except OSError as e:
        raise Exception(f"Erreur d'accès au dossier : {str(e)}")
    except Exception as e:
        raise Exception(f"Erreur lors de la génération du PDF : {str(e)}")
