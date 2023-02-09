
import subprocess
import gi
import os
import time
import glob

gi.require_version("Gtk", "4.0")
from gi.repository import GLib

class WallpaperManager:
    def change_wallpaper(self,picture_uri):
        full_path = "file:///"+picture_uri
        cmd = "gsettings set org.gnome.desktop.background picture-uri %s"%full_path
        return GLib.spawn_command_line_sync(cmd)
    def get_wallpapers(self):
        path = "/usr/share/backgrounds/gnome/"
        paths = os.listdir(path)
        complete_paths = []
        for item in paths:
            complete_paths.append(path + item)
        return complete_paths