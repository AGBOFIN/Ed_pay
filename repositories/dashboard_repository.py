"""
Repository pour les données du tableau de bord.
Requêtes SQL agrégées pour les indicateurs globaux.
"""

from database.connection import get_connection


class DashboardRepository:
    """Repository pour les données du tableau de bord."""
    
    def obtenir_nombre_eleves(self):
        """
        Compte le nombre total d'élèves.
        
        Returns:
            int: Nombre d'élèves
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM eleve")
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
    
    def obtenir_total_encaisse(self):
        """
        Calcule le montant total encaissé (somme de tous les paiements).
        
        Returns:
            int: Total encaissé en francs CFA
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COALESCE(SUM(montant), 0) as total FROM paiement")
            row = cursor.fetchone()
            return row['total'] if row else 0
        finally:
            conn.close()
    
    def obtenir_total_restant_du(self):
        """
        Calcule le montant total restant dû (somme des soldes de tous les élèves).
        
        Returns:
            int: Total restant dû en francs CFA
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Requête agrégée : somme des (total_du - total_paye) pour tous les élèves
            cursor.execute(
                """
                SELECT COALESCE(SUM(e.total_du - COALESCE(SUM(p.montant), 0)), 0) as total
                FROM eleve e
                LEFT JOIN paiement p ON e.id = p.eleve_id
                GROUP BY e.id
                """
            )
            rows = cursor.fetchall()
            # Somme des soldes individuels
            total = sum(row['total'] for row in rows)
            return total
        finally:
            conn.close()
    
    def obtenir_nombre_eleves_non_soldes(self):
        """
        Compte le nombre d'élèves non soldés.
        
        Note: La logique de détermination du statut est dans SoldeService.
        Cette méthode retourne le nombre d'élèves, le calcul du statut se fait dans DashboardService.
        
        Returns:
            int: Nombre total d'élèves
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM eleve")
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
    
    def obtenir_indicateurs_synthetiques(self):
        """
        Récupère tous les indicateurs synthétiques en une seule requête optimisée.
        
        Returns:
            dict: Dictionnaire avec tous les indicateurs
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Requête optimisée qui calcule tout en une seule passe
            cursor.execute(
                """
                SELECT
                    COUNT(*) as nb_eleves,
                    COALESCE(SUM(solde), 0) as total_restant_du
                FROM (
                    SELECT
                        e.id,
                        e.total_du - COALESCE(SUM(p.montant), 0) as solde
                    FROM eleve e
                    LEFT JOIN paiement p ON e.id = p.eleve_id
                    GROUP BY e.id
                )
                """
            )
            row = cursor.fetchone()
            
            nb_eleves = row['nb_eleves'] if row else 0
            total_restant_du = row['total_restant_du'] if row else 0
            
            # Total encaissé (requête séparée)
            cursor.execute("SELECT COALESCE(SUM(montant), 0) as total FROM paiement")
            row_encaisse = cursor.fetchone()
            total_encaisse = row_encaisse['total'] if row_encaisse else 0
            
            return {
                'nb_eleves': nb_eleves,
                'total_encaisse': total_encaisse,
                'total_restant_du': total_restant_du,
                'nb_eleves_non_soldes': 0  # Calculé dans DashboardService
            }
        finally:
            conn.close()
