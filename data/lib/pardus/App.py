import gi
import sys
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw
from .ApplicationWindow import ApplicationWindow
from .Widget import Widget


class App(Adw.Application):
    def __init__(
        self,
        *args,
        application_id=None,
        title=None,
        height=-1,
        width=-1,
        css_file_path=None,
        **kwargs
    ):
        super().__init__()

        self.window = None
        self.connect("activate", self.activate)

    def activate(self, app):
        self.window.present()
        self.window = ApplicationWindow(title=title, height=height, width=width)
        self.window.set_application(self)
