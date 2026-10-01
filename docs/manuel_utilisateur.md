# Manuel Utilisateur - EduPaie

Bienvenue dans EduPaie, l'application de gestion des paiements scolaires. Ce manuel vous explique comment utiliser les fonctionnalités principales au quotidien.

## Démarrage de l'application

### Premier lancement
1. Double-cliquez sur `EduPaie.exe`
2. L'application s'ouvre et affiche le tableau de bord
3. Les données de test sont déjà chargées (20 élèves, 36 paiements)

### Utilisation quotidienne
1. Double-cliquez sur `EduPaie.exe`
2. L'application s'ouvre sur le tableau de bord
3. Utilisez le menu pour accéder aux différentes fonctions

---

## Enregistrer un nouvel élève

### Étape 1 : Ouvrir la gestion des élèves
1. Cliquez sur le menu **Élèves**
2. Cliquez sur **Gérer les élèves**

### Étape 2 : Ajouter un élève
1. Cliquez sur le bouton **Ajouter**
2. Remplissez les champs :
   - **Nom** : Le nom de famille de l'élève
   - **Prénom** : Le prénom de l'élève
   - **Classe** : La classe (ex: CP, CE1, 6ème)
   - **Année scolaire** : L'année scolaire (ex: 2025-2026)
   - **Total dû** : Le montant total des frais (en francs CFA)
3. Cliquez sur **OK** pour enregistrer

### Étape 3 : Vérification
- L'élève apparaît dans la liste
- Vous pouvez le rechercher par nom ou filtrer par classe

---

## Enregistrer un paiement

### Étape 1 : Sélectionner l'élève
1. Cliquez sur le menu **Élèves**
2. Cliquez sur **Gérer les élèves**
3. Sélectionnez l'élève dans la liste (cliquez sur la ligne)

### Étape 2 : Enregistrer le paiement
1. Cliquez sur le bouton **Enregistrer paiement**
2. Le formulaire s'ouvre avec les informations de l'élève
3. Remplissez les champs :
   - **Montant** : Le montant payé (en francs CFA)
   - **Date** : La date du paiement (par défaut : aujourd'hui)
   - **Mode** : Le mode de paiement (espèces, chèque, virement, mobile money)
4. Cliquez sur **Enregistrer**

### Étape 3 : Confirmation
- Un message de succès s'affiche avec le numéro de reçu
- Le solde restant est indiqué
- Le reçu peut être généré immédiatement (optionnel)

---

## Imprimer un reçu

### Option 1 : Immédiatement après un paiement
1. Après avoir enregistré un paiement, cliquez sur **Oui** quand on vous demande
2. Le reçu PDF s'ouvre automatiquement
3. Imprimez-le depuis votre visionneuse PDF

### Option 2 : Réimprimer un reçu existant
1. Cliquez sur le menu **Élèves**
2. Cliquez sur **Gérer les élèves**
3. Double-cliquez sur l'élève (ou cliquez sur **Fiche élève**)
4. Dans la liste des paiements, sélectionnez le paiement voulu
5. Cliquez sur **Voir / Ré-imprimer le reçu**
6. Le reçu PDF s'ouvre automatiquement
7. Imprimez-le depuis votre visionneuse PDF

---

## Consulter la fiche d'un élève

### Étape 1 : Ouvrir la fiche
1. Cliquez sur le menu **Élèves**
2. Cliquez sur **Gérer les élèves**
3. Double-cliquez sur l'élève (ou cliquez sur **Fiche élève**)

### Étape 2 : Consulter les informations
- **En haut** : Identité de l'élève, total dû, payé, solde, statut
- **En bas** : Historique chronologique de tous les paiements
- **Couleurs** : Vert (soldé), Orange (partiellement payé), Rouge (non payé)

### Étape 3 : Actions depuis la fiche
- **Enregistrer un paiement** : Cliquez sur le bouton correspondant
- **Voir un reçu** : Sélectionnez un paiement, cliquez sur **Voir / Ré-imprimer le reçu**

---

## Tableau de bord

### Accès
- Le tableau de bord s'affiche au démarrage
- Vous pouvez y accéder via le menu **Tableau de bord** > **Afficher le tableau de bord**

### Indicateurs
- **Nombre d'élèves** : Le total d'élèves enregistrés
- **Total encaissé** : La somme de tous les paiements
- **Total restant dû** : La somme des soldes de tous les élèves
- **Élèves non soldés** : Le nombre d'élèves qui doivent encore payer

### Liste des élèves
- Vous pouvez filtrer par statut (Tous, Soldé, Partiellement payé, Non payé)
- Utilisez le menu déroulant pour choisir le filtre
- Cliquez sur les en-têtes de colonnes pour trier

---

## Rechercher un élève

### Étape 1 : Ouvrir la gestion des élèves
1. Cliquez sur le menu **Élèves**
2. Cliquez sur **Gérer les élèves**

### Étape 2 : Rechercher
1. Dans la barre de recherche, tapez le nom ou le prénom
2. La liste se met à jour automatiquement
3. Pour annuler la recherche, effacez le champ

### Étape 3 : Filtrer par classe
1. Utilisez le menu déroulant des classes
2. Sélectionnez la classe souhaitée
3. Pour voir toutes les classes, sélectionnez "Toutes les classes"

---

## Modifier un élève

### Étape 1 : Sélectionner l'élève
1. Cliquez sur le menu **Élèves**
2. Cliquez sur **Gérer les élèves**
3. Sélectionnez l'élève dans la liste

### Étape 2 : Modifier
1. Cliquez sur le bouton **Modifier**
2. Modifiez les champs nécessaires
3. Cliquez sur **OK** pour enregistrer

**Note** : Si l'élève a des paiements, vous ne pouvez pas le supprimer (pour préserver les reçus).

---

## Conseils utiles

### Le solde est calculé automatiquement
- Vous n'avez pas besoin de calculer les soldes
- L'application le fait automatiquement après chaque paiement

### Les paiements ne peuvent être modifiés
- Un paiement enregistré ne peut être ni modifié ni supprimé
- Si une erreur est commise, enregistrez un nouveau paiement et notez l'erreur

### Sauvegarde des données
- Les données sont dans le dossier `data/` à côté de l'exécutable
- Sauvegardez régulièrement ce dossier
- Pour restaurer, remplacez le dossier `data/` par votre sauvegarde

### En cas d'erreur
- Si un message d'erreur s'affiche, l'application continue de fonctionner
- Les erreurs sont enregistrées dans `edupaie_error.log`
- Contactez le support avec ce fichier en cas de problème récurrent

---

## En cas de problème

### L'application ne démarre pas
- Vérifiez que vous avez les droits d'écriture dans le dossier
- Essayez de lancer en tant qu'administrateur
- Désactivez temporairement votre antivirus

### Le reçu ne s'ouvre pas
- Vérifiez que vous avez une visionneuse PDF installée
- Le dossier `data/recus/` doit être accessible

### La base de données n'est pas créée
- Supprimez le dossier `data/` s'il existe
- Relancez l'application (elle recréera la base automatiquement)

---

## Besoin d'aide ?

Pour plus d'informations, consultez :
- Le guide d'installation : `docs/guide_installation.md`
- La documentation technique : `docs/documentation.md`

En cas de problème persistant, contactez le support technique avec :
- Le message d'erreur exact
- Le fichier `edupaie_error.log`
