"""Helpers for SQLCipher database encryption and Windows-protected keys."""

import ctypes
import os
import shutil
import sqlite3 as plaintext_sqlite
import tempfile
from ctypes import wintypes

from sqlcipher3 import dbapi2 as sqlcipher


class DatabaseEncryptionError(RuntimeError):
    """Raised when a database cannot be safely encrypted or opened."""


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


def _make_blob(value):
    buffer = ctypes.create_string_buffer(value)
    blob = _DataBlob(
        len(value),
        ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)),
    )
    return blob, buffer


def _free_windows_buffer(kernel32, pointer):
    if pointer:
        kernel32.LocalFree(ctypes.cast(pointer, ctypes.c_void_p))


def protect_key(key):
    """Protect a database key so only the current Windows user can recover it."""
    if os.name != "nt":
        raise DatabaseEncryptionError("La protection de clé DPAPI exige Windows.")

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(_DataBlob), wintypes.LPCWSTR,
        ctypes.POINTER(_DataBlob), ctypes.c_void_p, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(_DataBlob),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p

    source, source_buffer = _make_blob(key)
    result = _DataBlob()
    if not crypt32.CryptProtectData(
        ctypes.byref(source), "EduPaie SQLCipher key", None, None, None, 0,
        ctypes.byref(result),
    ):
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        return ctypes.string_at(result.pbData, result.cbData)
    finally:
        _free_windows_buffer(kernel32, result.pbData)
        del source_buffer


def unprotect_key(protected_key):
    """Recover a key protected for the current Windows user with DPAPI."""
    if os.name != "nt":
        raise DatabaseEncryptionError("La protection de clé DPAPI exige Windows.")

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(_DataBlob), ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(_DataBlob), ctypes.c_void_p, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(_DataBlob),
    ]
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p

    source, source_buffer = _make_blob(protected_key)
    result = _DataBlob()
    description = wintypes.LPWSTR()
    if not crypt32.CryptUnprotectData(
        ctypes.byref(source), ctypes.byref(description), None, None, None, 0,
        ctypes.byref(result),
    ):
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        return ctypes.string_at(result.pbData, result.cbData)
    finally:
        _free_windows_buffer(kernel32, result.pbData)
        _free_windows_buffer(kernel32, description)
        del source_buffer


def load_or_create_key(key_path, create_if_missing):
    """Load a DPAPI-protected key, creating one only when explicitly allowed."""
    if os.path.exists(key_path):
        with open(key_path, "rb") as key_file:
            key = unprotect_key(key_file.read())
        if len(key) != 32:
            raise DatabaseEncryptionError("La clé SQLCipher enregistrée est invalide.")
        return key

    if not create_if_missing:
        raise DatabaseEncryptionError(
            "La clé DPAPI de cette base est absente; la base chiffrée n'a pas été modifiée."
        )

    key = os.urandom(32)
    protected_key = protect_key(key)
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    try:
        descriptor = os.open(
            key_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError:
        with open(key_path, "rb") as key_file:
            key = unprotect_key(key_file.read())
        if len(key) != 32:
            raise DatabaseEncryptionError("La clé SQLCipher enregistrée est invalide.")
        return key

    try:
        with os.fdopen(descriptor, "wb") as key_file:
            key_file.write(protected_key)
            key_file.flush()
            os.fsync(key_file.fileno())
    except Exception:
        if os.path.exists(key_path):
            os.remove(key_path)
        raise
    return key


def database_is_plaintext(database_path):
    """Return whether a database file can be read as an ordinary SQLite file."""
    try:
        connection = plaintext_sqlite.connect(database_path)
        try:
            connection.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()
        finally:
            connection.close()
        return True
    except plaintext_sqlite.DatabaseError:
        return False


def verify_encrypted_database(database_path, key):
    """Verify that a database opens and its schema can be read with the key."""
    connection = sqlcipher.connect(database_path)
    try:
        connection.execute(f'PRAGMA key = "x\'{key.hex()}\'"')
        connection.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()
    finally:
        connection.close()


def encrypt_plain_database(source_path, destination_path, key):
    """Export a plaintext database to a verified SQLCipher file atomically."""
    destination_directory = os.path.dirname(destination_path)
    os.makedirs(destination_directory, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix="edupaie-db-", suffix=".tmp", dir=destination_directory
    )
    os.close(descriptor)
    os.remove(temporary_path)

    connection = None
    try:
        connection = sqlcipher.connect(source_path)
        connection.execute(
            f'ATTACH DATABASE ? AS encrypted KEY "x\'{key.hex()}\'"',
            (temporary_path,),
        )
        connection.execute("SELECT sqlcipher_export('encrypted')")
        connection.execute("DETACH DATABASE encrypted")
        connection.close()
        connection = None

        verify_encrypted_database(temporary_path, key)
        if os.path.abspath(source_path) == os.path.abspath(destination_path):
            _create_encrypted_backup(
                temporary_path,
                destination_path + ".pre-sqlcipher",
                key,
            )
        os.replace(temporary_path, destination_path)
    except Exception:
        if connection is not None:
            connection.close()
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise


def _create_encrypted_backup(source_path, backup_path, key):
    """Create and verify a stable encrypted backup without replacing an older one."""
    if os.path.exists(backup_path):
        verify_encrypted_database(backup_path, key)
        return

    backup_directory = os.path.dirname(backup_path)
    os.makedirs(backup_directory, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix="edupaie-backup-", suffix=".tmp", dir=backup_directory
    )
    os.close(descriptor)
    try:
        shutil.copy2(source_path, temporary_path)
        verify_encrypted_database(temporary_path, key)
        try:
            os.rename(temporary_path, backup_path)
        except FileExistsError:
            verify_encrypted_database(backup_path, key)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def ensure_encrypted_database(
    database_path,
    key_path,
    initial_database_path,
    legacy_database_path=None,
    remove_legacy=False,
):
    """Create, migrate, or verify the app database without replacing it on failure."""
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    legacy_is_migration_source = False

    if os.path.isfile(database_path):
        is_plaintext = database_is_plaintext(database_path)
        key = load_or_create_key(key_path, create_if_missing=is_plaintext)
        if is_plaintext:
            encrypt_plain_database(database_path, database_path, key)
        else:
            verify_encrypted_database(database_path, key)
    else:
        source_path = initial_database_path
        if (
            legacy_database_path
            and os.path.isfile(legacy_database_path)
            and os.path.abspath(legacy_database_path) != os.path.abspath(database_path)
        ):
            source_path = legacy_database_path
            legacy_is_migration_source = True
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Base de données initiale introuvable : {source_path}")

        key = load_or_create_key(key_path, create_if_missing=True)
        encrypt_plain_database(source_path, database_path, key)

    if (
        remove_legacy
        and legacy_database_path
        and os.path.isfile(legacy_database_path)
        and os.path.abspath(legacy_database_path) != os.path.abspath(database_path)
    ):
        backup_path = database_path + ".pre-sqlcipher"
        if not legacy_is_migration_source and not os.path.isfile(backup_path):
            raise DatabaseEncryptionError(
                "La base chiffrée et l'ancienne base coexistent; vérifiez et sauvegardez "
                "les deux fichiers avant de supprimer l'ancienne base."
            )
        _create_encrypted_backup(database_path, backup_path, key)
        os.remove(legacy_database_path)

    return key