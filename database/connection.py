"""
Module de connexion à la base de données EduPaie.
Fournit une fonction get_connection() robuste et compatible PyInstaller.
"""

import sqlite3
import os
from utils.resource_utils import get_database_path, get_initial_database_path, ensure_data_dirs, copy_initial_database_if_needed


def get_connection():
    """
    Crée et retourne une connexion à la base de données.
    
    Configuration :
    - PRAGMA foreign_keys = ON : active les contraintes de clés étrangères
    - row_factory = sqlite3.Row : permet d'accéder aux colonnes par nom
    
    En PyInstaller avec --onefile, copie la base initiale si elle n'existe pas.
    
    Returns:
        sqlite3.Connection : Connexion à la base de données
    """
    # Assure que les dossiers de données existent
    ensure_data_dirs()
    
    # Copie la base initiale si elle n'existe pas (cas PyInstaller --onefile)
    copy_initial_database_if_needed()
    
    db_path = get_database_path()
    
    # Vérifie que le fichier de base de données existe
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Base de données introuvable : {db_path}\n"
            "En développement : exécutez python database/seed.py pour créer la base.\n"
            "En exécutable : la base initiale devrait être copiée automatiquement."
        )
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn
