"""
Repository pour la gestion des paramètres.
Encapsule tout l'accès aux données pour la table parametre.
"""

import sqlite3
from database.connection import get_connection


class ParametreRepository:
    """Repository pour les opérations sur les paramètres."""
    
    def obtenir(self, cle):
        """
        Récupère un paramètre par sa clé.
        
        Args:
            cle: Clé du paramètre
            
        Returns:
            str: Valeur du paramètre, ou None si non trouvé
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT valeur FROM parametre WHERE cle = ?",
                (cle,)
            )
            row = cursor.fetchone()
            return row['valeur'] if row else None
        finally:
            conn.close()
    
    def definir(self, cle, valeur):
        """
        Définit ou met à jour un paramètre.
        
        Args:
            cle: Clé du paramètre
            valeur: Valeur du paramètre
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO parametre (cle, valeur) VALUES (?, ?)
                ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur
                """,
                (cle, valeur)
            )
            conn.commit()
        finally:
            conn.close()
    
    def obtenir_tous(self):
        """
        Récupère tous les paramètres.
        
        Returns:
            dict: Dictionnaire de tous les paramètres
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT cle, valeur FROM parametre")
            rows = cursor.fetchall()
            return {row['cle']: row['valeur'] for row in rows}
        finally:
            conn.close()
