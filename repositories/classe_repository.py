"""
Repository pour la gestion des classes.
Encapsule tout l'accès aux données pour la table classe.
"""

import sqlite3
from database.connection import get_connection


class ClasseRepository:
    """Repository pour les opérations sur les classes."""
    
    def lister_actives(self):
        """
        Liste toutes les classes actives.
        
        Returns:
            list: Liste de dictionnaires représentant les classes actives
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, nom, frais_defaut FROM classe WHERE actif = 1 ORDER BY nom"
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def lister_toutes(self):
        """
        Liste toutes les classes (actives et inactives).
        
        Returns:
            list: Liste de dictionnaires représentant toutes les classes
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, nom, frais_defaut, actif FROM classe ORDER BY nom")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def obtenir_par_id(self, classe_id):
        """
        Récupère une classe par son ID.
        
        Args:
            classe_id: ID de la classe
            
        Returns:
            dict: Dictionnaire représentant la classe, ou None
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, nom, frais_defaut, actif FROM classe WHERE id = ?",
                (classe_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def obtenir_par_nom(self, nom):
        """
        Récupère une classe par son nom.
        
        Args:
            nom: Nom de la classe
            
        Returns:
            dict: Dictionnaire représentant la classe, ou None
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, nom, frais_defaut, actif FROM classe WHERE nom = ?",
                (nom,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def ajouter(self, nom, frais_defaut):
        """
        Ajoute une nouvelle classe.
        
        Args:
            nom: Nom de la classe
            frais_defaut: Frais par défaut en FCFA
            
        Returns:
            int: ID de la classe créée
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO classe (nom, frais_defaut) VALUES (?, ?)",
                (nom, frais_defaut)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def modifier(self, classe_id, nom, frais_defaut):
        """
        Modifie une classe.
        
        Args:
            classe_id: ID de la classe
            nom: Nouveau nom de la classe
            frais_defaut: Nouveaux frais par défaut en FCFA
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                UPDATE classe SET nom = ?, frais_defaut = ?
                WHERE id = ?
                """,
                (nom, frais_defaut, classe_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    def desactiver(self, classe_id):
        """
        Désactive une classe (ne la supprime pas).
        
        Args:
            classe_id: ID de la classe à désactiver
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE classe SET actif = 0 WHERE id = ?",
                (classe_id,)
            )
            conn.commit()
        finally:
            conn.close()
    
    def activer(self, classe_id):
        """
        Réactive une classe.
        
        Args:
            classe_id: ID de la classe à réactiver
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE classe SET actif = 1 WHERE id = ?",
                (classe_id,)
            )
            conn.commit()
        finally:
            conn.close()
    
    def est_utilisee(self, classe_id):
        """
        Vérifie si une classe est utilisée par des élèves.
        
        Args:
            classe_id: ID de la classe
            
        Returns:
            bool: True si la classe est utilisée, False sinon
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT COUNT(*) as count FROM eleve WHERE classe = (SELECT nom FROM classe WHERE id = ?)",
                (classe_id,)
            )
            row = cursor.fetchone()
            return row['count'] > 0
        finally:
            conn.close()
