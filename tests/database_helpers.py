"""Helpers for tests that require temporary encrypted SQLite databases."""

import os
import shutil
import tempfile

from database.encryption import ensure_encrypted_database, load_or_create_key
from sqlcipher3 import dbapi2 as sqlcipher
from unittest import mock


def create_encrypted_test_database(source_path, database_path):
    key_path = database_path + ".dpapi"
    ensure_encrypted_database(database_path, key_path, source_path)
    return key_path


def make_encrypted_test_fixture(source_path):
    """Create an isolated encrypted fixture from the repository demo database."""
    temporary_directory = tempfile.mkdtemp(prefix="edupaie-encrypted-test-")
    plain_path = os.path.join(temporary_directory, "seed.db")
    database_path = os.path.join(temporary_directory, "data", "edupaie.db")
    shutil.copy2(source_path, plain_path)
    key_path = create_encrypted_test_database(plain_path, database_path)
    os.remove(plain_path)
    return temporary_directory, database_path, key_path


def connect_encrypted_test_database(database_path, key_path):
    key = load_or_create_key(key_path, create_if_missing=False)
    connection = sqlcipher.connect(database_path)
    connection.execute(f'PRAGMA key = "x\'{key.hex()}\'"')
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlcipher.Row
    return connection


def database_connection_patches(database_path, key_path):
    """Redirect application connections to a disposable encrypted test DB."""
    from database import connection as database_connection

    return [
        mock.patch.object(database_connection, "get_database_path", lambda: database_path),
        mock.patch.object(database_connection, "get_database_key_path", lambda: key_path),
        mock.patch.object(database_connection, "ensure_data_dirs", lambda: None),
        mock.patch.object(database_connection, "copy_initial_database_if_needed", lambda: None),
    ]