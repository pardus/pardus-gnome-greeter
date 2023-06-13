import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .utils import utils
from .gtk_settings import settings
from .Widget import Widget


class ListBoxRow(Gtk.ListBoxRow, Widget):
    def __init__(self, *args,child=None, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.set_child(child)
