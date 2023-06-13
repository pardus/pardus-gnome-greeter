import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .gtk_settings import settings

align_settings = {
    "fill": Gtk.Align(0),
    "start": Gtk.Align(1),
    "end": Gtk.Align(2),
    "center": Gtk.Align(3),
    "baseline": Gtk.Align(4),
}


class Widget(Gtk.Widget):
    def __init__(
        self,
        *args,
        css=[],
        name="",
        hexpand=False,
        vexpand=False,
        height=-1,
        width=-1,
        halign="fill",
        valign="fill",
        margin_top=0,
        margin_bottom=0,
        margin_start=0,
        margin_end=0,
        **kwargs
    ):
        super().__init__()
        self.set_css_classes(css)
        self.set_name(name)
        self.set_hexpand(hexpand)
        self.set_vexpand(vexpand)
        self.set_margin_top(margin_top)
        self.set_margin_bottom(margin_bottom)
        self.set_margin_start(margin_start)
        self.set_margin_end(margin_end)
        self.set_size_request(width, height)
        self.set_halign(align_settings[halign])
        self.set_valign(align_settings[valign])
