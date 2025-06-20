"""
Setup package for Telos
"""

from .setup import setup_telos
from .gsheet_setup import setup_gsheet_connection

__all__ = ['setup_telos', 'setup_gsheet_connection'] 