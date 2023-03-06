
import subprocess
import gi
import os
import time
import glob

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk,Gdk,Gio,GObject,GdkPixbuf,GLib
from utils import get_current_theme


class WallpaperManager:
    def change_wallpaper(self,picture_uri):
        theme = get_current_theme()
        theme_uri = "picture-uri"
        if "dark" in theme:
            theme_uri+="-dark"
        full_path = "file://"+picture_uri
        cmd = "gsettings set org.gnome.desktop.background %s '%s'"%(theme_uri,full_path)
        return GLib.spawn_command_line_sync(cmd)
        
    def get_wallpapers(self):
        wallpaper_dir = "/usr/share/backgrounds"
        wallpapers = []
        for root, dirs, files in os.walk(wallpaper_dir):
            if root == wallpaper_dir:
                continue
            dirs.clear()
            for file_name in files:
                path = os.path.join(root,file_name)
                wallpapers.append(path)

        print(wallpapers)
        return wallpapers
        #paths = os.listdir(path)
        #complete_paths = []
        #for item in paths:
        #    complete_paths.append(path + item)
        #return complete_paths
    