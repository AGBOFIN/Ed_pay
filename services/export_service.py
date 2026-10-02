"""
Service d'export des données EduPaie (CSV compatible Microsoft Excel).
Permet à la secrétaire scolaire d'exporter facilement les listes d'élèves,
leurs états financiers et les historiques de paiement.
"""

import csv
from services.solde_service import SoldeService


class ExportService:
    """Service d'exportation de données."""

    @staticmethod
    def _proteger_valeur_csv(valeur):
        """Empêche Excel d'interpréter une valeur textuelle comme une formule."""
        if isinstance(valeur, str) and valeur.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + valeur
        return valeur

    @staticmethod
    def exporter_eleves_csv(eleves, chemin_fichier):
        """
        Exporte une liste d'élèves au format CSV compatible Excel (UTF-8 avec BOM).
        
        Args:
            eleves: Liste de dictionnaires d'élèves
            chemin_fichier: Chemin complet du fichier destination (.csv)
            
        Returns:
            int: Nombre de lignes exportées
        """
        headers = [
            "ID",
            "Nom",
            "Prénom",
            "Classe",
            "Année scolaire",
            "Total dû (FCFA)",
            "Payé (FCFA)",
            "Solde (FCFA)",
            "Statut"
        ]

        with open(chemin_fichier, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(headers)

            for eleve in eleves:
                total_du = eleve.get('total_du', 0)
                total_paye = eleve.get('total_paye', 0)
                solde = eleve.get('solde', SoldeService.calculer_solde(total_du, total_paye))
                statut = eleve.get('statut', SoldeService.determiner_statut(total_du, total_paye))

                writer.writerow(ExportService._proteger_valeur_csv(valeur) for valeur in [
                    eleve.get('id', ''),
                    eleve.get('nom', ''),
                    eleve.get('prenom', ''),
                    eleve.get('classe', ''),
                    eleve.get('annee_scolaire', ''),
                    total_du,
                    total_paye,
                    solde,
                    statut
                ])

        return len(eleves)
