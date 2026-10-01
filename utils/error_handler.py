"""
Gestionnaire global d'exceptions pour EduPaie.
Capture toutes les exceptions non gérées, affiche un QMessageBox et écrit un log.
"""

import sys
import os
import traceback
from datetime import datetime


def get_log_file_path():
    """
    Retourne le chemin vers le fichier de log.
    
    Returns:
        str: Chemin absolu vers le fichier de log
    """
    from utils.resource_utils import get_app_dir
    app_dir = get_app_dir()
    return os.path.join(app_dir, "edupaie_error.log")


def write_to_log(error_message, traceback_str):
    """
    Écrit l'erreur dans le fichier de log.
    
    Args:
        error_message: Message d'erreur
        traceback_str: Traceback complet
    """
    log_path = get_log_file_path()
    
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"DATE : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            f.write(f"ERREUR :\n{error_message}\n\n")
            f.write(f"TRACEBACK :\n{traceback_str}\n")
    except Exception as e:
        # Si on ne peut pas écrire le log, on ne plante pas l'application
        print(f"Impossible d'écrire le log : {str(e)}")


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Gestionnaire global d'exceptions.
    
    Affiche un QMessageBox avec l'erreur et écrit dans le fichier de log.
    Ne ferme pas l'application.
    
    Args:
        exc_type: Type de l'exception
        exc_value: Valeur de l'exception
        exc_traceback: Traceback de l'exception
    """
    # Construit le message d'erreur
    error_message = f"{exc_type.__name__}: {str(exc_value)}"
    traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Écrit dans le fichier de log
    write_to_log(error_message, traceback_str)
    
    # Affiche un QMessageBox si QApplication existe
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        
        if app is not None:
            # Message pour l'utilisateur
            user_message = (
                "Une erreur inattendue s'est produite.\n\n"
                "L'application continue de fonctionner.\n"
                "Les détails de l'erreur ont été enregistrés dans le fichier de log.\n\n"
                f"Emplacement du log : {get_log_file_path()}"
            )
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Erreur EduPaie")
            msg_box.setText(user_message)
            msg_box.setDetailedText(error_message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        else:
            # Si QApplication n'existe pas encore, affiche dans la console
            print(f"ERREUR : {error_message}")
            print(f"Traceback :\n{traceback_str}")
    except ImportError:
        # PySide6 n'est pas installé (cas des tests)
        print(f"ERREUR : {error_message}")
        print(f"Traceback :\n{traceback_str}")


def setup_exception_handler():
    """
    Configure le gestionnaire global d'exceptions.
    Doit être appelé au démarrage de l'application.
    """
    sys.excepthook = handle_exception
