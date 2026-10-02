"""
Module de connexion à la base de données EduPaie.
Fournit une fonction get_connection() robuste et compatible PyInstaller.
"""

import os

from sqlcipher3 import dbapi2 as sqlite3
from database.encryption import load_or_create_key, verify_encrypted_database
from utils.resource_utils import (
    get_database_path,
    get_database_key_path,
    ensure_data_dirs,
    copy_initial_database_if_needed,
)


_DATABASE_KEYS = {}


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
    Initialise ou migre également la base chiffrée du profil Windows courant.

    Returns:
        sqlite3.Connection : Connexion à la base de données
    """
    ensure_data_dirs()

    db_path = get_database_path()
    key_path = get_database_key_path()
    cache_key = (db_path, key_path)
    key = _DATABASE_KEYS.get(cache_key)
    if key is None:
        key = copy_initial_database_if_needed()
        if key is None:
            key = load_or_create_key(key_path, create_if_missing=False)
            verify_encrypted_database(db_path, key)
        _DATABASE_KEYS[cache_key] = key

    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Base de données introuvable : {db_path}\n"
            "En développement : exécutez python database/seed.py pour créer la base.\n"
            "En exécutable : la base initiale devrait être copiée automatiquement."
        )

    appliquer_migration()

    conn = sqlite3.connect(db_path)
    conn.execute(f'PRAGMA key = "x\'{key.hex()}\'"')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn
