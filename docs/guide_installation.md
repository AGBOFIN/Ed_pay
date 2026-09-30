# Guide d'installation - EduPaie

Ce guide explique comment installer et utiliser l'exécutable EduPaie sur une machine Windows sans Python.

## Prérequis

- Windows 10 ou Windows 11
- Aucune installation de Python requise

## Installation

### Étape 1 : Récupérer l'exécutable

1. Téléchargez le fichier `EduPaie.exe`
2. Placez-le dans un dossier vide sur votre ordinateur (ex: `C:\EduPaie\`)

### Étape 2 : Premier lancement

1. Double-cliquez sur `EduPaie.exe`
2. Au premier lancement, l'application crée automatiquement :
   - Un dossier `data/` à côté de l'exécutable
   - Une base de données `data/edupaie.db` (avec les données de test)
   - Un dossier `data/recus/` pour les reçus PDF

### Étape 3 : Utilisation

L'application est prête à être utilisée :
- Vous pouvez gérer les élèves
- Enregistrer des paiements
- Générer des reçus PDF
- Consulter le tableau de bord

## Structure des fichiers après installation

```
EduPaie/
├── EduPaie.exe                    # L'exécutable
├── data/                          # Dossier créé automatiquement
│   ├── edupaie.db                 # Base de données
│   └── recus/                     # Dossier des reçus PDF
│       ├── REC-2026-00001.pdf
│       ├── REC-2026-00002.pdf
│       └── ...
└── edupaie_error.log              # Fichier de log (créé en cas d'erreur)
```

## Fonctionnalités

### Gestion des élèves
- **Menu Élèves > Gérer les élèves** : Ajouter, modifier, supprimer des élèves
- **Double-clic sur un élève** : Ouvrir sa fiche détaillée

### Enregistrement des paiements
- **Bouton "Enregistrer paiement"** : Sélectionnez un élève, puis cliquez sur ce bouton
- **Menu Paiements > Enregistrer un paiement** : Alternative via le menu

### Reçus PDF
- Après chaque paiement, l'application propose de générer le reçu PDF
- Le reçu s'ouvre automatiquement avec votre visionneuse PDF par défaut
- Pour réimprimer un reçu : Ouvrez la fiche élève, sélectionnez le paiement, cliquez sur "Voir / Ré-imprimer le reçu"

### Tableau de bord
- Le tableau de bord s'affiche au démarrage
- Il montre les indicateurs globaux (nombre d'élèves, total encaissé, etc.)
- Vous pouvez filtrer la liste des élèves par statut (Soldé, Partiellement payé, Non payé)

## Gestion des erreurs

Si une erreur survient :
- Un message d'erreur s'affiche
- L'application continue de fonctionner
- Les détails de l'erreur sont enregistrés dans `edupaie_error.log`
- Consultez ce fichier pour diagnostiquer les problèmes

## Sauvegarde des données

Pour sauvegarder vos données :
1. Fermez l'application
2. Copiez le dossier `data/` complet
3. Collez-le dans un emplacement de sauvegarde (ex: clé USB, disque dur externe)

Pour restaurer vos données :
1. Fermez l'application
2. Remplacez le dossier `data/` par votre sauvegarde
3. Relancez l'application

## Mise à jour de l'application

Pour mettre à jour EduPaie :
1. Fermez l'application
2. Sauvegardez votre dossier `data/` (voir ci-dessus)
3. Remplacez `EduPaie.exe` par la nouvelle version
4. Relancez l'application
5. Vos données seront conservées

## Problèmes fréquents

### L'application ne démarre pas
- Vérifiez que vous avez les droits d'écriture dans le dossier
- Désactivez temporairement votre antivirus (certains bloquent les exécutables Python)
- Essayez de lancer l'application en tant qu'administrateur

### La base de données n'est pas créée
- Vérifiez que vous avez les droits de création de dossiers
- Supprimez manuellement le dossier `data/` s'il existe et relancez l'application

### Les reçus PDF ne s'ouvrent pas
- Vérifiez que vous avez une visionneuse PDF installée (Adobe Reader, etc.)
- Le dossier `data/recus/` doit être accessible en écriture

### Message d'erreur récurrent
- Consultez le fichier `edupaie_error.log`
- Contactez le support avec le contenu du fichier de log

## Support

En cas de problème :
1. Consultez le fichier `edupaie_error.log`
2. Notez le message d'erreur exact
3. Contactez le support technique avec ces informations
