import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .gtk_settings import settings
from .Widget import Widget


class Button(Gtk.Button, Widget):
    def __init__(self, *args, label="", icon="", frame=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_label(label)
        self.set_has_frame(frame)
        if len(icon) > 0:
            self.set_icon_name(icon)
