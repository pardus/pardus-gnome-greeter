import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .Widget import Widget

settings = {"horizontal": Gtk.Orientation(0), "vertical": Gtk.Orientation(1)}
position_settings = {
    "LEFT": Gtk.PositionType(0),
    "RIGHT": Gtk.PositionType(1),
    "TOP": Gtk.PositionType(2),
    "BOTTOM": Gtk.PositionType(3),
}


class Scale(Gtk.Scale, Widget):
    def __init__(
        self,
        *args,
        value=0.0,
        lower=0.0,
        upper=0.0,
        step_increment=0.0,
        page_increment=0.0,
        page_size=0.0,
        restrict_to_fill_level=False,
        round_digits=-1,
        orientation="horizontal",
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.adjustment = Gtk.Adjustment.new(
            value, lower, upper, step_increment, page_increment, page_size
        )
        self.set_orientation(settings[orientation])
        self.set_adjustment(self.adjustment)
        self.set_restrict_to_fill_level(restrict_to_fill_level)
        self.set_round_digits(round_digits)

    def add(self, value, position, markup):
        self.add_mark(value, position_settings[position], markup)
