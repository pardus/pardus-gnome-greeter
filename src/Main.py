#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class Application(Gtk.Application):

    def __init__(self, **kwargs):
        super().__init__(**kwargs, application_id="tr.org.pardus.pardus-gnome-greeter")
        self.connect('activate', self.on_activate)
        self.main_window = None

    def on_activate(self, app):
        if not self.main_window:
            from MainWindow import MainWindow
            self.main_window = MainWindow().main_window
            self.main_window.set_application(self)
            self.main_window.present()


app = Application()
app.run(None)
