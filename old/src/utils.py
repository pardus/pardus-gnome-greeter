import gi
import os
import sys
import subprocess

sys.path.append("../")


gi.require_version("Gdk", "4.0")
from gi.repository import Gdk
from libpardus import Ptk


def get_layout_name():
    cmd = "gsettings get org.pardus.pardus-gnome-greeter layout-name"
    result = subprocess.getoutput(cmd)
    return result[1:-1]


def set_layout_name(layout_name: str):
    cmd = (
        "dconf write /org/pardus/pardus-gnome-greeter/layout-name \"'%s'\""
        % layout_name
    )
    return subprocess.getoutput(cmd)


def get_color_scheme():
    return Ptk.utils.gsettings_get("org.gnome.desktop.interface", "color-scheme")


def get_gtk_theme():
    return Ptk.utils.gsettings_get("org.gnome.desktop.interface", "gtk-theme")


def get_icon_theme():
    return Ptk.utils.gsettings_get("org.gnome.desktop.interface", "icon-theme")


def apply_layout_config(config: str):
    return subprocess.getoutput(config)


def get_recommended_scale():
    display_server = Ptk.utils.get_session()
    if display_server == "wayland":
        return 100
    base_scale = 100
    screen_const = 50
    approximate_result = 0
    display = Gdk.Display.get_default()
    monitors = display.get_monitors()

    for monitor in monitors:
        width_mm = monitor.get_width_mm()
        height_mm = monitor.get_height_mm()

        width_px = monitor.get_geometry().width
        height_px = monitor.get_geometry().height

        wdpi = width_mm / width_px
        hdpi = height_mm / height_px

        approximate_result += screen_const / (wdpi + hdpi)
    result = base_scale * 100 / approximate_result * len(monitors)
    if result % 25 > 12.5:
        rounded_result = int(result + (25 - result % 25))
    else:
        rounded_result = int(result - (result % 25))

    if rounded_result < 75:
        return 100
    return rounded_result


def dconf_set(path, value):
    cmd = ["dconf", "write", path, value]
    return subprocess.run(cmd)


def dconf_reset(path):
    response = subprocess.run(["dconf", "reset", "-f", path])
    return response


def desktop_env():
    return os.environ["XDG_CURRENT_DESKTOP"].lower()
