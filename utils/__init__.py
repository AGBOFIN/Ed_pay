"""
Package utils pour EduPaie.
"""

from .resource_utils import (
	resource_path,
	get_app_dir,
	get_user_data_dir,
	get_database_path,
	get_database_key_path,
	get_initial_database_path,
	get_legacy_database_path,
	get_recus_dir,
	ensure_data_dirs,
	copy_initial_database_if_needed,
)
from .error_handler import setup_exception_handler

__all__ = [
	'resource_path', 'get_app_dir', 'get_user_data_dir', 'get_database_path',
	'get_database_key_path', 'get_initial_database_path',
	'get_legacy_database_path', 'get_recus_dir', 'ensure_data_dirs',
	'copy_initial_database_if_needed', 'setup_exception_handler',
]
