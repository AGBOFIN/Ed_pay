# Fiche de Soutenance - EduPaie

## Plan de démonstration (10-15 minutes)

### Introduction (2 minutes)
- Présentation du contexte : application de gestion des paiements scolaires
- Objectif : faciliter le travail d'une secrétaire sans connaissances techniques
- Technologies utilisées : Python 3.10+, PySide6, SQLite

### Architecture (3 minutes)
- Présentation de l'architecture en couches
- Explication de la séparation des responsabilités (repositories, services, UI)
- Justification : maintenabilité, testabilité, séparation des préoccupations

### Démonstration du jeu de test (5 minutes)
1. **Tableau de bord**
   - Montrer les 4 indicateurs globaux
   - Expliquer la requête d'agrégation
   - Filtrer par statut

2. **Gestion des élèves**
   - Ajouter un nouvel élève
   - Montrer la validation des données
   - Rechercher et filtrer

3. **Enregistrement d'un paiement**
   - Sélectionner un élève
   - Enregistrer un paiement
   - Montrer la numérotation automatique du reçu
   - Générer le reçu PDF

4. **Fiche élève**
   - Ouvrir la fiche d'un élève
   - Montrer l'historique des paiements
   - Réimprimer un reçu

5. **Gestion des erreurs**
   - Montrer le gestionnaire global d'exceptions
   - Expliquer que l'application ne plante jamais

### Conclusion (2 minutes)
- Récapitulatif des fonctionnalités
- Choix techniques justifiés
- Limites connues
- Perspectives d'amélioration

---

## Questions probables du jury

### Architecture et modélisation

**Q1 : Pourquoi avoir choisi une architecture en couches ?**
R : Pour séparer clairement les responsabilités. Les repositories gèrent l'accès aux données (SQL), les services contiennent la logique métier, et l'UI gère les interactions. Cela rend le code plus maintenable, testable et facilite l'évolution de l'application.

**Q2 : Pourquoi le solde est-il calculé et non stocké ?**
R : Pour éviter les incohérences. Si le solde était stocké, il pourrait devenir incorrect après une modification. En le calculant dynamiquement (total_du - total_payé), il est toujours exact. Pour les reçus, on stocke `solde_apres` pour garantir la réimpression identique.

**Q3 : Pourquoi avoir stocké `solde_apres` dans la table paiement ?**
R : Pour garantir que chaque réimpression de reçu soit identique à l'original. Si on recalculait le solde au moment de l'impression, un reçu pourrait changer si le total_du de l'élève est modifié entre-temps. `solde_apres` est un instantané du solde au moment du paiement.

**Q4 : Pourquoi les paiements sont-ils immuables (ni modifiables ni supprimables) ?**
R : Les reçus sont des documents légaux. Chaque numéro de reçu doit correspondre exactement à un paiement. Si on pouvait modifier un paiement, le numéro de reçu ne correspondrait plus à la réalité. Pour corriger une erreur, on enregistre un nouveau paiement et on note l'erreur manuellement.

**Q5 : Pourquoi avoir utilisé une table de séquence pour la numérotation des reçus ?**
R : Pour garantir l'unicité et la continuité des numéros. La contrainte UNIQUE en base empêche les doublons. L'année scolaire permet de recommencer la numérotation chaque année. La transaction atomique évite les doublons en cas de concurrence.

**Q6 : Pourquoi avoir utilisé `BEGIN IMMEDIATE` dans les transactions ?**
R : Pour verrouiller la base immédiatement lors de l'enregistrement d'un paiement. Cela empêche deux utilisateurs d'obtenir le même numéro de reçu en même temps. Si l'opération échoue, le rollback annule tout, garantissant la cohérence.

### Choix techniques

**Q7 : Pourquoi avoir choisi PySide6 plutôt que Tkinter ou PyQt ?**
R : PySide6 est le binding officiel Qt pour Python. Il offre des widgets riches, une documentation complète et une communauté active. Tkinter est trop basique, et PyQt a des problèmes de licence. PySide6 est moderne et performant.

**Q8 : Pourquoi avoir choisi SQLite plutôt qu'une autre base de données ?**
R : SQLite ne nécessite aucune installation de serveur, tout est dans un seul fichier. C'est idéal pour une application desktop avec un volume de données modéré (quelques centaines d'élèves). Elle supporte les transactions et les clés étrangères, ce qui est suffisant pour nos besoins.

**Q9 : Pourquoi ne pas avoir utilisé d'ORM (SQLAlchemy, Django ORM) ?**
R : Pour garder un contrôle total sur les requêtes SQL et éviter la complexité inutile. Pour un projet de cette taille, l'ORM apporte plus de complexité que de bénéfices. Les requêtes paramétrées sont simples et sécurisées.

**Q10 : Pourquoi avoir stocké les montants en francs CFA (entiers) plutôt qu'en décimaux ?**
R : Pour éviter les erreurs d'arrondi des nombres flottants. Les calculs financiers doivent être exacts. Avec des entiers, on évite les problèmes de précision. De plus, le franc CFA est la devise adaptée au contexte d'utilisation, et le formatage avec séparateur de milliers rend les montants lisibles.

