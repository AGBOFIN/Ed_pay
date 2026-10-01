-- Schema de la base de données EduPaie
-- Active les clés étrangères
PRAGMA foreign_keys = ON;

-- Table pour la séquence de numérotation des reçus
-- Permet de générer des numéros uniques de format REC-YYYY-XXXXX
CREATE TABLE IF NOT EXISTS sequence_recus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    derniere_valeur INTEGER NOT NULL DEFAULT 0
);

-- Initialisation de la séquence
INSERT INTO sequence_recus (derniere_valeur) VALUES (0);

-- Table des élèves
CREATE TABLE IF NOT EXISTS eleve (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    classe TEXT NOT NULL,
    annee_scolaire TEXT NOT NULL,
    total_du INTEGER NOT NULL CHECK (total_du >= 0),
    date_creation TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Table des paiements
CREATE TABLE IF NOT EXISTS paiement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id INTEGER NOT NULL,
    montant INTEGER NOT NULL CHECK (montant > 0),
    date TEXT NOT NULL DEFAULT (datetime('now')),
    mode TEXT NOT NULL CHECK (mode IN ('espèces', 'chèque', 'virement', 'mobile money')),
    numero_recu TEXT NOT NULL UNIQUE,
    solde_apres INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (eleve_id) REFERENCES eleve(id) ON DELETE RESTRICT
);

-- Index pour optimiser les recherches
CREATE INDEX IF NOT EXISTS idx_paiement_eleve_id ON paiement(eleve_id);
CREATE INDEX IF NOT EXISTS idx_paiement_date ON paiement(date);
CREATE INDEX IF NOT EXISTS idx_eleve_classe ON eleve(classe);

-- Trigger pour empêcher les paiements qui dépassent le solde
CREATE TRIGGER IF NOT EXISTS verifier_solde_paiement
BEFORE INSERT ON paiement
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Le paiement dépasse le solde restant')
    WHERE NEW.montant > (
        SELECT total_du - COALESCE(SUM(montant), 0)
        FROM eleve
        LEFT JOIN paiement ON eleve.id = paiement.eleve_id
        WHERE eleve.id = NEW.eleve_id
    );
END;
