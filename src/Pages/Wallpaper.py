import gi
import sys
import threading

sys.path.append("../../")
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from libpardus import Ptk
from LayoutManager import LayoutManager
from WallpaperManager import WallpaperManager


class WallpaperPage:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui_wallpapers_flowbox = Ptk.FlowBox(
            column_spacing=8,
            hexpand=True,
            max_children_per_line=5,
            min_children_per_line=3,
            selection_mode="single",
        )
        self.ui_wallpapers_flowbox.connect(
            "child-activated", self.on_wallpaper_selected
        )

        self.wallpapers = WallpaperManager.get_wallpapers(None)
        thread = threading.Thread(
            target=self.fun_create_images, args=(self.wallpapers,)
        )
        thread.daemon = True
        thread.start()
        self.scrolled_window = Ptk.ScrolledWindow(
            hexpand=True,
            vexpand=True,
            margin_bottom=21,
            margin_end=21,
            margin_start=21,
            margin_top=21,
            child=self.ui_wallpapers_flowbox,
        )
        self.box = Ptk.Box(
            hexpand=True,
            vexpand=True,
            children=[self.scrolled_window],
        )

    def on_wallpaper_selected(self, flowbox, flowbox_child):
        index = flowbox_child.get_index()
        WallpaperManager.change_wallpaper(self, self.wallpapers[index])

    def fun_create_images(self, wallpapers):
        for wp in wallpapers:
            pixbuff = GdkPixbuf.Pixbuf.new_from_file(wp)
            pixbuff = pixbuff.scale_simple(260, 180, GdkPixbuf.InterpType.BILINEAR)
            image = Ptk.Image(height=260,width=180)
            image.set_from_pixbuf(pixbuff)
            GLib.idle_add(self.ui_wallpapers_flowbox.insert, image, -1)


def fun_create():
    # WALLPAPER PAGE BOX
    #  __(CONTAINER)____________________________
    # |                                        |
    # |        ___(ScrolledWindow)_____        |
    # |       |                        |       |
    # |       |                        |       |
    # |       |         _(FlowBox)__   |       |
    # |       |        |           |   |       |
    # |       |        |           |   |       |
    # |       |        |           |   |       |
    # |       |        |           |   |       |
    # |       |        |___________|   |       |
    # |       |________________________|       |
    # |                                        |
    # |________________________________________|

    return WallpaperPage().box
