"""
Module de connexion à la base de données EduPaie.
Fournit une fonction get_connection() robuste et compatible PyInstaller.
"""

import sqlite3
import os
from utils.resource_utils import get_database_path, get_initial_database_path, ensure_data_dirs, copy_initial_database_if_needed


def appliquer_migration():
    """
    Applique la migration de la base de données (idempotente).
    Exécute le schema.sql qui utilise CREATE TABLE IF NOT EXISTS.
    Ne modifie pas les données existantes.
    """
    db_path = get_database_path()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(schema_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
            cursor.executescript(schema)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_connection():
    """
    Crée et retourne une connexion à la base de données.
    
    Configuration :
    - PRAGMA foreign_keys = ON : active les contraintes de clés étrangères
    - row_factory = sqlite3.Row : permet d'accéder aux colonnes par nom
    
    En PyInstaller avec --onefile, copie la base initiale si elle n'existe pas.
    Applique la migration au premier appel.
    
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
    
    # Applique la migration (idempotente)
    appliquer_migration()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn
