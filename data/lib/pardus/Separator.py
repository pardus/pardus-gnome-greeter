import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .Widget import Widget
from .gtk_settings import settings


class Separator(Gtk.Separator, Widget):
    def __init__(self, orientation):
        super().__init__()
        self = Gtk.Separator.new(settings[orientation])
