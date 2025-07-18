#!/usr/bin/env python3
import sys
import os
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gio, GLib, Gtk, Adw

def load_gresource():
    """Loads the GResource file."""
    script_path = os.path.abspath(sys.argv[0])
    
    if 'build' in script_path.split(os.sep):
        project_root = os.path.dirname(os.path.dirname(script_path))
        resource_path = os.path.join(project_root, 'build', 'pardus-gnome-greeter.gresource')
    else:
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