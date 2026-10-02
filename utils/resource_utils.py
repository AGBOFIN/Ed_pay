"""
Utilitaires pour la gestion des chemins de ressources.
Fonctionne en développement et dans PyInstaller.
"""

import sys
import os


def resource_path(relative_path):
    """
    Retourne le chemin absolu vers une ressource.
    
    Fonctionne en développement (chemin relatif) et dans PyInstaller (sys._MEIPASS).
    
    Args:
        relative_path: Chemin relatif depuis la racine du projet
        
    Returns:
        str: Chemin absolu vers la ressource
    """
    try:
        # PyInstaller crée un dossier temporaire et le stocke dans _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # En développement, utilise le répertoire du script
        base_path = get_app_dir()
    
    return os.path.join(base_path, relative_path)


def get_app_dir():
    """
    Retourne le répertoire de l'application (là où se trouve l'exécutable).
    
    En développement : répertoire du projet
    En PyInstaller : répertoire contenant l'exécutable
    
    Returns:
        str: Chemin absolu du répertoire de l'application
    """
    if getattr(sys, 'frozen', False):
        # En exécutable PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # En développement
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_database_path():
    """
    Retourne le chemin vers la base chiffrée du profil Windows courant.
    
    Returns:
        str: Chemin absolu vers la base de données
    """
    return os.path.join(get_user_data_dir(), "data", "edupaie.db")


def get_user_data_dir():
    """Retourne le dossier privé EduPaie du profil Windows courant."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        local_app_data = os.path.join(os.path.expanduser("~"), "AppData", "Local")
    return os.path.join(local_app_data, "EduPaie")


def get_database_key_path():
    """Retourne le chemin de la clé SQLCipher protégée par DPAPI."""
    return os.path.join(get_user_data_dir(), "keys", "database.dpapi")


def get_legacy_database_path():
    """Retourne l'ancien emplacement de la base active à migrer."""
    return os.path.join(get_app_dir(), "data", "edupaie.db")


def get_initial_database_path():
    """
    Retourne le chemin vers la base de données initiale (embarquée).
    
    Cette base est copiée à côté de l'exécutable si elle n'existe pas.
    
    Returns:
        str: Chemin absolu vers la base de données initiale
    """
    return resource_path("data/edupaie-seed.db")


def get_recus_dir():
    """
    Retourne le chemin vers le dossier privé des reçus PDF.
    
    Returns:
        str: Chemin absolu vers le dossier des reçus
    """
    return os.path.join(get_user_data_dir(), "data", "recus")


def ensure_data_dirs():
    """
    S'assure que les dossiers de données existent.
    Crée data/ et data/recus si nécessaire.
    """
    data_dir = os.path.join(get_user_data_dir(), "data")
    recus_dir = os.path.join(data_dir, "recus")
    os.makedirs(recus_dir, exist_ok=True)


def copy_initial_database_if_needed():
    """Initialise ou migre la base active vers SQLCipher."""
    from database.encryption import ensure_encrypted_database

    legacy_path = get_legacy_database_path()
    return ensure_encrypted_database(
        get_database_path(),
        get_database_key_path(),
        get_initial_database_path(),
        legacy_database_path=legacy_path,
        remove_legacy=bool(legacy_path and getattr(sys, 'frozen', False)),
    )
