import gi
import os
import dbus
import subprocess

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio, GLib


class utils:
    def val_to_variant(val):
        if type(val) == float:
            return GLib.Variant.new_double(val)
        if type(val) == str:
            return GLib.Variant.new_string(val)
        if type(val) == int:
            return GLib.Variant.new_int32(val)
        if type(val) == GLib.Variant:
            return val

    def get_session():
        return os.environ["XDG_SESSION_TYPE"]

    def load_css(css_file_path):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(css_file_path)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def gsettings_set(schema, key, value):
        gio_val = utils.val_to_variant(value)
        settings = Gio.Settings.new(schema)
        return settings.set_value(key, gio_val)

    def gsettings_get(schema, key):
        settings = Gio.Settings.new(schema)
        return settings.get_value(key)
