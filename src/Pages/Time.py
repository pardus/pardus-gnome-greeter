import os
import locale
import gi
import sys

sys.path.insert(0, "../")
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from ExtensionManager import ExtensionManager
from libpardus import Ptk
from locale import gettext as _

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)
schema = "org.gnome.shell.extensions.date-menu-formatter"
key = "pattern"
clock_ext = "date-menu-formatter@marcinjakubowski.github.com"
types = {
    "time": "HH:MM",
    "time-sec": "HH:MM:ss",
    "date": "HH:MM\\ndd:MM:YYYY",
    "date-sec": "HH:MM:ss\\ndd:MM:YYYY",
}


class Time:
    def __init__(self) -> None:
        time_txt = "10:00"
        date_txt = "01.01.2023"

        ui_clock_label = Ptk.Label(
            label=_("Enable clock formatting"), yalign=0.5, vexpand=True
        )
        ui_clock_switch = Gtk.Switch()

        enab_exts = ExtensionManager.get_extensions("enabled-extensions")
        state = clock_ext in enab_exts

        ui_clock_switch.set_state(state)

        ui_switch_box = Ptk.Box(hexpand=True, halign="end", children=[ui_clock_switch])
        ui_clock_box = Ptk.Box(
            margin_end=13,
            margin_start=26,
            hexpand=True,
            halign="fill",
            spacing=13,
            children=[ui_clock_label, ui_switch_box],
        )

        ui_time_button = Ptk.Button(vexpand=True)

        ui_time_button.set_child(Ptk.Label(label=time_txt, yalign=0.5))

        ui_date_box = Ptk.Box(
            orientation="vertical",
            children=[
                Ptk.Label(label=time_txt, xalign=0.5, hexpand=True),
                Ptk.Label(label=date_txt, xalign=0.5, yalign=0.5),
            ],
        )

        ui_date_button = Ptk.Button()

        ui_date_button.set_child(ui_date_box)
        ui_datetime_label = Ptk.Label(label=_("Date / Time Format"), yalign=0.5)
        ui_datetime_button_box = Ptk.Box(
            hexpand=True,
            halign="end",
            spacing=13,
            children=[ui_time_button, ui_date_button],
        )

        ui_datetime_box = Ptk.Box(
            margin_start=13,
            margin_end=13,
            hexpand=True,
            margin_top=13,
            children=[ui_datetime_label, ui_datetime_button_box],
        )

        ui_fontsize_label = Ptk.Label(label=_("Font Size"), yalign=0.5, vexpand=True)
        ui_fontsize_spinbutton = Gtk.SpinButton.new_with_range(0, 100, 1)

        f_size = Ptk.utils.gsettings_get(schema, "font-size")
        ui_fontsize_spinbutton.set_value(GLib.Variant.get_int32(f_size))
        ui_fontsize_sb_box = Ptk.Box(
            hexpand=True,
            halign="end",
            spacing=13,
            children=[ui_fontsize_spinbutton],
        )

        ui_font_box = Ptk.Box(
            margin_start=13,
            margin_end=13,
            hexpand=True,
            children=[ui_fontsize_label, ui_fontsize_sb_box],
        )

        ui_seconds_label = Ptk.Label(label=_("Show Seconds"), yalign=0.5, vexpand=True)
        self.ui_seconds_switch = Gtk.Switch()
        ptrn = self.get_pattern()
        if "ss" in str(ptrn):
            self.ui_seconds_switch.set_state(True)

        ui_fontsize_sb_box = Ptk.Box(
            hexpand=True,
            halign="end",
            spacing=13,
            children=[self.ui_seconds_switch],
        )

        ui_seconds_box = Ptk.Box(
            margin_start=13,
            margin_end=13,
            hexpand=True,
            margin_bottom=13,
            children=[ui_seconds_label, ui_fontsize_sb_box],
        )
        self.ui_settings_box = Ptk.Box(
            css=["settings-box", "rounded"],
            orientation="vertical",
            margin_top=13,
            margin_start=13,
            spacing=13,
            children=[
                ui_datetime_box,
                ui_font_box,
                ui_seconds_box,
            ],
        )

        self.ui_settings_box.set_sensitive(state)
        ui_clock_switch.connect("state-set", self.on_ext_change)
        ui_date_button.connect("clicked", self.change_format, "date")
        ui_time_button.connect("clicked", self.change_format, "time")
        ui_fontsize_spinbutton.connect("value-changed", self.on_f_size_change)
        self.ui_seconds_switch.connect("state-set", self.change_sec)
        print("sys sec check", self.sys_sec_check())
        self.box = Ptk.Box(
            orientation="vertical",
            hexpand=True,
            margin_top=23,
            margin_end=23,
            margin_start=23,
            margin_bottom=23,
            children=[
                ui_clock_box,
                self.ui_settings_box,
            ],
        )

    def change_sec(self, switch, state):
        res = str(Ptk.utils.gsettings_get(schema, key))[1:-1]
        if state:
            if "dd:MM:YYYY" in res:
                Ptk.utils.gsettings_set(schema, key, types["date-sec"])
            else:
                Ptk.utils.gsettings_set(schema, key, types["time-sec"])
        if not state:
            print("remove sec")
            if "dd:MM:YYYY" in res:
                Ptk.utils.gsettings_set(schema, key, types["date"])
            else:
                Ptk.utils.gsettings_set(schema, key, types["time"])

    def on_f_size_change(self, button):
        size = int(button.get_value())
        self.change_f_size(size)

    def change_f_size(self, size: int):
        key = "font-size"
        Ptk.utils.gsettings_set(schema, key, size)

    def change_format(self, button, f_type):
        sec_state = self.ui_seconds_switch.get_state()
        sec_type = f"{f_type}-sec"
        print("sec-state", sec_state, sec_type)
        if sec_state:
            self.set_pattern(types[sec_type])
        else:
            self.set_pattern(types[f_type])

    def on_ext_change(self, switch, state):
        if state:
            ExtensionManager.extension_operations("enable", clock_ext)
        else:
            ExtensionManager.extension_operations("disable", clock_ext)

        self.ui_settings_box.set_sensitive(state)

    def get_pattern(self):
        return Ptk.utils.gsettings_get(schema, "pattern")

    def set_pattern(self, type):
        Ptk.utils.gsettings_set(schema, "pattern", type)

    def sys_sec_check(self):
        sys_schema = "org.gnome.desktop.interface"
        sys_key = "clock-show-seconds"
        return bool(Ptk.utils.gsettings_get(sys_schema, sys_key))


def fun_create():
    return Time().box
