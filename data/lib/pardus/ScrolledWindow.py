import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib
from .Widget import Widget


class ScrolledWindow(Gtk.ScrolledWindow, Widget):
    def __init__(self, *args, child: Gtk.Widget = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_child(child)
