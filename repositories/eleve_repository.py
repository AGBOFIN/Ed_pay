"""
Repository pour la gestion des élèves.
Encapsule tout l'accès aux données pour la table eleve.
"""

import sqlite3
from database.connection import get_connection


class EleveRepository:
    """Repository pour les opérations sur les élèves."""
    
    def ajouter(self, nom, prenom, classe, annee_scolaire, total_du):
        """
        Ajoute un nouvel élève dans la base de données.
        
        Args:
            nom: Nom de l'élève
            prenom: Prénom de l'élève
            classe: Classe de l'élève
            annee_scolaire: Année scolaire (format 2025-2026)
            total_du: Montant total dû
            
        Returns:
            int: L'ID de l'élève créé
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO eleve (nom, prenom, classe, annee_scolaire, total_du)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nom, prenom, classe, annee_scolaire, total_du)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def modifier(self, eleve_id, nom, prenom, classe, annee_scolaire, total_du):
        """
        Modifie un élève existant.
        
        Args:
            eleve_id: ID de l'élève à modifier
            nom: Nouveau nom
            prenom: Nouveau prénom
            classe: Nouvelle classe
            annee_scolaire: Nouvelle année scolaire
            total_du: Nouveau total dû
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                UPDATE eleve
                SET nom = ?, prenom = ?, classe = ?, annee_scolaire = ?, total_du = ?
                WHERE id = ?
                """,
                (nom, prenom, classe, annee_scolaire, total_du, eleve_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def supprimer(self, eleve_id):
        """
        Supprime un élève de la base de données.
        
        Args:
            eleve_id: ID de l'élève à supprimer
            
        Note:
            La suppression échouera si l'élève a des paiements
            (contrainte de clé étrangère ON DELETE RESTRICT).
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM eleve WHERE id = ?", (eleve_id,))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def obtenir_par_id(self, eleve_id):
        """
        Récupère un élève par son ID avec le total payé.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            dict: Dictionnaire avec les informations de l'élève et total_paye, ou None si non trouvé
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT 
                    e.id, e.nom, e.prenom, e.classe, e.annee_scolaire, 
                    e.total_du, e.date_creation,
                    COALESCE(SUM(p.montant), 0) as total_paye
                FROM eleve e
                LEFT JOIN paiement p ON e.id = p.eleve_id
                WHERE e.id = ?
                GROUP BY e.id, e.nom, e.prenom, e.classe, e.annee_scolaire, e.total_du, e.date_creation
                """,
                (eleve_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def lister(self, recherche=None, classe=None):
        """
        Liste les élèves avec recherche et filtre optionnels.
        Inclut le total payé calculé avec LEFT JOIN et GROUP BY.
        
        Args:
            recherche: Terme de recherche (nom ou prénom)
            classe: Filtre par classe
            
        Returns:
            list: Liste de dictionnaires représentant les élèves avec total_paye
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Construction dynamique de la requête avec paramètres
            # LEFT JOIN pour inclure les élèves sans paiements
            # GROUP BY pour calculer le total payé par élève
            query = """
                SELECT 
                    e.id, e.nom, e.prenom, e.classe, e.annee_scolaire, 
                    e.total_du, e.date_creation,
                    COALESCE(SUM(p.montant), 0) as total_paye
                FROM eleve e
                LEFT JOIN paiement p ON e.id = p.eleve_id
                WHERE 1=1
            """
            params = []
            
            if recherche:
                query += " AND (e.nom LIKE ? OR e.prenom LIKE ?)"
                params.extend([f"%{recherche}%", f"%{recherche}%"])
            
            if classe:
                query += " AND e.classe = ?"
                params.append(classe)
            
            query += " GROUP BY e.id, e.nom, e.prenom, e.classe, e.annee_scolaire, e.total_du, e.date_creation"
            query += " ORDER BY e.nom, e.prenom"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def lister_classes(self):
        """
        Liste toutes les classes distinctes.
        
        Returns:
            list: Liste des noms de classes
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT DISTINCT classe
                FROM eleve
                ORDER BY classe
                """
            )
            rows = cursor.fetchall()
            return [row['classe'] for row in rows]
        finally:
            conn.close()
    
    def a_des_paiements(self, eleve_id):
        """
        Vérifie si un élève a des paiements.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            bool: True si l'élève a des paiements, False sinon
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM paiement
                WHERE eleve_id = ?
                """,
                (eleve_id,)
            )
            row = cursor.fetchone()
            return row['count'] > 0
        finally:
            conn.close()
