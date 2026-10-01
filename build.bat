@echo off
REM Script de construction de l'exécutable EduPaie avec PyInstaller

echo ========================================
echo Construction de l'exécutable EduPaie
echo ========================================
echo.

REM Vérifie que PyInstaller est installé
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller n'est pas installe. Installation en cours...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Erreur lors de l'installation de PyInstaller.
        pause
        exit /b 1
    )
)

REM Nettoie les builds précédents
echo Nettoyage des builds precedents...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Construit l'exécutable
echo Construction de l'exécutable...
echo.

REM Vérifie si l'icône existe
if exist "resources\edupaie.ico" (
    echo Utilisation de l'icône resources\edupaie.ico
    pyinstaller --onefile --windowed --add-data "data/edupaie.db;data" --add-data "resources;resources" --name "EduPaie" --icon=resources\edupaie.ico main.py
) else (
    echo AVERTISSEMENT : L'icône resources\edupaie.ico n'existe pas.
    echo L'exécutable sera construit sans icône.
    pyinstaller --onefile --windowed --add-data "data/edupaie.db;data" --add-data "resources;resources" --name "EduPaie" main.py
)

if %errorlevel% neq 0 (
    echo.
    echo Erreur lors de la construction de l'exécutable.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Construction terminee avec succes !
echo ========================================
echo.
echo L'exécutable se trouve dans : dist\EduPaie.exe
echo.
echo IMPORTANT :
echo - Placez l'exécutable dans un dossier vide
echo - Au premier lancement, la base de données sera copiee automatiquement
echo - Le dossier data/ sera cree a cote de l'exécutable
echo - Les reçus PDF seront enregistres dans data/recus/
echo.
pause
