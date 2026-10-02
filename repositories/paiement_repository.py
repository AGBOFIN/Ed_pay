"""
Repository pour la gestion des paiements.
Encapsule tout l'accès aux données pour la table paiement.
"""

from sqlcipher3 import dbapi2 as sqlite3
from database.connection import get_connection


class PaiementRepository:
    """Repository pour les opérations sur les paiements."""
    
    def total_paye_par_eleve(self, eleve_id):
        """
        Calcule le total payé pour un élève.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            int: Total payé en francs CFA (entier), 0 si aucun paiement
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT COALESCE(SUM(montant), 0) as total
                FROM paiement
                WHERE eleve_id = ?
                """,
                (eleve_id,)
            )
            row = cursor.fetchone()
            return int(row['total'])
        finally:
            conn.close()
    
    def lister_par_eleve(self, eleve_id):
        """
        Liste tous les paiements d'un élève, triés par date puis ID.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            list: Liste de dictionnaires représentant les paiements
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT id, eleve_id, montant, date, mode, numero_recu, solde_apres
                FROM paiement
                WHERE eleve_id = ?
                ORDER BY date, id
                """,
                (eleve_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def obtenir_total_du_eleve(self, conn, eleve_id):
        """
        Récupère le total_du d'un élève (utilise une connexion existante).
        
        Args:
            conn: Connexion existante à la base
            eleve_id: ID de l'élève
            
        Returns:
            int: Total dû en francs CFA
        """
        cursor = conn.cursor()
        cursor.execute("SELECT total_du FROM eleve WHERE id = ?", (eleve_id,))
        row = cursor.fetchone()
        return int(row['total_du'])
    
    def obtenir_total_paye_eleve(self, conn, eleve_id):
        """
        Récupère le total payé d'un élève (utilise une connexion existante).
        
        Args:
            conn: Connexion existante à la base
            eleve_id: ID de l'élève
            
        Returns:
            int: Total payé en francs CFA
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(montant), 0) as total
            FROM paiement
            WHERE eleve_id = ?
            """,
            (eleve_id,)
        )
        row = cursor.fetchone()
        return int(row['total'])
    
    def incrementer_sequence_recu(self, conn, annee):
        """
        Incrémente la séquence des numéros de reçus et retourne le nouveau numéro.
        
        Args:
            conn: Connexion existante à la base
            annee: Année pour le numéro de reçu
            
        Returns:
            str: Numéro de reçu généré
        """
        cursor = conn.cursor()
        
        # Récupère la dernière valeur
        cursor.execute("SELECT derniere_valeur FROM sequence_recus WHERE id = 1")
        row = cursor.fetchone()
        derniere_valeur = row['derniere_valeur'] if row else 0
        
        # Incrémente
        nouvelle_valeur = derniere_valeur + 1
        
        # Met à jour la séquence
        cursor.execute(
            "UPDATE sequence_recus SET derniere_valeur = ? WHERE id = 1",
            (nouvelle_valeur,)
        )
        
        # Formate le numéro
        return f"REC-{annee}-{nouvelle_valeur:05d}"
    
    def inserer_paiement(self, conn, eleve_id, montant, date, mode, numero_recu, solde_apres):
        """
        Insère un paiement dans la base (utilise une connexion existante).
        
        Args:
            conn: Connexion existante à la base (transaction déjà commencée)
            eleve_id: ID de l'élève
            montant: Montant du paiement en francs CFA
            date: Date du paiement
            mode: Mode de paiement
            numero_recu: Numéro de reçu unique
            solde_apres: Solde restant après ce paiement (en francs CFA)
            
        Returns:
            int: ID du paiement créé
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO paiement (eleve_id, montant, date, mode, numero_recu, solde_apres)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (eleve_id, montant, date, mode, numero_recu, solde_apres)
        )
        return cursor.lastrowid
