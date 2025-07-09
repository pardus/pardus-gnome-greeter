import os

import locale

from libpardus import Ptk
from utils import get_recommended_scale, is_gsettings_schema_exists
from locale import gettext as _

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)
di_options = {
    0.0: "tiny",
    1.0: "small",
    2.0: "standard",
    3.0: "large",
    "'tiny'": 0.0,
    "'small'": 1.0,
    "'standard'": 2.0,
    "'large'": 3.0,
}
ni_options = {
    0.0: "small",
    1.0: "small-plus",
    2.0: "medium",
    3.0: "large",
    4.0: "extra-large",
    "'small'": 0.0,
    "'small-plus'": 1.0,
    "'medium'": 2.0,
    "'large'": 3.0,
    "'extra-large'": 4.0,
}


desktop_schema = "org.gnome.desktop.interface"
desktop_key = "text-scaling-factor"

desktop_icons_schema = "org.gnome.shell.extensions.ding"
desktop_icons_key = "icon-size"

nautilus_schema = "org.gnome.nautilus.icon-view"
nautilus_key = "default-zoom-level"
is_nautilus_installed = is_gsettings_schema_exists(nautilus_schema)


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
    cur_dir = os.path.dirname(os.path.abspath(__file__))

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
    markup = f"<b>{_('Recommended scale option for main display is')} {get_recommended_scale()}%</b>"
    ui_recommended_scale_label = Ptk.Label(markup=markup)

    ui_desktop_icons_scale = Ptk.Scale(
        value=0.0,
        lower=0.0,
        upper=3.0,
        step_increment=1.0,
        page_increment=1.0,
        page_size=0.0,
        restrict_to_fill_level=True,
        round_digits=0.0,
    )
    ui_desktop_icons_scale.add(0, "TOP", _("Tiny"))
    ui_desktop_icons_scale.add(1, "TOP", _("Small"))
    ui_desktop_icons_scale.add(2, "TOP", _("Standart"))
    ui_desktop_icons_scale.add(3, "TOP", _("Large"))

    ui_desktop_icons_scale.connect("value-changed", fun_change_desktop_icons_scale)

    ui_desktop_icons_label_markup = f"<b>{_('Desktop icon size')}</b>"
    ui_desktop_icons_label = Ptk.Label(
        markup=ui_desktop_icons_label_markup, margin_top=21
    )

    ui_nautilus_icons_scale = Ptk.Scale(
        value=0.0,
        lower=0.0,
        upper=4.0,
        step_increment=1.0,
        page_increment=1.0,
        page_size=0.0,
        restrict_to_fill_level=True,
        round_digits=0.0,
    )
    ui_nautilus_icons_scale.add(0, "TOP", _("Tiny"))
    ui_nautilus_icons_scale.add(1, "TOP", _("Small"))
    ui_nautilus_icons_scale.add(2, "TOP", _("Standart"))
    ui_nautilus_icons_scale.add(3, "TOP", _("Large"))
    ui_nautilus_icons_scale.add(4, "TOP", _("Huge"))

    ui_nautilus_icons_scale.connect("value-changed", fun_change_nautilus_icons_scale)

    ui_nautilus_icons_label_markup = f"<b>{_('File manager icon size')}</b>"
    ui_nautilus_icons_label = Ptk.Label(
        markup=ui_nautilus_icons_label_markup, margin_top=21
    )

    fun_set_values_to_scale(ui_desktop_icons_scale, ui_nautilus_icons_scale)

    ui_nautilus_not_installed_label = Ptk.Label(
        markup=f"<b>{_('Some options were disabled because Nautilus file manager is not installed')}</b>", margin_top=21
    )

    if is_nautilus_installed:
        ui_nautilus_not_installed_label.set_visible(False)
    else:
        ui_nautilus_icons_scale.set_sensitive(False)
        ui_nautilus_icons_label.set_sensitive(False)

    temporary_icon = Ptk.Image(
        file=cur_dir + "/../../data/assets/cursor.svg", pixel_size=12
    )
    temporary_icon2 = Ptk.Image(
        file=cur_dir + "/../../data/assets/cursor.svg", pixel_size=24
    )
    temporary_icon3 = Ptk.Image(
        file=cur_dir + "/../../data/assets/cursor.svg", pixel_size=36
    )

    ui_default_cursor_togglebutton = Ptk.ToggleButton(
        group=None, name="24", child=temporary_icon
    )
    ui_default_cursor_togglebutton.connect("toggled", fun_change_cursor_scale)

    ui_2x_cursor_togglebutton = Ptk.ToggleButton(
        group=ui_default_cursor_togglebutton,
        name="48",
        child=temporary_icon2,
    )
    ui_2x_cursor_togglebutton.connect("toggled", fun_change_cursor_scale)
    ui_3x_cursor_togglebutton = Ptk.ToggleButton(
        group=ui_default_cursor_togglebutton,
        name="72",
        child=temporary_icon3,
    )
    ui_3x_cursor_togglebutton.connect("toggled", fun_change_cursor_scale)
    ui_cursor_buttons_box = Ptk.Box(
        hexpand=True,
        halign="center",
        css=["linked"],
        children=[
            ui_default_cursor_togglebutton,
            ui_2x_cursor_togglebutton,
            ui_3x_cursor_togglebutton,
        ],
    )
    ui_font_scale_label = Ptk.Label(
        markup=f"<b>{_('Cursor Size')}</b>",
        hexpand=True,
        halign="center",
        margin_top=21,
    )
    ui_display_box = Ptk.Box(
        spacing=21,
        vexpand=True,
        hexpand=True,
        orientation="vertical",
        valign="center",
        halign="center",
        children=[
            # scale
            ui_recommended_scale_label,
            ui_display_scale,
            ui_desktop_icons_label,
            ui_desktop_icons_scale,
            # file man scale
            ui_nautilus_icons_label,
            ui_nautilus_icons_scale,
            ui_nautilus_not_installed_label,
            ui_font_scale_label,
            ui_cursor_buttons_box,
        ],
    )
    return ui_display_box


def fun_change_display_scale(widget):
    value = widget.get_value()
    scale = float(1 + (0.25 * value))
    key = "text-scaling-factor"
    Ptk.utils.gsettings_set(desktop_schema, key, scale)


def fun_change_cursor_scale(widget):
    key = "cursor-size"
    value = int(widget.get_name())
    if widget.get_active():
        Ptk.utils.gsettings_set(desktop_schema, key, value)


def fun_change_desktop_icons_scale(widget):
    widget_value = widget.get_value()
    value = di_options[widget_value]
    Ptk.utils.gsettings_set(desktop_icons_schema, desktop_icons_key, value)


def fun_change_nautilus_icons_scale(widget):
    if not is_nautilus_installed:
        return
    widget_value = widget.get_value()
    value = ni_options[widget_value]
    Ptk.utils.gsettings_set(nautilus_schema, nautilus_key, value)


def fun_set_values_to_scale(desktop, nautilus):
    # Desktop icon size
    desktop_icon_size = str(
        Ptk.utils.gsettings_get(desktop_icons_schema, desktop_icons_key)
    )
    di_value = di_options[desktop_icon_size]
    desktop.set_value(di_value)

    # Nautilus icon size
    if not is_nautilus_installed:
        return
    nautilus_icon_size = str(Ptk.utils.gsettings_get(nautilus_schema, nautilus_key))
    ni_value = ni_options[nautilus_icon_size]
    nautilus.set_value(ni_value)
