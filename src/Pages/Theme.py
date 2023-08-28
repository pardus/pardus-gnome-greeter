import os
import gi
from libpardus import Ptk
from utils import get_current_theme
from gi.repository import GLib
import locale
from locale import gettext as _

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)

def fun_change_theme(toggle_button,theme_name):
    schema = "org.gnome.desktop.interface"
    key = "color-scheme"
    theme_key = "gtk-theme"
    name = toggle_button.get_name()
    state = toggle_button.get_active()
    if state:
        Ptk.utils.gsettings_set(schema, key, name)
        Ptk.utils.gsettings_set(schema, theme_key, theme_name)


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

    ui_dark_theme_image = Ptk.Image(
        file=cur_dir + "/../data/assets/theme-dark.png", pixel_size=300
    )
    ui_light_theme_image = Ptk.Image(
        file=cur_dir + "/../data/assets/theme-light.png", pixel_size=300
    )

    
    ui_dark_theme_label_markup = f"<b>{_('Dark Theme')}</b>"
    ui_light_theme_label_markup = f"<b>{_('Light Theme')}</b>"
    
    ui_dark_theme_label = Ptk.Label(markup=ui_dark_theme_label_markup,hexpand=True,halign="center")
    
    ui_dark_theme_button = Ptk.ToggleButton(
        valign="center",
        halign="center",
        name="prefer-dark",
        group=None,
        child=ui_dark_theme_image,
    )
    ui_dark_theme_box = Ptk.Box(orientation="vertical",spacing=8,halign="center",children=[ui_dark_theme_button,ui_dark_theme_label])

    
    ui_light_theme_label = Ptk.Label(markup=ui_light_theme_label_markup,hexpand=True,halign="center")
    ui_light_theme_button = Ptk.ToggleButton(
        valign="center",
        halign="center",
        name="default",
        group=ui_dark_theme_button,
        child=ui_light_theme_image,
    )
    ui_light_theme_box = Ptk.Box(orientation="vertical",spacing=8, halign="center",children=[ui_light_theme_button,ui_light_theme_label])


    theme = get_current_theme()
    
    if str(theme) == "'prefer-dark'":
        ui_dark_theme_button.set_active(True)
    else:
        ui_light_theme_button.set_active(True)

    ui_light_theme_button.connect("toggled", fun_change_theme, 'Adwaita')
    ui_dark_theme_button.connect("toggled", fun_change_theme, 'Adwaita-dark')

    ui_theme_box = Ptk.Box(
        valign="center",
        homogeneous=True,
        spacing=23,
        children=[ui_light_theme_box,ui_dark_theme_box],
    )
    return ui_theme_box
