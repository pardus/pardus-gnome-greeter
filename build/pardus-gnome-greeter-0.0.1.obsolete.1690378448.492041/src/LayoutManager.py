import gi
import os
import json
import subprocess


from gi.repository import Gio, GLib
from libpardus import Ptk
from utils import (
    get_current_theme,
    get_layout_name,
    set_layout_name,
    apply_layout_config,
    dconf_set,
)


arcmenu = "arcmenu@arcmenu.com"
dashtopanel = "dash-to-panel@jderose9.github.com"
dashtodock = "dash-to-dock@micxgx.gmail.com"


layouts = {}

with open(
    os.path.dirname(os.path.abspath(__file__)) + "/../data/layout_config.json"
) as file_content:
    layouts = json.loads(file_content.read())


class LayoutManager:
    def get_layout():
        schema = "org.pardus.pardus-gnome-greeter"
        schema_key = "layout-name"
        return str(Ptk.utils.gsettings_get(schema, schema_key))[1:-1]

    def set_layout(toggle_button):
        layout_name = toggle_button.get_name()
        extensions_schema = "org.gnome.shell"
        enabled_extensions_key = "enabled-extensions"
        disabled_extensions_key = "disabled-extensions"

        enabled_extensions = Ptk.utils.gsettings_get(
            extensions_schema, enabled_extensions_key
        )
        disabled_extensions = Ptk.utils.gsettings_get(
            extensions_schema, disabled_extensions_key
        )

        new_enabled_extensions = list(enabled_extensions.unpack())
        new_disabled_extensions = list(disabled_extensions.unpack())

        if layout_name not in layouts:
            return "There is layout named %s" % layout_name

        if "enable" in layouts[layout_name]:
            for extension in layouts[layout_name]["enable"]:
                if extension not in new_enabled_extensions:
                    new_enabled_extensions.append(extension)
                if extension in new_disabled_extensions:
                    new_disabled_extensions.remove(extension)

        if "disable" in layouts[layout_name]:
            for extension in layouts[layout_name]["disable"]:
                if extension not in new_disabled_extensions:
                    new_disabled_extensions.append(extension)
                if extension in new_enabled_extensions:
                    new_enabled_extensions.remove(extension)

        new_enabled_variant = GLib.Variant.new_strv(new_enabled_extensions)
        new_disabled_variant = GLib.Variant.new_strv(new_disabled_extensions)

        Ptk.utils.gsettings_set(
            extensions_schema, enabled_extensions_key, new_enabled_variant
        )
        Ptk.utils.gsettings_set(
            extensions_schema, disabled_extensions_key, new_disabled_variant
        )

        if "config" in layouts[layout_name]:
            for conf in layouts[layout_name]["config"]:
                escape_conf = conf
                # dont directly give conf as parameter to apply_config function.
                # otherwise escape characters wont be rendered correctly
                dconf_set(conf["path"], conf["value"])

        state = toggle_button.get_active()
        layout_name = None
        if state:
            layout_name = toggle_button.get_name()
            set_layout_name(layout_name)
