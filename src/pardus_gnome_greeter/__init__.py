"""
Pardus GNOME Greeter - Managers and components

This package contains managers and components from the Pardus GNOME Greeter
application. Users can import this package in their Python projects to
manage GNOME desktop settings.
"""

__version__ = "0.0.13"

# Export managers
from .managers import (
    ShortcutManager,
    ThemeManager,
    WallpaperManager,
    DisplayManager,
    ExtensionManager,
    LayoutManager,
    SettingsManager,
)

# Export settings instances
from .managers.settings import (
    app_settings,
    theme_settings,
    shell_settings,
    background_settings,
)

__all__ = [
    'ShortcutManager',
    'ThemeManager',
    'WallpaperManager',
    'DisplayManager',
    'ExtensionManager',
    'LayoutManager',
    'SettingsManager',
    'app_settings',
    'theme_settings',
    'shell_settings',
    'background_settings',
]