**Q11 : Pourquoi avoir utilisé fpdf2 pour les reçus PDF ?**
R : C'est une bibliothèque légère et simple, suffisante pour des reçus basiques. Elle est compatible avec Python 3 et ne nécessite pas de dépendances complexes. Les polices standard supportent le latin-1, ce qui est suffisant pour l'usage français.

**Q12 : Pourquoi avoir ajouté un gestionnaire global d'exceptions ?**
R : Pour que l'application ne plante jamais. Si une erreur survient, un QMessageBox s'affiche avec un message clair, et l'erreur est enregistrée dans un fichier de log. L'utilisateur peut continuer à travailler. C'est crucial pour une secrétaire qui ne peut pas se permettre d'avoir l'application qui plante.

### Tests et validation

**Q13 : Comment avez-vous testé l'application ?**
R : J'ai écrit des tests unitaires pour les services (calcul du solde, enregistrement de paiements, génération de PDF, indicateurs du tableau de bord). J'ai également testé manuellement l'interface avec le jeu de test (20 élèves, 36 paiements).

**Q14 : Pourquoi avoir utilisé des fonctions pures dans SoldeService ?**
R : Pour faciliter les tests. Une fonction pure ne dépend que de ses paramètres et n'a pas d'effets de bord. On peut la tester sans avoir besoin d'une base de données ou de mock. Cela rend les tests plus simples et plus fiables.

**Q15 : Comment avez-vous assuré que la base de données peut être recréée de zéro ?**
R : Le script `seed.py` crée la base à partir de `schema.sql` et insère les données de test. On peut supprimer `edupaie.db` et relancer `seed.py` pour recréer la base. L'exécutable PyInstaller embarque la base initiale et la copie au premier lancement.

### Packaging et déploiement

**Q16 : Pourquoi avoir utilisé PyInstaller avec --onefile ?**
R : Pour créer un exécutable unique facile à distribuer. L'utilisateur n'a pas besoin d'installer Python. Avec --onefile, tout est embarqué dans un seul fichier. L'inconvénient est que le dossier temporaire est en lecture seule, mais j'ai géré cela avec `resource_utils` qui copie la base à côté de l'exe.

**Q17 : Comment avez-vous géré les chemins de fichiers pour PyInstaller ?**
R : J'ai créé une fonction `resource_path()` qui détecte si l'application tourne dans PyInstaller (via `sys._MEIPASS`) ou en développement. En PyInstaller, les ressources sont dans un dossier temporaire en lecture seule, donc j'ai configuré l'application pour copier la base et créer le dossier des reçus à côté de l'exécutable.

**Q18 : Pourquoi avoir ajouté un script build.bat ?**
R : Pour automatiser la construction de l'exécutable. Le script installe PyInstaller si nécessaire, nettoie les builds précédents, et exécute la commande PyInstaller avec les bonnes options. Cela simplifie le processus pour l'utilisateur.

### Sécurité et performances

**Q19 : Comment avez-vous sécurisé les requêtes SQL contre les injections ?**
R : En utilisant exclusivement des requêtes paramétrées avec `?`. Jamais de f-string ou de concaténation dans le SQL. Les paramètres sont passés séparément et échappés automatiquement par SQLite, ce qui empêche les injections SQL.

**Q20 : Comment avez-vous optimisé les requêtes pour le tableau de bord ?**
R : J'ai utilisé une requête d'agrégation avec une sous-requête qui calcule le solde de chaque élève en une seule passe, puis une requête externe qui agrège ces résultats. Au lieu de faire N+1 requêtes (une par élève), je n'en fais que 2, ce qui est beaucoup plus performant.

---

## Points forts à mettre en avant

1. **Architecture propre** : Séparation claire des responsabilités, code maintenable
2. **Gestion des erreurs** : L'application ne plante jamais, gestionnaire global d'exceptions
3. **Fiabilité** : Transactions atomiques, numérotation unique des reçus, immutabilité des paiements
4. **Simplicité pour l'utilisateur** : Interface intuitive, calculs automatiques, génération automatique de reçus
5. **Packaging** : Exécutable autonome, pas besoin d'installer Python
6. **Tests** : Tests unitaires pour les services, validation du jeu de test

---

## Points faibles à anticiper

1. **Mono-utilisateur** : Pas de gestion multi-utilisateur, pas de droits d'accès
2. **Pas de sauvegarde automatique** : L'utilisateur doit sauvegarder manuellement
3. **Polices PDF limitées** : Supporte uniquement le latin-1, pas de caractères spéciaux
4. **Pas d'export/import** : Difficile de migrer les données vers un autre système
5. **Pas de statistiques avancées** : Indicateurs simples, pas de graphiques

---

## Améliorations possibles

1. Ajouter une sauvegarde automatique des données
2. Implémenter l'export/import des données (CSV, Excel)
3. Ajouter des graphiques dans le tableau de bord
4. Support de l'UTF-8 dans les PDF (police TTF embarquée)
5. Gestion multi-établissement
6. Module de gestion des absences
7. Gestion des droits d'accès multi-utilisateur
8. Serveur web pour consultation en ligne
