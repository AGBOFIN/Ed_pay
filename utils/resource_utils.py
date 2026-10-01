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
        base_path = os.path.dirname(os.path.abspath(__file__))
    
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
    Retourne le chemin vers la base de données.
    
    En PyInstaller avec --onefile, la base doit être à côté de l'exécutable
    car le dossier temporaire est en lecture seule.
    
    Returns:
        str: Chemin absolu vers la base de données
    """
    app_dir = get_app_dir()
    return os.path.join(app_dir, "data", "edupaie.db")


def get_initial_database_path():
    """
    Retourne le chemin vers la base de données initiale (embarquée).
    
    Cette base est copiée à côté de l'exécutable si elle n'existe pas.
    
    Returns:
        str: Chemin absolu vers la base de données initiale
    """
    return resource_path("data/edupaie.db")


def get_recus_dir():
    """
    Retourne le chemin vers le dossier des reçus PDF.
    
    En PyInstaller, ce dossier doit être à côté de l'exécutable.
    
    Returns:
        str: Chemin absolu vers le dossier des reçus
    """
    app_dir = get_app_dir()
    return os.path.join(app_dir, "data", "recus")


def ensure_data_dirs():
    """
    S'assure que les dossiers de données existent.
    Crée data/ et data/recus si nécessaire.
    """
    app_dir = get_app_dir()
    data_dir = os.path.join(app_dir, "data")
    recus_dir = os.path.join(data_dir, "recus")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    if not os.path.exists(recus_dir):
        os.makedirs(recus_dir)


def copy_initial_database_if_needed():
    """
    Copie la base de données initiale si elle n'existe pas.
    
    En PyInstaller avec --onefile, la base doit être à côté de l'exécutable.
    Si elle n'existe pas, on copie la base embarquée à cet endroit.
    """
    db_path = get_database_path()
    initial_db_path = get_initial_database_path()
    
    if not os.path.exists(db_path):
        # Assure que le dossier data/ existe
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Copie la base initiale
        import shutil
        shutil.copy2(initial_db_path, db_path)
