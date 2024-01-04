import os
import locale
import gi
import sys

sys.path.insert(0, "../")
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from ExtensionManager import ExtensionManager
from libpardus import Ptk
from locale import gettext as _

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)
schema = "org.gnome.shell.extensions.date-menu-formatter"


def fun_create():
    lbl_warn = Ptk.Label(
        label="This config only works if Dash to Panel is enabled", xalign=0.5
    )
    time_txt = "10:00"
    date_txt = "01.01.2023"

    ui_time_button = Ptk.Button(vexpand=True)
    ui_time_button.connect("clicked", change_format, ui_time_button, "time")
    ui_time_button.set_child(Ptk.Label(label=time_txt, yalign=0.5))

    ui_date_box = Ptk.Box(
        orientation="vertical",
        children=[
            Ptk.Label(label=time_txt, xalign=0.5, hexpand=True),
            Ptk.Label(label=date_txt, xalign=0.5, yalign=0.5),
        ],
    )

    ui_date_button = Ptk.Button()
    ui_date_button.connect("clicked", change_format, ui_date_button, "date")
    ui_date_button.set_child(ui_date_box)
    ui_datetime_label = Ptk.Label(label="Date / Time Format")
    ui_datetime_button_box = Ptk.Box(
        hexpand=True,
        halign="end",
        spacing=13,
        children=[ui_time_button, ui_date_button],
    )

    ui_datetime_box = Ptk.Box(
        hexpand=True,
        margin_top=13,
        children=[ui_datetime_label, ui_datetime_button_box],
    )

    ui_fontsize_label = Ptk.Label(label="Font Size", yalign=0.5, vexpand=True)
    ui_fontsize_spinbutton = Gtk.SpinButton.new_with_range(0, 100, 1)
    ui_fontsize_spinbutton.connect(
        "value-changed", on_f_size_change, ui_fontsize_spinbutton
    )
    ui_fontsize_spinbutton.set_value(12)
    ui_fontsize_sb_box = Ptk.Box(
        hexpand=True,
        halign="end",
        spacing=13,
        children=[ui_fontsize_spinbutton],
    )

    ui_font_box = Ptk.Box(
        hexpand=True,
        margin_top=13,
        children=[ui_fontsize_label, ui_fontsize_sb_box],
    )

    ui_seconds_label = Ptk.Label(label="Show Seconds", yalign=0.5, vexpand=True)
    ui_seconds_switch = Gtk.Switch()
    ui_seconds_switch.connect("state-set", change_sec, ui_seconds_switch)
    ui_fontsize_sb_box = Ptk.Box(
        hexpand=True,
        halign="end",
        spacing=13,
        children=[ui_seconds_switch],
    )

    ui_seconds_box = Ptk.Box(
        hexpand=True,
        margin_top=13,
        children=[ui_seconds_label, ui_fontsize_sb_box],
    )

    box = Ptk.Box(
        orientation="vertical",
        hexpand=True,
        vexpand=True,
        margin_top=23,
        margin_end=23,
        margin_start=23,
        margin_bottom=23,
        children=[lbl_warn, ui_seconds_box, ui_font_box, ui_datetime_box],
    )

    enabled_ext = ExtensionManager.get_extensions("enabled-extensions")
    clock_ext = "date-menu-formatter@marcinjakubowski.github.com"
    if clock_ext not in enabled_ext:
        ui_date_button.set_sensitive(False)
        ui_time_button.set_sensitive(False)
        ui_fontsize_spinbutton.set_sensitive(False)
        ui_seconds_switch.set_sensitive(False)
    return box


def change_sec(self, state, switch):
    key = "pattern"
    res = str(Ptk.utils.gsettings_get(schema, key))[1:-1]
    new_val_arr = res.split("HH:MM")
    if "HH:MM" in new_val_arr:
        new_val_arr.insert(1, ":ss")
    print(new_val_arr)
    new_val = "".join(new_val_arr)
    Ptk.utils.gsettings_set(schema, key, new_val)

    pass


def on_f_size_change(self, button):
    size = int(button.get_value())
    change_f_size(size)


def change_f_size(size: int):
    key = "font-size"
    Ptk.utils.gsettings_set(schema, key, size)


def change_format(self, button, f_type):
    types = {"time": "HH:MM", "date": "HH:MM\\ndd:MM:YYYY"}
    key = "pattern"
    Ptk.utils.gsettings_set(schema, key, types[f_type])
