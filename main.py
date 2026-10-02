"""
Point d'entrée de l'application EduPaie.
"""

import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from ui.main_window import MainWindow
from ui.theme import apply_theme
from utils.error_handler import setup_exception_handler
from utils.resource_utils import resource_path


def main():
    """Fonction principale de l'application."""
    # Configure le gestionnaire global d'exceptions
    setup_exception_handler()
    
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("EduPaie")
    app.setOrganizationName("EduPaie")
    
    # Définition de l'icône de l'application
    icon_path = resource_path("resources/edupaie.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # Application de la police système par défaut et du thème moderne
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    apply_theme(app)
    
    # Crée et affiche la fenêtre principale
    window = MainWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
