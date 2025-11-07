"""
Manager modules

This module contains manager classes used to manage GNOME desktop settings.
"""

from .ShortcutManager import ShortcutManager
from .ThemeManager import ThemeManager
from .WallpaperManager import WallpaperManager
from .DisplayManager import DisplayManager
from .ExtensionManager import ExtensionManager
from .LayoutManager import LayoutManager
from .settings import SettingsManager

__all__ = [
    'ShortcutManager',
    'ThemeManager',
    'WallpaperManager',
    'DisplayManager',
    'ExtensionManager',
    'LayoutManager',
    'SettingsManager',
]

