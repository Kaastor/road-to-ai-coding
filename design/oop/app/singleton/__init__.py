"""
Singleton pattern implementation with thread safety.

This module provides a thread-safe Singleton implementation for database
connection management.
"""

from .database_manager import DatabaseConnectionManager

__all__ = ['DatabaseConnectionManager']