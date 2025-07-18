import gi
import sys
import locale
import os

from libpardus import Ptk
from locale import gettext as _

gi.require_version("Gtk", "4.0")
from LayoutManager import LayoutManager
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib, GObject

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)


layouts = [
    {
        "id": "gnome",
        "label": "Classic",
        "gif": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_gif_gnome.gif",
        "img": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_img_gnome.svg",
        "togglebutton": None,
    },
    {
        "id": "mac",
        "label": "Mac",
        "gif": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_gif_mac.gif",
        "img": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_img_mac.svg",
        "togglebutton": None,
    },
    {
        "id": "ubuntu",
        "label": "Ubuntu",
        "gif": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_gif_ubuntu.gif",
        "img": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_img_ubuntu.svg",
        "togglebutton": None,
    },
    {
        "id": "10",
        "label": "10",
        "gif": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_gif_10.gif",
        "img": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_img_10.svg",
        "togglebutton": None,
    },
    {
        "id": "xp",
        "label": "XP",
        "gif": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_gif_xp.gif",
        "img": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_img_xp.svg",
        "togglebutton": None,
    },
    {
        "id": "pardus",
        "label": "Pardus",
        "gif": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_gif_pardus.gif",
        "img": os.path.dirname(os.path.abspath(__file__)) + "/../../data/assets/layout_img_pardus.svg",
        "togglebutton": None,
    },
]


def fun_create():
    # RETURNING EXTENSION BOX
    # _______(Box)_____________________________________
    # |                                                 |
    # |    _______(Box)______    _______(Box)____  |    |
    # |   |                  |  |                  |    |
    # |   |  (ToggleButton)  |  |  (ToggleButton)  |    |
    # |   |    (Layout 1)    |  |    (Layout 2)    |    |
    # |   |                  |  |                  |    |
    # |   |      [Image]     |  |      [Image]     |    |
    # |   |__________________|  |__________________|    |
    # |                                            |    |
    # |    _______(Box)______    _______(Box)____  |    |
    # |   |                  |  |                  |    |
    # |   |  (ToggleButton)  |  |  (ToggleButton)  |    |
    # |   |    (Layout 3)    |  |    (Layout 4)    |    |
    # |   |                  |  |                  |    |
    # |   |      [Image]     |  |      [Image]     |    |
    # |   |__________________|  |__________________|    |
    # |                                                 |
    # |_________________________________________________|

    flowbox = Ptk.FlowBox(
        min_children_per_line=3,
        max_children_per_line=3,
        row_spacing=21,
        column_spacing=21,
        halign="center",
        valign="center",
        hexpand=True,
        vexpand=True,
        margin_bottom=21,
        margin_end=21,
        margin_start=21,
        margin_top=21,
        selection_mode="none",
    )
    flowbox.set_homogeneous(True)

    for index, layout in enumerate(layouts):
        toggle_box = fun_create_togglebutton_img(index)
        toggle = Ptk.ToggleButton(
            name=layout["id"], group=layouts[0]["togglebutton"], child=toggle_box
        )
        current_layout = str(LayoutManager.get_layout())
        toggle.set_active(current_layout == layout["id"])
        toggle.connect("toggled", LayoutManager.set_layout)

        motion_controller = Gtk.EventControllerMotion()
        toggle.add_controller(motion_controller)
        motion_controller.connect("enter", on_motion_enter, index, toggle)
        motion_controller.connect("leave", on_motion_leave, index, toggle)
        layout["togglebutton"] = toggle
        flowbox.insert(toggle, -1)

    box = Ptk.Box(
        spacing=21,
        hexpand=True,
        vexpand=True,
        homogeneous=True,
        orientation="vertical",
        children={flowbox},
    )
    return box


class GifPaintable(GObject.Object, Gdk.Paintable):
    def __init__(self, path):
        super().__init__()
        self.animation = GdkPixbuf.PixbufAnimation.new_from_file(path)
        self.iterator = self.animation.get_iter()
        self.delay = self.iterator.get_delay_time()
        self.timeout = GLib.timeout_add(self.delay, self.on_delay)

        self.invalidate_contents()

    def on_delay(self):
        delay = self.iterator.get_delay_time()
        self.timeout = GLib.timeout_add(delay, self.on_delay)
        self.invalidate_contents()

        return GLib.SOURCE_REMOVE

    def do_get_intrinsic_height(self):
        return self.animation.get_height()

    def do_get_intrinsic_width(self):
        return self.animation.get_width()

    def invalidate_contents(self):
        self.emit("invalidate-contents")

    def do_snapshot(self, snapshot, width, height):
        timeval = GLib.TimeVal()
        timeval.tv_usec = GLib.get_real_time()
        self.iterator.advance(timeval)
        pixbuf = self.iterator.get_pixbuf()
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)

        texture.snapshot(snapshot, width, height)


def fun_create_togglebutton_img(index):
    img = layouts[index]["img"]
    label = _(layouts[index]["label"]) + " " + _("Style")
    image = Gtk.Picture.new_for_filename(img)
    Label = Ptk.Label(label=label, halign="center")

    toggle_box = Ptk.Box(
        spacing=13,
        orientation="vertical",
        children=[image, Label],
        halign="center",
        valign="center",
    )
    return toggle_box


def fun_create_togglebutton_gif(index):
    gif = layouts[index]["gif"]
    label = _(layouts[index]["label"]) + " " + _("Style")

    Label = Ptk.Label(label=label, halign="center")
    paintable = GifPaintable(gif)
    picture = Gtk.Picture()

    picture.set_paintable(paintable)
    toggle_box = Ptk.Box(
        spacing=13,
        orientation="vertical",
        children=[picture, Label],
        halign="center",
        valign="center",
    )
    return toggle_box


def on_motion_enter(controller, x, y, index, toggle):
    gif = fun_create_togglebutton_gif(index)
    GLib.idle_add(toggle.set_child, gif)


def on_motion_leave(controller, index, toggle):
    img = fun_create_togglebutton_img(index)
    GLib.idle_add(toggle.set_child, img)
