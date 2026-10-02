# EduPaie - Gestion des Paiements Scolaires

Application desktop de gestion des paiements scolaires développée pour une secrétaire sans connaissances techniques.

## Présentation

EduPaie est une application de gestion des paiements scolaires conçue pour simplifier le travail quotidien d'une secrétaire scolaire. Elle permet de gérer les élèves, d'enregistrer les paiements, de générer des reçus PDF numérotés et de suivre l'état des comptes de manière fiable et intuitive.

L'application a été développée dans le cadre d'un projet scolaire individuel avec pour objectif de démontrer une architecture logicielle propre, une gestion des erreurs robuste et une interface utilisateur adaptée aux utilisateurs non techniques.

## Caractéristiques

- **Interface PySide6** : Interface graphique moderne et intuitive
- **Base de données SQLCipher** : Données actives chiffrées avec une clé protégée par DPAPI pour l'utilisateur Windows courant
- **Architecture en couches** : Séparation claire entre données, logique métier et interface
- **Code lisible** : Commenté en français, avec gestion des erreurs
- **Exécutable Windows autonome** : Pas besoin d'installer Python
- **Gestion globale des exceptions** : L'application ne plante jamais

## Fonctionnalités

### Gestion des élèves
- Ajout, modification et suppression d'élèves
- Recherche par nom ou prénom
- Filtrage par classe
- Validation des données (format de l'année scolaire, montants positifs)

### Calcul automatique des soldes
- Calcul en temps réel du solde restant pour chaque élève
- Détermination automatique du statut (Soldé, Partiellement payé, Non payé)
- Affichage coloré selon le statut (vert, orange, rouge)

### Enregistrement des paiements
- Enregistrement de paiements rattachés aux élèves
- Validation du montant (ne peut pas dépasser le solde)
- Numérotation automatique des reçus (format REC-AAAA-NNNNN)
- Modes de paiement : espèces, chèque, virement, mobile money
- Transaction atomique pour garantir la cohérence des données

### Historique des paiements
- Fiche élève détaillée avec historique chronologique
- Affichage du solde après chaque paiement
- Réimpression des reçus à l'identique

### Génération de reçus PDF
- Génération automatique de reçus PDF numérotés
- Contenu complet : élève, paiement, solde, signature
- Réimpression identique grâce au stockage du solde après paiement
- Ouverture automatique avec la visionneuse par défaut

### Tableau de bord & Pilotage
- Indicateurs globaux : nombre d'élèves, total encaissé, total restant dû, élèves non soldés
- **Taux de recouvrement en temps réel** (%)
- Recherche rapide et filtrage par statut
- **Double-clic direct sur un élève** pour consulter sa fiche
- **Exportation CSV (Excel)** du tableau en 1 clic
- Mise à jour instantanée après chaque opération

### Expérience Utilisateur (UX) & Design Moderne
- **Design System moderne** : Palette sobre et professionnelle (Tailwind Blue, Emerald, Amber, Rose), badges pastel
- **Barre d'outils supérieure** : Accès direct aux écrans clés et actions rapides (Nouveau versement, Nouvel élève)
- **Raccourcis clavier** : `Ctrl+1` (Dashboard), `Ctrl+2` (Élèves), `Ctrl+P` (Paiement), `Ctrl+N` (Nouvel élève), `F5` (Actualiser), `F1` (Aide)
- **Menu contextuel (clic droit)** sur les élèves pour actions rapides
- **Dialogue de versement intelligent** : Raccourcis de montant ("Payer tout le solde", "50%") et aperçu dynamique du solde restant
- **Guide d'utilisation et aide intégrés** accessibles via F1
- **Reçus PDF certifiés** avec présentation officielle soignée
- **Icône d'application haute résolution** intégrée (ICO et PNG)

## Structure du projet

```
edupaie/
├── main.py              # Point d'entrée de l'application
├── requirements.txt     # Dépendances Python
├── build.bat            # Script de construction de l'exécutable
├── README.md           # Documentation du projet
├── data/
│   └── edupaie-seed.db # Base de démonstration embarquée (non destinée aux données réelles)
├── database/
│   ├── schema.sql      # Schéma de la base de données
│   ├── seed.py         # Script de peuplement de la base
│   └── connection.py   # Connexion à la base de données
├── repositories/       # Accès aux données (DAO)
│   ├── eleve_repository.py
│   └── paiement_repository.py
├── services/           # Logique métier
│   ├── eleve_service.py
│   ├── solde_service.py
│   ├── paiement_service.py
│   ├── recu_service.py
│   ├── recu_pdf.py
│   ├── fiche_eleve_service.py
│   └── dashboard_service.py
├── ui/                 # Fenêtres PySide6
│   ├── main_window.py
│   ├── eleves_widget.py
│   ├── eleve_form_dialog.py
│   ├── paiement_dialog.py
│   ├── fiche_eleve_dialog.py
│   └── dashboard_widget.py
├── resources/          # Icônes et ressources
├── utils/              # Utilitaires
│   ├── resource_utils.py
│   └── error_handler.py
├── tests/              # Tests unitaires
│   ├── test_solde_service.py
│   ├── test_paiement_service.py
│   ├── test_recu_pdf.py
│   └── test_dashboard_service.py
└── docs/               # Documentation
    ├── schema.md       # Schéma MCD/UML et explications
    ├── documentation.md  # Documentation technique complète
    ├── manuel_utilisateur.md  # Manuel utilisateur
    ├── fiche_soutenance.md  # Plan de soutenance
    └── guide_installation.md  # Guide d'installation pour l'exécutable
```

## Installation pour le développement

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Clonez le dépôt ou téléchargez les fichiers
2. Naviguez vers le répertoire du projet
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Initialisation de la base de données

Pour recréer le seed de démonstration (ne jamais utiliser sur une base utilisateur) :

```bash
python database/seed.py
```

Cette commande :
- Crée le fichier plaintext `data/edupaie-seed.db` à partir du schéma
- Insère 20 élèves de test dans plusieurs classes
- Insère 36 paiements variés (soldés, partiellement payés, non payés)
- Initialise la séquence de numérotation des reçus

Au premier lancement, l'application chiffre ce seed et stocke la base active dans `%LOCALAPPDATA%\EduPaie\data\edupaie.db`. La clé SQLCipher est protégée par DPAPI dans `%LOCALAPPDATA%\EduPaie\keys\database.dpapi`. Les anciennes bases adjacentes à l'EXE sont migrées après vérification; conservez une sauvegarde avant mise à jour.

## Lancement de l'application (développement)

```bash
python main.py
```

## Tests

Pour exécuter les tests unitaires :

```bash
python -m unittest discover tests
```

Les tests couvrent :
- Calcul du solde et détermination du statut
- Enregistrement des paiements
- Génération des reçus PDF
- Indicateurs du tableau de bord

## Construction de l'exécutable Windows

Pour créer un exécutable autonome Windows :

1. Placez une icône `edupaie.ico` dans le dossier `resources/` (optionnel)
2. Exécutez le script de construction :
   ```cmd
   build.bat
   ```
3. L'exécutable `EduPaie.exe` sera créé dans le dossier `dist/`

**Note** : Le script installe automatiquement PyInstaller s'il n'est pas installé.

### Configuration PyInstaller

La commande PyInstaller utilisée :
```cmd
pyinstaller --noconfirm EduPaie.spec
```

Options :
- `--onefile` : Crée un seul fichier exécutable
- `--windowed` : Pas de console (application GUI)
- `--add-data` : Embarque la base de données initiale et les ressources
- `--name` : Nom de l'exécutable

## Architecture

Le projet respecte une architecture en couches stricte :

### 1. Couche d'accès aux données (`repositories/`)
- Encapsule tout le code SQL
- Utilise des requêtes paramétrées (sécurité contre les injections)
- Aucune logique métier
- Méthodes : CRUD pour chaque entité

### 2. Couche logique métier (`services/`)
- Contient les règles métier et validations
- Convertit les erreurs de base en erreurs métier
- Fonctions pures pour les calculs (sans effet de bord)
- Orchestre les appels aux repositories

### 3. Couche interface (`ui/`)
- Widgets PySide6
- Gère les interactions utilisateur
- Affiche les erreurs avec QMessageBox
- N'exécute jamais de SQL directement

## Conventions de développement

- Code commenté en français
- Messages de commit en français à l'impératif
- Git flow avec branches par fonctionnalité
- Pas d'ORM, utilisation directe de sqlite3
- SQL uniquement dans `repositories/`
- Aucun `sqlite3` import dans `ui/`

## Documentation

Pour plus de détails, consultez :

- [docs/documentation.md](docs/documentation.md) : Documentation technique complète (architecture, modélisation, choix techniques)
- [docs/manuel_utilisateur.md](docs/manuel_utilisateur.md) : Manuel utilisateur pour la secrétaire
- [docs/fiche_soutenance.md](docs/fiche_soutenance.md) : Plan de soutenance et questions du jury
- [docs/guide_installation.md](docs/guide_installation.md) : Guide d'installation pour l'exécutable
- [docs/schema.md](docs/schema.md) : Schéma MCD/UML de la base de données

## Licence

Ce projet a été développé dans un cadre éducatif.
