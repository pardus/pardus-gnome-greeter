import os
import gi
from data.lib.pardus import Ptk
from utils import get_current_theme
from gi.repository import GLib


def fun_change_theme(toggle_button):
    schema = "org.gnome.desktop.interface"
    key = "color-scheme"
    name = toggle_button.get_name()
    state = toggle_button.get_active()
    if state:
        Ptk.utils.gsettings_set(schema, key, name)


def fun_create():
    # RETURNING EXTENSION BOX
    # _________________________________________________________________
    # |                                                                 |
    # |  ________(ToggleButton)______  ________(ToggleButton)______     |
    # | |                            ||                            |    |
    # | |        (Prefer Dark)       ||         (Default)          |    |
    # | |                            ||                            |    |
    # | |         [Dark Theme]       ||         [Light Theme]      |    |
    # | |____________________________||____________________________|    |
    # |                                                                 |
    # |_________________________________________________________________|

    cur_dir = os.getcwd()

    ui_dark_image = Ptk.Image(
        file=cur_dir + "/../data/assets/theme-dark.png", pixel_size=350
    )
    ui_light_image = Ptk.Image(
        file=cur_dir + "/../data/assets/theme-light.png", pixel_size=350
    )

    ui_dark_theme_button = Ptk.ToggleButton(
        valign="center",
        halign="center",
        name="prefer-dark",
        group=None,
        child=ui_dark_image,
    )
    ui_dark_theme_button.connect("toggled", fun_change_theme)
    ui_light_theme_button = Ptk.ToggleButton(
        valign="center",
        halign="center",
        name="default",
        group=ui_dark_theme_button,
        child=ui_light_image,
    )
    ui_light_theme_button.connect("toggled", fun_change_theme)
    theme = get_current_theme()
    if str(theme) == "'prefer-dark'":
        ui_dark_theme_button.set_active(True)
    else:
        ui_light_theme_button.set_active(True)

    ui_theme_box = Ptk.Box(
        valign="center",
        homogeneous=True,
        spacing=23,
        css=["p-23"],
        children=[ui_dark_theme_button, ui_light_theme_button],
    )
    return ui_theme_box
