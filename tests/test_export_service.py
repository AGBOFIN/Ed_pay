"""
Tests unitaires pour le service d'export CSV (ExportService).
"""

import unittest
import os
import tempfile
import csv
from services.export_service import ExportService


class TestExportService(unittest.TestCase):
    """Tests pour ExportService."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.fichier_csv = os.path.join(self.temp_dir, "test_export.csv")
        self.eleves_test = [
            {
                "id": 1,
                "nom": "Kouassi",
                "prenom": "Aya",
                "classe": "6ème A",
                "annee_scolaire": "2025-2026",
                "total_du": 150000,
                "total_paye": 100000,
                "solde": 50000,
                "statut": "Partiellement payé"
            },
            {
                "id": 2,
                "nom": "Traoré",
                "prenom": "Moussa",
                "classe": "5ème B",
                "annee_scolaire": "2025-2026",
                "total_du": 180000,
                "total_paye": 180000,
                "solde": 0,
                "statut": "Soldé"
            }
        ]

    def tearDown(self):
        if os.path.exists(self.fichier_csv):
            os.remove(self.fichier_csv)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_exporter_eleves_csv_cree_fichier_valide(self):
        """Vérifie que l'export crée un fichier CSV non vide avec encodage UTF-8 avec BOM."""
        nb_lignes = ExportService.exporter_eleves_csv(self.eleves_test, self.fichier_csv)
        
        self.assertEqual(nb_lignes, 2)
        self.assertTrue(os.path.exists(self.fichier_csv))
        self.assertGreater(os.path.getsize(self.fichier_csv), 0)

        # Vérifie le contenu avec csv.reader
        with open(self.fichier_csv, mode="r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f, delimiter=";"))
            self.assertEqual(len(reader), 3)  # 1 ligne d'en-tête + 2 élèves
            
            # En-tête
            headers = reader[0]
            self.assertIn("Nom", headers)
            self.assertIn("Total dû (FCFA)", headers)
            self.assertIn("Solde (FCFA)", headers)
            self.assertIn("Statut", headers)

            # Ligne 1
            self.assertEqual(reader[1][1], "Kouassi")
            self.assertEqual(reader[1][2], "Aya")
            self.assertEqual(reader[1][8], "Partiellement payé")

            # Ligne 2
            self.assertEqual(reader[2][1], "Traoré")
            self.assertEqual(reader[2][8], "Soldé")


    def test_exporter_eleves_csv_neutralise_les_formules_excel(self):
        self.eleves_test[0]["nom"] = "=HYPERLINK(\"https://example.invalid\")"
        self.eleves_test[0]["prenom"] = "\t@SUM(1+1)"
        self.eleves_test[0]["classe"] = "  +1+1"

        ExportService.exporter_eleves_csv([self.eleves_test[0]], self.fichier_csv)

        with open(self.fichier_csv, mode="r", encoding="utf-8-sig") as f:
            row = list(csv.reader(f, delimiter=";"))[1]

        self.assertEqual(row[1], "'=HYPERLINK(\"https://example.invalid\")")
        self.assertEqual(row[2], "'\t@SUM(1+1)")
        self.assertEqual(row[3], "'  +1+1")


if __name__ == "__main__":
    unittest.main()
