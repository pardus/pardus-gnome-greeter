import gettext
import builtins
from pathlib import Path

APP_NAME = "pardus-gnome-greeter"

def init_translation():
    """Initializes gettext for the application."""
    
    localedir = Path('/usr/share/locale')
    
    try:
        translation = gettext.translation(APP_NAME, localedir=str(localedir), fallback=True)
        builtins._ = translation.gettext
    except FileNotFoundError:
        # This can happen if the .mo files are not found for the current locale
        print(f"Warning: Translation files for domain '{APP_NAME}' not found in '{localedir}'. Using default strings.")
        builtins._ = lambda s: s
