"""
Tests d'interface pour la navigation et le reçu PDF (QT_QPA_PLATFORM=offscreen).

Reproduit trois bugs constatés sur le terrain :
  (a) les boutons ou l'action de menu « Élèves » ne font rien (écran bloqué) ;
  (b) RuntimeError: libshiboken: Internal C++ object (DashboardWidget) already
      deleted au retour sur le tableau de bord (voir edupaie_error.log) ;
  (c) le reçu PDF ne se génère pas (aucun paiement n'aboutit via l'interface,
      et solde_apres est corrompu par une conversion centimes/FCFA).

Ces tests utilisent une COPIE temporaire de data/edupaie.db : la vraie base
n'est jamais modifiée (vérifiée par empreinte SHA-256 avant/après).
"""

import unittest
import os
import sys
import shutil
import sqlite3
import tempfile
import hashlib
import datetime
from unittest import mock

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import QApplication, QStackedWidget, QDialog, QMessageBox
from PySide6.QtCore import Qt, QEvent, QCoreApplication
from PySide6.QtTest import QTest
from PySide6.QtGui import QDesktopServices
import shiboken6

from ui.main_window import MainWindow
from ui.paiement_dialog import PaiementDialog
from ui.eleve_form_dialog import EleveFormDialog
from ui.fiche_eleve_dialog import FicheEleveDialog
import database.connection as db_connection
import services.recu_pdf as recu_pdf
import utils.resource_utils as resource_utils


RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_REELLE = os.path.join(RACINE_PROJET, 'data', 'edupaie.db')


