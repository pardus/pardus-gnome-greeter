import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .Widget import Widget


class ToggleButton(Gtk.ToggleButton, Widget):
    def __init__(self, *args, group=None, child=None, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.set_group(group)
        self.set_child(child)
