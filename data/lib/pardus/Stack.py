import gi
gi.require_version("Gtk","4.0")
from gi.repository import Gtk
from .Widget import Widget
class Stack(Gtk.Stack,Widget):
    def __init__(self,*args,**kwargs):
        super().__init__(self,*args,**kwargs)
        