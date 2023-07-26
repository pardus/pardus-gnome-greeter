import gi
import sys

sys.path.append("../")
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, Gio, GLib, GObject
from libpardus import Ptk
from LayoutManager import LayoutManager


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

    layouts = [
        {
            "id": "gnome",
            "label": "Classic",
            "img": "../data/assets/set5.gif",
            "togglebutton": None,
        },
        {
            "id": "mac",
            "label": "Mac",
            "img": "../data/assets/set1.gif",
            "togglebutton": None,
        },
        {
            "id": "ubuntu",
            "label": "Ubuntu",
            "img": "../data/assets/set4.gif",
            "togglebutton": None,
        },
        {
            "id": "10",
            "label": "10",
            "img": "../data/assets/set2.gif",
            "togglebutton": None,
        },
        {
            "id": "xp",
            "label": "XP",
            "img": "../data/assets/set3.gif",
            "togglebutton": None,
        },
    ]

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
    )
    flowbox.set_homogeneous(True)

    for index, layout in enumerate(layouts):
        image = Ptk.Image(file=layout["img"])
        label = Ptk.Label(label=layout["label"] + " Style", halign="center")
        paintable = GifPaintable(layout["img"])

        picture = Gtk.Picture()
        picture.set_paintable(paintable)
        toggle_box = Ptk.Box(
            orientation="vertical",
            children=[picture, label],
            halign="center",
            valign="center",
            spacing=13,
            width=220,
            height=100,
        )

        toggle = Ptk.ToggleButton(
            name=layout["id"],
            group=layouts[0]["togglebutton"],
            child=toggle_box,
        )
        toggle.connect("toggled", LayoutManager.set_layout)
        current_layout = str(LayoutManager.get_layout())
        toggle.set_active(current_layout == layout["id"])
        layout["togglebutton"] = toggle

    box1 = Ptk.Box(
        spacing=21,
        homogeneous=True,
        hexpand=True,
        vexpand=True,
        margin_top=21,
        margin_end=21,
        margin_start=21,
        children=[
            layouts[0]["togglebutton"],
            layouts[1]["togglebutton"],
            layouts[2]["togglebutton"],
        ],
    )
    box2 = Ptk.Box(
        spacing=21,
        homogeneous=True,
        hexpand=True,
        vexpand=True,
        halign="center",
        margin_bottom=21,
        children=[layouts[3]["togglebutton"], layouts[4]["togglebutton"]],
    )

    box = Ptk.Box(
        spacing=21,
        hexpand=True,
        vexpand=True,
        homogeneous=True,
        orientation="vertical",
        children=[box1, box2],
    )
    return box
