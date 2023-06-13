import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .Widget import Widget


class Image(Gtk.Image, Widget):
    def __init__(
        self, *args, file=None, icon=None, icon_size=None, pixel_size=None, **kwargs
    ):
        super().__init__(self, *args, **kwargs)
        if icon != None:
            self.set_from_icon_name(icon)
        if file != None:
            self.set_from_file(file)

        if icon_size != None:
            self.set_icon_size(icon_size)
        if pixel_size != None:
            self.set_pixel_size(pixel_size)