class TestNavigationEtRecuPDF(unittest.TestCase):
    """Tests de navigation élèves <-> tableau de bord et de génération de reçu."""

    @classmethod
    def setUpClass(cls):
        """Prépare QApplication, une copie temporaire de la base et les espions."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

        # Empreinte de la vraie base avant les tests
        cls.hash_db_avant = cls._sha256(DB_REELLE)
        cls.recus_reels_avant = sorted(os.listdir(os.path.join(RACINE_PROJET, 'data', 'recus')))

        # Copie temporaire de la base (jamais data/edupaie.db)
        cls.tmp = tempfile.mkdtemp(prefix='edupaie_tests_')
        cls.db_tmp = os.path.join(cls.tmp, 'data', 'edupaie.db')
        os.makedirs(os.path.dirname(cls.db_tmp))
        shutil.copy2(DB_REELLE, cls.db_tmp)
        cls.recus_tmp = os.path.join(cls.tmp, 'recus')
        os.makedirs(cls.recus_tmp)

        # Redirige toute l'application vers la copie temporaire
        cls._patches = [
            mock.patch.object(db_connection, 'get_database_path', lambda: cls.db_tmp),
            mock.patch.object(db_connection, 'ensure_data_dirs', lambda: None),
            mock.patch.object(db_connection, 'copy_initial_database_if_needed', lambda: None),
            mock.patch.object(recu_pdf, 'get_recus_dir', lambda: cls.recus_tmp),
            mock.patch.object(recu_pdf, 'ensure_data_dirs', lambda: None),
            mock.patch.object(resource_utils, 'get_app_dir', lambda: cls.tmp),
        ]
        for p in cls._patches:
            p.start()

        # Capture les exceptions levées dans les slots Qt (elles vont à
        # sys.excepthook, c'est ainsi que le RuntimeError a fini dans le log)
        cls._ancien_hook = sys.excepthook
        cls.exceptions_slots = []
        sys.excepthook = cls._capturer_exception

    @classmethod
    def tearDownClass(cls):
        sys.excepthook = cls._ancien_hook
        for p in cls._patches:
            p.stop()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def _capturer_exception(cls, type_exc, valeur, traceback):
        cls.exceptions_slots.append(f"{type_exc.__name__}: {valeur}")

    @staticmethod
    def _sha256(chemin):
        with open(chemin, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def setUp(self):
        """Fenêtre principale neuve pour chaque test + état des espions vide."""
        self.exceptions_slots.clear()
        self.dialogs_ouverts = []
        self.erreurs_navigation = []
        self.main_window = MainWindow()
        self.main_window.show()
        self._purger_evenements()

    def tearDown(self):
        self.main_window.close()
        self._purger_evenements()

    def _purger_evenements(self):
        """Simule un tour de boucle d'événements complet (deleteLater compris)."""
        self.app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()

    def _action_menu(self, libelle):
        """Retrouve une QAction de la barre de menu par son libellé."""
        for menu in self.main_window.menuBar().actions():
            for action in menu.menu().actions():
                if action.text().replace('&', '') == libelle:
                    return action
        self.fail(f"Action de menu introuvable : {libelle}")

    def _naviguer(self, libelle):
        """Déclenche une action de menu réelle et purge les événements."""
        try:
            self._action_menu(libelle).trigger()
            self._purger_evenements()
        except Exception as e:
            self.erreurs_navigation.append(f"{libelle} -> {type(e).__name__}: {e}")

    def _naviguer_trois_allers_retours(self):
        """Scénario utilisateur : élèves -> tableau de bord -> élèves, trois fois."""
        for _ in range(3):
            self._naviguer("Gérer les élèves")
            self._naviguer("Afficher le tableau de bord")
            self._naviguer("Gérer les élèves")

    def _selectionner_premiere_ligne(self):
        """Sélectionne la première ligne de la table des élèves."""
        widget = self.main_window.eleves_widget
        widget.table.selectRow(0)
        self._purger_evenements()
        return widget

    def _selectionner_eleve_avec_solde(self, montant_minimum):
        """Sélectionne le premier élève dont le solde dépasse montant_minimum."""
        widget = self.main_window.eleves_widget
        for ligne, eleve in enumerate(widget.model.eleves):
            if eleve['total_du'] - eleve.get('total_paye', 0) > montant_minimum:
                widget.table.selectRow(ligne)
                self._purger_evenements()
                return eleve
        self.fail("Aucun élève avec un solde suffisant dans la base de test")

    # ------------------------------------------------------------------
    # (a) + (b) : navigation
    # ------------------------------------------------------------------

    def test_a_b_navigation_trois_allers_retours_sans_erreur(self):
        """(a)+(b) Trois allers-retours élèves <-> tableau de bord sans erreur.

        Avant correction : le premier retour au tableau de bord lève
        « RuntimeError: libshiboken: Internal C++ object (DashboardWidget)
        already deleted » car setCentralWidget() a détruit le widget.
        """
        central = self.main_window.centralWidget()
        self.assertIsInstance(
            central, QStackedWidget,
            "Le widget central doit être UN QStackedWidget défini une seule fois")

        for numero in range(1, 4):
            self._naviguer("Gérer les élèves")
            self.assertEqual(
                self.erreurs_navigation, [],
                f"Passage n°{numero} aux élèves : la navigation ne doit lever aucune erreur")
            self.assertIs(
                central.currentWidget(), self.main_window.eleves_widget,
                f"Passage n°{numero} : l'écran Élèves doit être affiché")

            self._naviguer("Afficher le tableau de bord")
            self.assertEqual(
                self.erreurs_navigation, [],
                f"Retour n°{numero} au tableau de bord : la navigation ne doit lever aucune erreur")
            self.assertIs(
                central.currentWidget(), self.main_window.dashboard_widget,
                f"Retour n°{numero} : le tableau de bord doit être affiché")

            self._naviguer("Gérer les élèves")
            self.assertIs(
                central.currentWidget(), self.main_window.eleves_widget,
                f"Retour n°{numero} aux élèves : l'écran Élèves doit être réaffiché")

            # Aucun écran ne doit avoir été détruit par la navigation
            self.assertTrue(
                shiboken6.isValid(self.main_window.dashboard_widget),
                "Le tableau de bord ne doit jamais être détruit par la navigation")
            self.assertTrue(
                shiboken6.isValid(self.main_window.eleves_widget),
                "L'écran Élèves ne doit jamais être détruit par la navigation")

        self.assertEqual(self.exceptions_slots, [],
                         "Aucune exception ne doit atteindre le gestionnaire global")

    def test_a_boutons_clitables_apres_navigation(self):
        """(a) Après trois allers-retours, les boutons ouvrent bien leurs dialogues.

        Avant correction : la navigation échoue d'abord (RuntimeError), l'écran
        reste bloqué et le parcours des boutons est inatteignable.
        """
        self._naviguer_trois_allers_retours()
        self.assertEqual(
            self.erreurs_navigation, [],
            "La navigation doit réussir avant de pouvoir cliquer sur les boutons")

        widget = self.main_window.eleves_widget
        self.assertIsNotNone(widget, "L'écran Élèves doit être accessible")

        def espion_exec(nom, resultat=QDialog.Rejected):
            def _exec(self_dialog):
                self.dialogs_ouverts.append(nom)
                return resultat
            return _exec

        with mock.patch.object(EleveFormDialog, 'exec', espion_exec('EleveFormDialog')), \
             mock.patch.object(PaiementDialog, 'exec', espion_exec('PaiementDialog')), \
             mock.patch.object(FicheEleveDialog, 'exec', espion_exec('FicheEleveDialog')), \
             mock.patch('ui.eleves_widget.QMessageBox.question',
                        lambda *a, **k: QMessageBox.StandardButton.No):
            # Ajouter (aucune sélection nécessaire)
            QTest.mouseClick(widget.ajouter_btn, Qt.LeftButton)
            self._purger_evenements()

            # Modifier, Supprimer, Enregistrer paiement, Fiche élève (avec sélection)
            self._selectionner_premiere_ligne()
            QTest.mouseClick(widget.modifier_btn, Qt.LeftButton)
            self._purger_evenements()
            QTest.mouseClick(widget.supprimer_btn, Qt.LeftButton)
            self._purger_evenements()
            QTest.mouseClick(widget.paiement_btn, Qt.LeftButton)
            self._purger_evenements()
            QTest.mouseClick(widget.fiche_btn, Qt.LeftButton)
            self._purger_evenements()

        self.assertEqual(
            self.dialogs_ouverts,
            ['EleveFormDialog', 'EleveFormDialog', 'PaiementDialog', 'FicheEleveDialog'],
            "Chaque bouton doit réellement ouvrir son dialogue")
        self.assertEqual(self.exceptions_slots, [],
                         "Aucune exception ne doit être levée par les clics")

        # « Supprimer » suivie de Non ne doit rien supprimer
        with sqlite3.connect(self.db_tmp) as conn:
            nb_eleves = conn.execute("SELECT COUNT(*) FROM eleve").fetchone()[0]
        self.assertEqual(nb_eleves, 20, "Répondre Non à la confirmation ne doit rien supprimer")

    # ------------------------------------------------------------------
    # (c) : paiement valide + reçu PDF
    # ------------------------------------------------------------------

    def test_c_paiement_valide_genere_recu_pdf(self):
        """(c) Un paiement valide crée un PDF non vide avec le bon numéro de reçu.

        Avant correction : solde_apres est corrompu (multiplication par 100 dans
        PaiementRepository) et le rafraîchissement du tableau de bord lève
        RuntimeError après l'enregistrement.
        """
        # Ouvre l'écran Élèves (le widget n'existe pas avant la première navigation)
        self.main_window.afficher_gestion_eleves()
        self._purger_evenements()
        widget = self.main_window.eleves_widget
        eleve = self._selectionner_eleve_avec_solde(10000)
        eleve_id = eleve['id']

        # État attendu avant le paiement
        with sqlite3.connect(self.db_tmp) as conn:
            conn.row_factory = sqlite3.Row
            eleve = conn.execute(
                "SELECT total_du,"
                " (SELECT COALESCE(SUM(montant), 0) FROM paiement WHERE eleve_id = ?) AS paye"
                " FROM eleve WHERE id = ?", (eleve_id, eleve_id)).fetchone()
            sequence = conn.execute(
                "SELECT derniere_valeur FROM sequence_recus WHERE id = 1").fetchone()[0]
        solde_reel = eleve['total_du'] - eleve['paye']
        self.assertGreater(solde_reel, 10000, "L'élève de test doit avoir un solde suffisant")
        numero_attendu = f"REC-{datetime.date.today().year}-{sequence + 1:05d}"

        def exec_paiement(self_dialog):
            self.dialogs_ouverts.append('PaiementDialog')
            self_dialog.montant_spin.setValue(10000)
            self_dialog.accept()
            return QDialog.Accepted

        messages = []
        with mock.patch.object(PaiementDialog, 'exec', exec_paiement), \
             mock.patch('ui.eleves_widget.QMessageBox.information',
                        lambda *a, **k: messages.append(a[2])), \
             mock.patch('ui.eleves_widget.QMessageBox.question',
                        lambda *a, **k: QMessageBox.StandardButton.Yes), \
             mock.patch.object(QDesktopServices, 'openUrl', lambda *a, **k: True):
            QTest.mouseClick(widget.paiement_btn, Qt.LeftButton)
            self._purger_evenements()

        self.assertEqual(self.exceptions_slots, [],
                         "Aucune exception ne doit être levée pendant l'enregistrement du paiement")
        self.assertIn('PaiementDialog', self.dialogs_ouverts)

        # Le paiement est en base avec le bon solde en FCFA
        with sqlite3.connect(self.db_tmp) as conn:
            conn.row_factory = sqlite3.Row
            paiement = conn.execute(
                "SELECT numero_recu, montant, solde_apres FROM paiement"
                " WHERE eleve_id = ? ORDER BY id DESC LIMIT 1", (eleve_id,)).fetchone()
        self.assertIsNotNone(paiement, "Le paiement doit être enregistré en base")
        self.assertEqual(paiement['numero_recu'], numero_attendu,
                         "Le numéro de reçu doit suivre la séquence")
        self.assertEqual(paiement['montant'], 10000)
        self.assertEqual(paiement['solde_apres'], solde_reel - 10000,
                         "Le solde après paiement doit être en FCFA (pas x100)")

        # Le message de succès affiche le bon numéro de reçu
        self.assertTrue(
            any(numero_attendu in str(m) for m in messages),
            f"Le message de succès doit afficher le numéro {numero_attendu} : {messages}")

        # Le reçu PDF existe, est non vide et porte le bon numéro
        chemin_pdf = os.path.join(self.recus_tmp, f"{numero_attendu}.pdf")
        self.assertTrue(os.path.exists(chemin_pdf), f"Le reçu PDF doit exister : {chemin_pdf}")
        taille = os.path.getsize(chemin_pdf)
        self.assertGreater(taille, 0, "Le reçu PDF ne doit pas être vide")
        with open(chemin_pdf, 'rb') as f:
            self.assertTrue(f.read(5).startswith(b'%PDF'), "Le fichier doit être un vrai PDF")

    # ------------------------------------------------------------------
    # Garantie : la vraie base de données n'est jamais touchée
    # ------------------------------------------------------------------

    def test_z_base_reelle_intacte(self):
        """La vraie base et le dossier des reçus ne doivent jamais être modifiés."""
        self.assertEqual(self._sha256(DB_REELLE), self.hash_db_avant,
                         "data/edupaie.db ne doit jamais être modifiée par les tests")
        recus_reels = sorted(os.listdir(os.path.join(RACINE_PROJET, 'data', 'recus')))
        self.assertEqual(recus_reels, self.recus_reels_avant,
                         "data/recus ne doit jamais être modifié par les tests")


if __name__ == '__main__':
    unittest.main()
