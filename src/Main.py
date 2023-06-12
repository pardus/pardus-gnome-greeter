#!/usr/bin/env python3

import gi, sys

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GLib, Adw


class Application(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="tr.org.pardus.pardus-gnome-greeter",
            flags=Gio.ApplicationFlags(8),
            **kwargs
        )
        self.connect("activate", self.on_activate)
        self.main_window = None

        self.add_main_option(
            "details",
            ord("d"),
            GLib.OptionFlags(0),
            GLib.OptionArg(1),
            "Details page of application",
            None,
        )

        self.add_main_option(
            "remove",
            ord("r"),
            GLib.OptionFlags(0),
            GLib.OptionArg(1),
            "Remove page of application",
            None,
        )

    def on_activate(self, app):
        if not self.main_window:
            from MainWindow import MainWindow

            self.main_window = MainWindow().window
            self.main_window.set_application(self)
            self.main_window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()
        self.args = options
        self.activate()
        return 0


app = Application()
app.run(sys.argv)
