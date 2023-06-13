import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib
from .Widget import Widget

settings = {
    "none": Gtk.SelectionMode(0),
    "single": Gtk.SelectionMode(1),
    "browse": Gtk.SelectionMode(2),
    "multiple": Gtk.SelectionMode(3),
}


class FlowBox(Gtk.FlowBox, Widget):
    def __init__(
        self,
        *args,
        row_spacing=0,
        column_spacing=0,
        max_children_per_line=4,
        min_children_per_line=0,
        selection_mode="none",
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.set_row_spacing(row_spacing)
        self.set_column_spacing(column_spacing)
        self.set_selection_mode(settings[selection_mode])
        self.set_min_children_per_line(min_children_per_line)
        self.set_max_children_per_line(max_children_per_line)
