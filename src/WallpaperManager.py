import os
import sys
import utils

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

    def get_wallpaper():
        color_scheme = str(utils.get_color_scheme())
        wp_keys = {"'default'": "picture-uri", "'prefer-dark'": "picture-uri-dark"}
        wp_schema = "org.gnome.desktop.background"
        return Ptk.utils.gsettings_get(wp_schema, wp_keys[color_scheme])
