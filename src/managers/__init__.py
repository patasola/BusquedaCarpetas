# src/managers/__init__.py
"""
Managers refactorizados con clase base compartida
"""

from .base_tree_manager import BaseTreeManager
from .file_explorer import FileExplorer
from .historial import Historial
from .tree_navigator import TreeNavigator

__all__ = ['BaseTreeManager', 'FileExplorer', 'Historial', 'TreeNavigator']
