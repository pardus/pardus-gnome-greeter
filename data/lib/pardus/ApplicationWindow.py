import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from .utils import utils


# session = utils.get_session()
# application_windows = {"x11": Gtk.ApplicationWindow, "wayland": Adw.ApplicationWindow}
class ApplicationWindow(Gtk.ApplicationWindow):
    def __init__(
        self,
        *args,
        title="",
        titlebar=None,
        icon_name=None,
        height=-1,
        width=-1,
        **kwargs
    ):
        super().__init__()
        self.set_title(title)
        self.set_titlebar(titlebar)
        self.set_icon_name(icon_name)
        self.set_default_size(width, height)
