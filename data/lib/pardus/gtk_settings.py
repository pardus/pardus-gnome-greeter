import gi
gi.require_version('Gtk','4.0')
gi.require_version('Adw','1')
from gi.repository import Gtk, Adw

settings = {
    "horizontal":Gtk.Orientation(0),
    "vertical":Gtk.Orientation(1),
    "fill":Gtk.Align(0),
    "start":Gtk.Align(1),
    "end":Gtk.Align(2),
    "center":Gtk.Align(3),
    "baseline":Gtk.Align(4),
}