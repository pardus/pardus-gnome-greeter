import gettext
import builtins
from pathlib import Path

APP_NAME = "pardus-gnome-greeter"

def init_translation():
    """Initializes gettext for the application."""

    project_root = Path(__file__).parent.parent.parent
    
    dev_localedir = project_root / 'build' / 'data' / 'po'
    install_localedir = Path('/usr/share/locale')

    localedir_to_use = None

    # Prefer development locale dir if it exists, otherwise use system dir
    if dev_localedir.is_dir():
        localedir_to_use = str(dev_localedir)
    else:
        localedir_to_use = str(install_localedir)

    try:
        translation = gettext.translation(APP_NAME, localedir=localedir_to_use, fallback=True)
        builtins._ = translation.gettext
    except FileNotFoundError:
        # This can happen if the .mo files are not found for the current locale
        print(f"Warning: Translation files for domain '{APP_NAME}' not found in '{localedir_to_use}'. Using default strings.")
        builtins._ = lambda s: s
