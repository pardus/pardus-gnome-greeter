import os
import gi
import apt
import sys

sys.path.append("../")
import json
import locale
import utils
from pathlib import Path
from libpardus import Ptk
from utils import get_color_scheme, get_gtk_theme, get_icon_theme

import WallpaperManager

from locale import gettext as _

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)

color_scheme = str(get_color_scheme())[1:-1]
gtk_theme = str(get_gtk_theme())[1:-1]
icon_theme = str(get_icon_theme())[1:-1]


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

    themes = [
        {
            "label": _("Dark Theme"),
            "theme": "adw-gtk3-dark",
            "name": "prefer-dark",
            "image": cur_dir + "/../data/assets/theme-dark.png",
            "toggle_button": None,
        },
        {
            "label": _("Light Theme"),
            "theme": "adw-gtk3",
            "name": "default",
            "image": cur_dir + "/../data/assets/theme-light.png",
            "toggle_button": None,
        },
    ]
    special_theme_options = fun_check_special_themes()

    ui_standart_theme_box = Ptk.Box(
        valign="center",
        homogeneous=True,
        spacing=23,
    )
    ui_special_theme_box = Ptk.Box(
        valign="center",
        homogeneous=True,
        spacing=23,
    )
    ui_theme_box = Ptk.Box(
        orientation="vertical",
        valign="center",
        homogeneous=True,
        spacing=23,
        children=[ui_special_theme_box, ui_standart_theme_box],
    )
    for index, theme in enumerate(themes):
        in_use = is_theme_in_use(theme)
        button = fun_create_theme_button(themes, theme, special_theme_options)
        button.connect("toggled", fun_change_theme, theme["theme"])
        button.set_active(in_use)
        theme["toggle_button"] = button
        ui_standart_theme_box.append(button)

        if special_theme_options:
            spec_theme = special_theme_options[index]
            spec_in_use = is_theme_in_use(spec_theme)
            spec_btn = fun_create_theme_button(
                themes,
                spec_theme,
                special_theme_options,
            )
            spec_btn.connect(
                "toggled",
                fun_change_theme,
                spec_theme["theme"],
                spec_theme["wallpaper"],
                spec_theme["icon"],
            )
            spec_btn.set_active(spec_in_use)
            special_theme_options[index]["toggle_button"] = spec_btn
            ui_special_theme_box.append(spec_btn)

    return ui_theme_box


def fun_change_theme(toggle_button, theme_name, wallpaper=None, icon_theme=None):
    def_wp_light = "/usr/share/backgrounds/pardus23-0_default-light.svg"
    def_wp_dark = "/usr/share/backgrounds/pardus23-0_default-dark.svg"
    schema = "org.gnome.desktop.interface"
    key = "color-scheme"
    theme_key = "gtk-theme"
    icon_theme_key = "icon-theme"

    name = toggle_button.get_name()
    state = toggle_button.get_active()
    if state:
        Ptk.utils.gsettings_set(schema, key, name)
        Ptk.utils.gsettings_set(schema, theme_key, theme_name)
    if wallpaper:
        WallpaperManager.change_wallpaper(wallpaper)
    else:
        if name == "default":
            WallpaperManager.change_wallpaper(def_wp_light)
        elif name == "prefer-dark":
            WallpaperManager.change_wallpaper(def_wp_dark)
    if icon_theme:
        Ptk.utils.gsettings_set(schema, icon_theme_key, icon_theme)


def fun_check_special_themes():
    themes = ["pardus-yuzyil"]
    pkg_found = False

    home_path = Path.home()
    lang = os.getenv("LANG")[0:2]
    desktop_env = utils.desktop_env()
    user_theme_json = (
        f"{home_path}/.config/pardus/pardus-special-theme/special-theme.json"
    )
    user_theme_json_ok = os.path.isfile(user_theme_json)

    sys_theme_json = "/usr/share/pardus/pardus-special-theme/special-theme.json"
    sys_theme_json_ok = os.path.isfile(sys_theme_json)
    special_theme_json = None
    for theme in themes:
        try:
            cache = apt.Cache()
            if cache[theme].is_installed:
                if user_theme_json_ok:
                    special_theme_json = json.load(open(user_theme_json))
                elif not user_theme_json and sys_theme_json_ok:
                    special_theme_json = json.load(open(sys_theme_json))
                else:
                    print("There is no json files")
                    return
        except Exception as e:
            print(e)

    variants = ["dark", "light"]
    special_theme_options = []
    for var in variants:
        name = special_theme_json[var]["name"].replace("@@desktop@@", desktop_env)
        label = {
            "tr": special_theme_json[var]["pretty_tr"],
            "en": special_theme_json[var]["pretty_en"],
        }

        bg = special_theme_json[var]["background"]
        img = special_theme_json[var]["image"]

        new_theme = {
            "label": _(label[lang]),
            "icon": name,
            "name": None,
            "image": img,
            "toggle_button": None,
            "wallpaper": bg,
        }
        if var == "dark":
            new_theme["name"] = "prefer-dark"
            new_theme["theme"] = "adw-gtk3-dark"

        else:
            new_theme["name"] = "default"
            new_theme["theme"] = "adw-gtk3"
        special_theme_options.append(new_theme)
    return special_theme_options


def fun_create_theme_button(themes, theme, special=None):
    markup = f"<b>{theme['label']}</b>"
    label = Ptk.Label(markup=markup, hexpand=True, halign="center")
    img_size = 300
    if special:
        img_size = 233
    image = Ptk.Image(file=theme["image"], pixel_size=img_size)
    box = Ptk.Box(
        orientation="vertical", spacing=8, halign="center", children=[image, label]
    )

    toggle = Ptk.ToggleButton(
        valign="center",
        halign="center",
        group=themes[0]["toggle_button"],
        name=theme["name"],
        child=box,
    )
    return toggle


def is_theme_in_use(theme):
    stat = color_scheme == theme["name"] and gtk_theme == theme["theme"]

    if "icon" in theme.keys():
        return stat and icon_theme == theme["icon"]
    else:
        return stat
