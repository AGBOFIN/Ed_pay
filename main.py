"""
Point d'entrée de l'application EduPaie.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from utils.error_handler import setup_exception_handler


def main():
    """Fonction principale de l'application."""
    # Configure le gestionnaire global d'exceptions
    setup_exception_handler()
    
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("EduPaie")
    app.setOrganizationName("EduPaie")
    
    # Crée et affiche la fenêtre principale
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
