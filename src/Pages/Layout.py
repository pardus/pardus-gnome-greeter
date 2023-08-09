import gi
import sys

sys.path.append("../")
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, Gio, GLib, GObject
from libpardus import Ptk
from LayoutManager import LayoutManager

layouts = [
    {
        "id": "gnome",
        "label": "Classic",
        "gif": "../data/assets/layout_gif_gnome.gif",
        "img": "../data/assets/layout_img_gnome.svg",
        "togglebutton": None,
    },
    {
        "id": "mac",
        "label": "Mac",
        "gif": "../data/assets/layout_gif_mac.gif",
        "img": "../data/assets/layout_img_mac.svg",
        "togglebutton": None,
    },
    {
        "id": "ubuntu",
        "label": "Ubuntu",
        "gif": "../data/assets/layout_gif_ubuntu.gif",
        "img": "../data/assets/layout_img_ubuntu.svg",
        "togglebutton": None,
    },
    {
        "id": "10",
        "label": "10",
        "gif": "../data/assets/layout_gif_10.gif",
        "img": "../data/assets/layout_img_10_1.svg",
        "togglebutton": None,
    },
    {
        "id": "xp",
        "label": "XP",
        "gif": "../data/assets/layout_gif_xp.gif",
        "img": "../data/assets/layout_img_xp.svg",
        "togglebutton": None,
    },
]


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
    label = layouts[index]["label"] + " Style"
    # image = Ptk.Image(file=img, height=231, width=351)
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
    label = layouts[index]["label"] + " Style"

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
    GLib.idle_add(toggle.set_child,gif)
    #toggle.set_child(gif)


def on_motion_leave(controller, index, toggle):
    img = fun_create_togglebutton_img(index)
    GLib.idle_add(toggle.set_child,img)
    #toggle.set_child(img)


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
        toggle.connect("toggled", LayoutManager.set_layout)
        current_layout = str(LayoutManager.get_layout())
        toggle.set_active(current_layout == layout["id"])

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
        # children=[box1, box2],
        children={flowbox},
    )
    return box
