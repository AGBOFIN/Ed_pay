"""
Script de création et peuplement de la base de données EduPaie.
Ce script lit le schema.sql et insère des données de test.
"""

import sqlite3
import os
from datetime import datetime, timedelta


def get_db_path():
    """Retourne le chemin vers la base de données."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'data', 'edupaie.db')


def get_schema_path():
    """Retourne le chemin vers le fichier schema.sql."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'schema.sql')


def generate_numero_recu(cursor, annee):
    """
    Génère un numéro de reçu unique au format REC-YYYY-XXXXX.
    Utilise une séquence pour garantir l'unicité.
    Doit être appelé dans une transaction pour garantir l'atomicité.
    """
    # Récupère la dernière valeur de la séquence
    cursor.execute("SELECT derniere_valeur FROM sequence_recus WHERE id = 1")
    result = cursor.fetchone()
    derniere_valeur = result[0] if result else 0
    
    # Incrémente la valeur
    nouvelle_valeur = derniere_valeur + 1
    
    # Met à jour la séquence
    cursor.execute("UPDATE sequence_recus SET derniere_valeur = ? WHERE id = 1", (nouvelle_valeur,))
    
    # Formate le numéro de reçu avec padding de zéros
    return f"REC-{annee}-{nouvelle_valeur:05d}"


def creer_base_de_donnees():
    """Crée la base de données en exécutant le schema.sql."""
    db_path = get_db_path()
    schema_path = get_schema_path()
    
    # Crée le répertoire data s'il n'existe pas
    data_dir = os.path.dirname(db_path)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Supprime la base existante si elle existe
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Crée la base avec isolation_level=None pour contrôler manuellement les transactions
    conn = sqlite3.connect(db_path, isolation_level=None)
    cursor = conn.cursor()
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    print(f"Base de données créée : {db_path}")
    return conn


