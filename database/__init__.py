"""
Database package for SoilWise
Uses custom SQLite manager with raw sqlite3
"""

from database.db_manager import DatabaseManager, get_database

__all__ = ['DatabaseManager', 'get_database']
