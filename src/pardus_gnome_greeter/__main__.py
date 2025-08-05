#!/usr/bin/env python3
import sys
import os
import locale
import gi

# Gettext setup - must be done before any other imports
from locale import gettext as _
locale.bindtextdomain('pardus-gnome-greeter', '/usr/share/locale')
locale.textdomain('pardus-gnome-greeter')

# Enable translation support for UI files
Gtk = None  # Will be imported later

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gio, GLib, Gtk, Adw

def load_gresource():
    """Loads the GResource file."""
    # Simplified dev environment check
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    build_dir = os.path.join(project_root, 'build')
    resource_path = os.path.join(build_dir, 'pardus-gnome-greeter.gresource')

    if os.path.exists(build_dir) and os.path.exists(resource_path):
        # Development environment
        pass
    else:
        # Installed environment
        resource_path = "/usr/share/pardus-gnome-greeter/pardus-gnome-greeter.gresource"

    try:
        resource = Gio.resource_load(resource_path)
        Gio.Resource._register(resource)
        print(f"GResource loaded from {resource_path}")
    except GLib.Error as e:
        print(f"FATAL: Could not load GResource: {e}")
        sys.exit(1)

# Load GResource before importing any UI code
load_gresource()

# Import UI classes after GResource is loaded
from .main_window import MainWindow

class PardusGreeterApplication(Adw.Application):
    """The main application."""

    def __init__(self):
        super().__init__(application_id='tr.org.pardus.pardus-gnome-greeter',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.win = None

    def do_activate(self):
        """Called when the application is activated."""
        if not self.win:
            self.win = MainWindow(application=self)
        self.win.present()

def main():
    """The main entry point of the application."""
    app = PardusGreeterApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main()) 