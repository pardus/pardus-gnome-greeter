import gi
import sys

sys.path.append("../")
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from data.lib.pardus import Ptk
from LayoutManager import LayoutManager


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
        {"id": "layout_1", "img": "../data/assets/set1.svg", "togglebutton": None},
        {"id": "layout_2", "img": "../data/assets/set2.svg", "togglebutton": None},
        {"id": "layout_3", "img": "../data/assets/set3.svg", "togglebutton": None},
        {"id": "layout_4", "img": "../data/assets/set4.svg", "togglebutton": None},
    ]

    for index, layout in enumerate(layouts):
        image = Ptk.Image(file=layout["img"], pixel_size=60)
        toggle = Ptk.ToggleButton(
            name=layout["id"], group=layouts[0]["togglebutton"], child=image
        )
        toggle.connect("toggled", LayoutManager.set_layout)
        current_layout = str(LayoutManager.get_layout())
        toggle.set_active(current_layout == layout["id"])
        layout["togglebutton"] = toggle

    box1 = Ptk.Box(
        spacing=23,
        homogeneous=True,
        hexpand=True,
        vexpand=True,
        children=[layouts[0]["togglebutton"], layouts[1]["togglebutton"]],
    )
    box2 = Ptk.Box(
        spacing=23,
        homogeneous=True,
        hexpand=True,
        vexpand=True,
        children=[layouts[2]["togglebutton"], layouts[3]["togglebutton"]],
    )

    box = Ptk.Box(
        spacing=23,
        hexpand=True,
        vexpand=True,
        orientation="vertical",
        children=[box1, box2],
        css=["p-23"],
    )
    return box
