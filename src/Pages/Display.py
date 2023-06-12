import os
import gi

gi.require_version("Gtk", "4.0")
from data.lib.pardus import Ptk
from utils import get_current_theme
from gi.repository import GLib, Gtk
from utils import get_recommended_scale


def fun_change_display_scale(widget):
    value = widget.get_value()
    scale = float(1 + (0.25 * value))

    schema = "org.gnome.desktop.interface"
    key = "text-scaling-factor"
    Ptk.utils.gsettings_set(schema, key, scale)


def fun_change_cursor_scale(widget):
    schema = "org.gnome.desktop.interface"
    key = "cursor-size"
    value = int(widget.get_name())
    if widget.get_active():
        Ptk.utils.gsettings_set(schema, key, value)


def fun_create():
    # RETURNING DISPLAY BOX
    # _______(Box)______________________________
    # |                                          |
    # |    _____(Image)___________               |
    # |   |                       |              |
    # |   |      Logo Image       |              |
    # |   |_______________________|              |
    # |                                          |
    # |    ________(Scale)______                 |
    # |   |                       |              |
    # |   |    Display Scale      |              |
    # |   |                       |              |
    # |   |   [---+---+----+---]  |              |
    # |   |_______________________|              |
    # |                                          |
    # |    ________(Label)______                 |
    # |   |                      |               |
    # |   | Recommended Scale    |               |
    # |   |                      |               |
    # |   |                      |               |
    # |   |                      |               |
    # |   |                      |               |
    # |   |                      |               |
    # |   |______________________|               |
    # |                                          |
    # |__________________________________________|

    ui_logo_image = Ptk.Image(
        file=os.getcwd() + "/../data/assets/logo.svg", pixel_size=200
    )
    ui_display_scale = Ptk.Scale(
        value=0.0,
        lower=0.0,
        upper=4.0,
        step_increment=1.0,
        page_increment=1.0,
        page_size=0.0,
        restrict_to_fill_level=True,
        round_digits=0.0,
    )
    ui_display_scale.add(0, "TOP", "100%")
    ui_display_scale.add(1, "TOP", "125%")
    ui_display_scale.add(2, "TOP", "150%")
    ui_display_scale.add(3, "TOP", "175%")
    ui_display_scale.add(4, "TOP", "200%")

    ui_display_scale.connect("value-changed", fun_change_display_scale)

    ui_recommended_scale_label = Ptk.Label(
        markup=f"<b>Recommended scale option is {get_recommended_scale()}%</b>"
    )

    temporary_icon = Ptk.Image(icon="extensions-symbolic")
    temporary_icon2 = Ptk.Image(icon="extensions-symbolic")
    temporary_icon3 = Ptk.Image(icon="extensions-symbolic")

    ui_default_cursor_togglebutton = Ptk.ToggleButton(
        group=None, name="24", css=["firstbuttonbox"], child=temporary_icon
    )
    ui_default_cursor_togglebutton.connect("toggled", fun_change_cursor_scale)

    ui_2x_cursor_togglebutton = Ptk.ToggleButton(
        group=ui_default_cursor_togglebutton,
        name="48",
        css=["buttonbox"],
        child=temporary_icon2,
    )
    ui_2x_cursor_togglebutton.connect("toggled", fun_change_cursor_scale)
    ui_3x_cursor_togglebutton = Ptk.ToggleButton(
        group=ui_default_cursor_togglebutton,
        name="72",
        css=["lastbuttonbox"],
        child=temporary_icon3,
    )
    ui_3x_cursor_togglebutton.connect("toggled", fun_change_cursor_scale)
    ui_cursor_buttons_box = Ptk.Box(
        margin_top=40,
        hexpand=True,
        halign="center",
        children=[
            ui_default_cursor_togglebutton,
            ui_2x_cursor_togglebutton,
            ui_3x_cursor_togglebutton,
        ],
    )
    ui_font_scale_label = Ptk.Label(
        markup="<span size='12pt'>Cursor Size</span>",
        hexpand=True,
    )

    ui_display_box = Ptk.Box(
        spacing=23,
        vexpand=True,
        hexpand=True,
        orientation="vertical",
        valign="center",
        halign="center",
        children=[
            ui_logo_image,
            ui_display_scale,
            ui_recommended_scale_label,
            ui_cursor_buttons_box,
            ui_font_scale_label,
        ],
    )
    return ui_display_box
