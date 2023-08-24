import subprocess
import gi
import os
import sys
import time
import glob

sys.path.append("../")
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, GLib
from utils import get_current_theme
from libpardus import Ptk


class WallpaperManager:
    def change_wallpaper(self, picture_uri):
        theme = str(get_current_theme())
        theme_schema = "org.gnome.desktop.background"
        theme_keys = {
            "'prefer-dark'": "picture-uri-dark",
            "'default'": "picture-uri",
        }
        return Ptk.utils.gsettings_set(
            theme_schema, theme_keys[theme], "file://" + picture_uri
        )

    def get_wallpapers(self):
        wallpaper_dir = "/usr/share/backgrounds"
        wallpapers = []
        for root, dirs, files in os.walk(wallpaper_dir):
            dirs.clear()
            for file_name in files:
                path = os.path.join(root, file_name)
                wallpapers.append(path)

        return wallpapers
