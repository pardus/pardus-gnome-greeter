import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango
from .Widget import Widget

ellipsize_mode = {
    "none": Pango.EllipsizeMode(0),
    "start": Pango.EllipsizeMode(1),
    "middle": Pango.EllipsizeMode(2),
    "end": Pango.EllipsizeMode(3),
}


class Label(Gtk.Label, Widget):
    def __init__(
        self,
        *args,
        label="",
        markup="",
        ellipsize="none",
        xalign=0,
        yalign=0,
        lines=1,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.set_text(label)
        self.set_ellipsize(ellipsize_mode[ellipsize])
        if len(markup) > 0:
            self.set_markup(markup)
        self.set_xalign(xalign)
        self.set_yalign(yalign)
        self.set_lines(lines)
