import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .gtk_settings import settings
from .Widget import Widget


class Box(Gtk.Box, Widget):
    def __init__(
        self,
        *args,
        orientation="horizontal",
        homogeneous=False,
        spacing=-1,
        name="",
        children=[],
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.set_orientation(settings[orientation])
        self.set_spacing(spacing)
        self.set_homogeneous(homogeneous)
        self.set_name(name)
        for child in children:
            self.append(child)
