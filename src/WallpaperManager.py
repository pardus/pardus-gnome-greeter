import os
import sys

sys.path.append("../")
from libpardus import Ptk


class WallpaperManager:
    def change_wallpaper(self, picture_uri):
        theme_schema = "org.gnome.desktop.background"
        theme_keys = ["picture-uri-dark", "picture-uri"]
        for theme in theme_keys:
            Ptk.utils.gsettings_set(theme_schema, theme, "file://" + picture_uri)
        return True

    def get_wallpapers(self):
        wallpaper_dir = "/usr/share/backgrounds"
        wallpapers = []
        for root, dirs, files in os.walk(wallpaper_dir):
            dirs.clear()
            for file_name in files:
                path = os.path.join(root, file_name)
                wallpapers.append(path)

        return wallpapers
