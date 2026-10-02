"""Tests for SQLCipher initialization and Windows DPAPI key protection."""

import os
import shutil
import sqlite3
import tempfile
import unittest

from database.encryption import (
    DatabaseEncryptionError,
    ensure_encrypted_database,
    load_or_create_key,
    unprotect_key,
    verify_encrypted_database,
)
from sqlcipher3 import dbapi2 as sqlcipher


@unittest.skipUnless(os.name == "nt", "La protection DPAPI est spécifique à Windows")
class TestDatabaseEncryption(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="edupaie-sqlcipher-test-")
        self.seed_path = os.path.join(self.temp_dir, "seed.db")
        self.database_path = os.path.join(self.temp_dir, "profile", "data", "edupaie.db")
        self.key_path = os.path.join(self.temp_dir, "profile", "keys", "database.dpapi")
        self.legacy_path = os.path.join(self.temp_dir, "legacy", "data", "edupaie.db")
        os.makedirs(os.path.dirname(self.legacy_path))
        self._create_plain_database(self.seed_path, "seed-record")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @staticmethod
    def _create_plain_database(path, value):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE sample (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sample VALUES (?)", (value,))
        connection.commit()
        connection.close()

    def _read_encrypted_value(self, path):
        key = load_or_create_key(self.key_path, create_if_missing=False)
        verify_encrypted_database(path, key)
        connection = sqlcipher.connect(path)
        try:
            connection.execute(f'PRAGMA key = "x\'{key.hex()}\'"')
            return connection.execute("SELECT value FROM sample").fetchone()[0]
        finally:
            connection.close()

    def test_dpapi_key_roundtrip(self):
        key = load_or_create_key(self.key_path, create_if_missing=True)

        self.assertEqual(len(key), 32)
        with open(self.key_path, "rb") as key_file:
            self.assertEqual(unprotect_key(key_file.read()), key)

    def test_initial_seed_is_copied_as_encrypted_database(self):
        ensure_encrypted_database(
            self.database_path,
            self.key_path,
            self.seed_path,
        )

        self.assertEqual(self._read_encrypted_value(self.database_path), "seed-record")
        with self.assertRaises(sqlite3.DatabaseError):
            with sqlite3.connect(self.database_path) as plaintext_connection:
                plaintext_connection.execute("SELECT * FROM sample").fetchall()

    def test_legacy_database_is_migrated_backed_up_then_removed(self):
        self._create_plain_database(self.legacy_path, "legacy-record")

        ensure_encrypted_database(
            self.database_path,
            self.key_path,
            self.seed_path,
            legacy_database_path=self.legacy_path,
            remove_legacy=True,
        )

        self.assertEqual(self._read_encrypted_value(self.database_path), "legacy-record")
        self.assertFalse(os.path.exists(self.legacy_path))
        self.assertEqual(
            self._read_encrypted_value(self.database_path + ".pre-sqlcipher"),
            "legacy-record",
        )

    def test_missing_key_does_not_modify_encrypted_database(self):
        ensure_encrypted_database(self.database_path, self.key_path, self.seed_path)
        with open(self.database_path, "rb") as database_file:
            original_bytes = database_file.read()
        os.remove(self.key_path)

        with self.assertRaises(DatabaseEncryptionError):
            ensure_encrypted_database(self.database_path, self.key_path, self.seed_path)

        with open(self.database_path, "rb") as database_file:
            self.assertEqual(database_file.read(), original_bytes)

    def test_ambiguous_encrypted_and_legacy_bases_are_preserved(self):
        ensure_encrypted_database(self.database_path, self.key_path, self.seed_path)
        self._create_plain_database(self.legacy_path, "legacy-record")
        with open(self.legacy_path, "rb") as legacy_file:
            original_legacy_bytes = legacy_file.read()

        with self.assertRaises(DatabaseEncryptionError):
            ensure_encrypted_database(
                self.database_path,
                self.key_path,
                self.seed_path,
                legacy_database_path=self.legacy_path,
                remove_legacy=True,
            )

        with open(self.legacy_path, "rb") as legacy_file:
            self.assertEqual(legacy_file.read(), original_legacy_bytes)
        self.assertFalse(os.path.exists(self.database_path + ".pre-sqlcipher"))


if __name__ == "__main__":
    unittest.main()