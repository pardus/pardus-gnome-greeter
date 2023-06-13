import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .utils import utils
from .Widget import Widget
from .gtk_settings import settings


class ListBox(Gtk.ListBox, Widget):
    def __init__(self,*args,show_seperators=False,**kwargs):
        super().__init__(self,*args,**kwargs)
        self.set_show_separators(show_seperators)
    