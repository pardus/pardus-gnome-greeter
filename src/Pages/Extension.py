import os
import gi
import json

gi.require_version("Gtk", "4.0")
from libpardus import Ptk
from gi.repository import Gtk
from ExtensionManager import ExtensionManager


def fun_extension_toggle(switch, param, extension_id):
    info = {True: "enable", False: "disable"}
    status = info[switch.get_active()]
    ExtensionManager.extension_operations(status, extension_id)


def fun_create_extension_box(extension_props, extensions):
    # RETURNING EXTENSION BOX
    # _______(Container)______________________________
    # |                                               |
    # |     _____(Header)_________________________    |
    # |    |   logo | extension name    | switch |    |
    # |    ---------------------------------------    |
    # |                                               |
    # |     _____(description)___________________|    |
    # |    | extension long description          |    |
    # |    |_____________________________________|    |
    # |    |                                     |    |
    # |    |    ___(Image)_________________      |    |
    # |    |   |                          |      |    |
    # |    |   |                          |      |    |
    # |    |   |                          |      |    |
    # |    |   |                          |      |    |
    # |    |   |__________________________|      |    |
    # |    |_____________________________________|    |
    # |                                               |
    # |_______________________________________________|

    # EXTENSION LOGO
    ui_image_logo = Ptk.Image(file=extension_props["logo"], halign="start")

    # EXTENSION IMAGE
    ui_image_extension_image = Ptk.Image(
        file=extension_props["image"], height=150, width=180
    )

    # EXTENSION NAME
    ui_label_name = Ptk.Label(
        label=extension_props["name"], hexpand=True, halign="start", valign="center"
    )
    # SWITCH TO CONTROL STATE OF EXTENSION

    ui_switch_toggle = Gtk.Switch()
    ui_switch_toggle.connect(
        "notify::active", fun_extension_toggle, extension_props["id"]
    )
    ui_switch_toggle.set_sensitive(True)
    if extension_props["id"] in extensions:
        ui_switch_toggle.set_active(True)
    else:
        ui_switch_toggle.set_active(False)

    # HEADER THAT GOT LOGO EXTENSION NAME AND SWITCH
    ui_box_header = Ptk.Box(
        spacing=5,
        valign="start",
        css=["only-top-border"],
        children=[ui_image_logo, ui_label_name, ui_switch_toggle],
    )

    # EXTENSION DESCRIPTION
    ui_label_description = Ptk.Label(
        label=extension_props["description"],
        halign="start",
        valign="start",
        ellipsize="middle",
        lines=5,
        margin_top=20,
        margin_end=20,
        margin_start=20,
    )
    # ADDING HEADER AND OTHER ELEMENTS TO CONTAINER
    ui_box_container = Ptk.Box(
        orientation="vertical",
        spacing=13,
        hexpand=True,
        vexpand=True,
        css=["bordered-box-nop"],
        valign="start",
        children=[ui_label_description, ui_image_extension_image, ui_box_header],
    )
    # RETURN CONTAINER
    return ui_box_container


def fun_create():
    extension_datas = None
    enabled_extensions = ExtensionManager.get_extensions("enabled-extensions")
    ui_extension_flowbox = Ptk.FlowBox(
        hexpand=True,
        vexpand=True,
        max_children_per_line=5,
        min_children_per_line=2,
        row_spacing=23,
        column_spacing=23,
    )

    with open(
        os.path.dirname(os.path.abspath(__file__)) + "/../../data/extensions.json"
    ) as file_content:
        extension_datas = json.loads(file_content.read())
    for item in extension_datas:
        extension = fun_create_extension_box(item, enabled_extensions)
        ui_extension_flowbox.insert(extension, -1)
    ui_extension_scrolledwindow = Ptk.ScrolledWindow(
        vexpand=True, hexpand=True, child=ui_extension_flowbox
    )
    ui_extension_box = Ptk.Box(
        vexpand=True, hexpand=True, css=["p-23"], children=[ui_extension_scrolledwindow]
    )
    return ui_extension_box