def peupler_donnees(conn):
    """Insère des données de test dans la base."""
    cursor = conn.cursor()
    
    # Insère les classes avec des frais par défaut réalistes
    classes = [
        ("6ème A", 150000),
        ("6ème B", 120000),
        ("5ème A", 180000),
        ("5ème B", 170000),
        ("4ème A", 200000),
        ("4ème B", 190000),
        ("3ème A", 250000),
        ("3ème B", 230000),
    ]
    
    for nom, frais in classes:
        cursor.execute(
            "INSERT INTO classe (nom, frais_defaut) VALUES (?, ?)",
            (nom, frais)
        )
    
    print(f"{len(classes)} classes insérées")
    
    # Insère les paramètres par défaut
    parametres = [
        ("etablissement_nom", "École Exemple"),
        ("etablissement_adresse", "123 Rue de l'École"),
        ("etablissement_telephone", "01 23 45 67 89"),
        ("etablissement_email", "contact@ecole-exemple.fr"),
        ("etablissement_devise", "FCFA"),
        ("etablissement_logo", ""),
        ("etablissement_pied_page", "Merci pour votre confiance !"),
        ("annee_scolaire", "2025-2026"),
        ("recu_prefixe", "REC"),
        ("paiement_modes", "espèces,chèque,virement,mobile money"),
    ]
    
    for cle, valeur in parametres:
        cursor.execute(
            "INSERT INTO parametre (cle, valeur) VALUES (?, ?)",
            (cle, valeur)
        )
    
    print(f"{len(parametres)} paramètres insérés")
    
    # Liste des élèves avec différentes classes et années
    # Montants en francs CFA (50 000 à 350 000 FCFA)
    eleves = [
        ("Dupont", "Jean", "6ème A", "2025-2026", 150000),
        ("Martin", "Marie", "6ème A", "2025-2026", 150000),
        ("Bernard", "Pierre", "6ème B", "2025-2026", 120000),
        ("Dubois", "Sophie", "6ème B", "2025-2026", 120000),
        ("Thomas", "Lucas", "5ème A", "2025-2026", 180000),
        ("Robert", "Emma", "5ème A", "2025-2026", 180000),
        ("Richard", "Louis", "5ème B", "2025-2026", 170000),
        ("Petit", "Chloé", "5ème B", "2025-2026", 170000),
        ("Leroy", "Hugo", "4ème A", "2025-2026", 200000),
        ("Moreau", "Léa", "4ème A", "2025-2026", 200000),
        ("Simon", "Gabriel", "4ème B", "2025-2026", 190000),
        ("Laurent", "Jade", "4ème B", "2025-2026", 190000),
        ("Lefebvre", "Enzo", "3ème A", "2025-2026", 250000),
        ("Garcia", "Manon", "3ème A", "2025-2026", 250000),
        ("David", "Paul", "3ème B", "2025-2026", 230000),
        ("Bertrand", "Camille", "3ème B", "2025-2026", 230000),
        ("Roux", "Antoine", "6ème A", "2025-2026", 150000),
        ("Fournier", "Sarah", "6ème B", "2025-2026", 120000),
        ("Meyer", "Kevin", "5ème A", "2025-2026", 180000),
        ("Gauthier", "Julie", "5ème B", "2025-2026", 170000),
    ]
    
    # Insère les élèves
    eleve_ids = []
    for nom, prenom, classe, annee, total in eleves:
        cursor.execute(
            "INSERT INTO eleve (nom, prenom, classe, annee_scolaire, total_du) VALUES (?, ?, ?, ?, ?)",
            (nom, prenom, classe, annee, total)
        )
        eleve_ids.append(cursor.lastrowid)
    
    print(f"{len(eleve_ids)} élèves insérés")
    
    # Génère des paiements variés pour tester différents scénarios
    # Montants en francs CFA (10 000 à 100 000 FCFA)
    annee_actuelle = "2026"
    base_date = datetime(2025, 9, 1)  # Début de l'année scolaire
    
    paiements = []
    
    # Élèves soldés (paiement complet en une fois)
    paiements.append((eleve_ids[0], 150000, base_date, "espèces"))  # Dupont Jean
    paiements.append((eleve_ids[1], 150000, base_date + timedelta(days=5), "chèque"))  # Martin Marie
    paiements.append((eleve_ids[4], 180000, base_date + timedelta(days=10), "virement"))  # Thomas Lucas
    paiements.append((eleve_ids[16], 150000, base_date + timedelta(days=15), "mobile money"))  # Roux Antoine
    
    # Élèves partiellement payés (2 versements)
    paiements.append((eleve_ids[2], 50000, base_date + timedelta(days=2), "espèces"))  # Bernard Pierre (reste 70 000)
    paiements.append((eleve_ids[2], 70000, base_date + timedelta(days=45), "virement"))  # Bernard Pierre (soldé)
    
    paiements.append((eleve_ids[3], 40000, base_date + timedelta(days=7), "mobile money"))  # Dubois Sophie (reste 80 000)
    paiements.append((eleve_ids[3], 80000, base_date + timedelta(days=50), "chèque"))  # Dubois Sophie (soldé)
    
    # Élèves partiellement payés (3 versements)
    paiements.append((eleve_ids[5], 60000, base_date + timedelta(days=12), "chèque"))  # Robert Emma (reste 120 000)
    paiements.append((eleve_ids[5], 60000, base_date + timedelta(days=60), "espèces"))  # Robert Emma (reste 60 000)
    paiements.append((eleve_ids[5], 60000, base_date + timedelta(days=90), "virement"))  # Robert Emma (soldé)
    
    paiements.append((eleve_ids[6], 50000, base_date + timedelta(days=15), "virement"))  # Richard Louis (reste 120 000)
    paiements.append((eleve_ids[6], 60000, base_date + timedelta(days=65), "mobile money"))  # Richard Louis (reste 60 000)
    paiements.append((eleve_ids[6], 60000, base_date + timedelta(days=95), "espèces"))  # Richard Louis (soldé)
    
    # Élèves partiellement payés (4 versements)
    paiements.append((eleve_ids[12], 60000, base_date + timedelta(days=1), "espèces"))  # Lefebvre Enzo (reste 190 000)
    paiements.append((eleve_ids[12], 63000, base_date + timedelta(days=30), "virement"))  # Lefebvre Enzo (reste 127 000)
    paiements.append((eleve_ids[12], 64000, base_date + timedelta(days=60), "chèque"))  # Lefebvre Enzo (reste 63 000)
    paiements.append((eleve_ids[12], 63000, base_date + timedelta(days=90), "mobile money"))  # Lefebvre Enzo (soldé)
    
    # Élèves partiellement payés (non soldés)
    paiements.append((eleve_ids[7], 85000, base_date + timedelta(days=20), "espèces"))  # Petit Chloé (reste 85 000)
    paiements.append((eleve_ids[7], 85000, base_date + timedelta(days=70), "virement"))  # Petit Chloé (soldé)
    
    paiements.append((eleve_ids[8], 100000, base_date + timedelta(days=25), "chèque"))  # Leroy Hugo (reste 100 000)
    
    paiements.append((eleve_ids[9], 50000, base_date + timedelta(days=30), "mobile money"))  # Moreau Léa (reste 150 000)
    paiements.append((eleve_ids[9], 50000, base_date + timedelta(days=75), "espèces"))  # Moreau Léa (reste 100 000)
    
    # Élèves non payés (aucun paiement)
    # eleve_ids[10] (Simon Gabriel), eleve_ids[11] (Laurent Jade), eleve_ids[13] (Garcia Manon)
    # eleve_ids[14] (David Paul), eleve_ids[15] (Bertrand Camille), eleve_ids[17] (Fournier Sarah)
    # eleve_ids[18] (Meyer Kevin), eleve_ids[19] (Gauthier Julie)
    
    # Paiements avec les 4 modes de paiement étalés sur l'année
    paiements.append((eleve_ids[14], 115000, base_date + timedelta(days=40), "espèces"))  # David Paul (reste 115 000)
    paiements.append((eleve_ids[14], 115000, base_date + timedelta(days=80), "chèque"))  # David Paul (soldé)
    
    paiements.append((eleve_ids[15], 115000, base_date + timedelta(days=45), "virement"))  # Bertrand Camille (reste 115 000)
    
    paiements.append((eleve_ids[17], 85000, base_date + timedelta(days=50), "mobile money"))  # Fournier Sarah (reste 35 000)
    paiements.append((eleve_ids[17], 35000, base_date + timedelta(days=85), "espèces"))  # Fournier Sarah (soldé)
    
    paiements.append((eleve_ids[18], 90000, base_date + timedelta(days=55), "chèque"))  # Meyer Kevin (reste 90 000)
    
    paiements.append((eleve_ids[19], 85000, base_date + timedelta(days=60), "virement"))  # Gauthier Julie (reste 85 000)
    paiements.append((eleve_ids[19], 85000, base_date + timedelta(days=100), "mobile money"))  # Gauthier Julie (soldé)
    
    # Paiements supplémentaires pour atteindre 35+
    paiements.append((eleve_ids[10], 95000, base_date + timedelta(days=35), "espèces"))  # Simon Gabriel (reste 95 000)
    paiements.append((eleve_ids[10], 95000, base_date + timedelta(days=70), "chèque"))  # Simon Gabriel (soldé)
    
    paiements.append((eleve_ids[11], 60000, base_date + timedelta(days=40), "virement"))  # Laurent Jade (reste 130 000)
    paiements.append((eleve_ids[11], 65000, base_date + timedelta(days=75), "mobile money"))  # Laurent Jade (reste 65 000)
    paiements.append((eleve_ids[11], 65000, base_date + timedelta(days=110), "espèces"))  # Laurent Jade (soldé)
    
    # Insère les paiements avec numéros de reçus uniques dans une transaction
    # La transaction garantit l'atomicité entre la génération du numéro et l'insertion
    # Calcule solde_apres pour chaque paiement (instantané du solde après ce paiement)
    try:
        # Début explicite de la transaction
        conn.execute("BEGIN")
        
        # Dictionnaire pour suivre le total payé par élève (en francs CFA)
        total_paye_par_eleve = {eleve_id: 0 for eleve_id in eleve_ids}
        
        # Récupère le total_du de chaque élève
        total_du_par_eleve = {}
        for eleve_id in eleve_ids:
            cursor.execute("SELECT total_du FROM eleve WHERE id = ?", (eleve_id,))
            row = cursor.fetchone()
            total_du_par_eleve[eleve_id] = int(row[0])  # Déjà en francs CFA
        
        for eleve_id, montant, date_paiement, mode in paiements:
            numero_recu = generate_numero_recu(cursor, annee_actuelle)
            date_str = date_paiement.strftime("%Y-%m-%d %H:%M:%S")
            montant_fcfa = int(montant)  # Déjà en francs CFA
            
            # Met à jour le total payé pour cet élève
            total_paye_par_eleve[eleve_id] += montant_fcfa
            
            # Calcule le solde après ce paiement
            solde_apres = total_du_par_eleve[eleve_id] - total_paye_par_eleve[eleve_id]
            
            cursor.execute(
                "INSERT INTO paiement (eleve_id, montant, date, mode, numero_recu, solde_apres) VALUES (?, ?, ?, ?, ?, ?)",
                (eleve_id, montant_fcfa, date_str, mode, numero_recu, solde_apres)
            )
        
        # Commit de la transaction
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    
    print(f"{len(paiements)} paiements insérés")


def main():
    """Fonction principale."""
    print("Création de la base de données EduPaie...")
    conn = creer_base_de_donnees()
    peupler_donnees(conn)
    conn.close()
    print("Base de données créée et peuplée avec succès !")


if __name__ == "__main__":
    main()
