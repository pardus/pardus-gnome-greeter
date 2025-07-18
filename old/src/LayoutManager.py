import os
import json


from gi.repository import GLib
from libpardus import Ptk
from utils import set_layout_name, dconf_set, dconf_reset


arcmenu = "/org/gnome/shell/extensions/arcmenu/"
dashtopanel = "/org/gnome/shell/extensions/dash-to-panel/"
dashtodock = "/org/gnome/shell/extensions/dash-to-dock/"

layout_names = [arcmenu, dashtodock, dashtopanel]

layouts = {}

with open(
    os.path.dirname(os.path.abspath(__file__)) + "/../data/layout_config.json"
) as file_content:
    layouts = json.loads(file_content.read())


class LayoutManager:
    def reset_layout():
        for layout in layout_names:
            dconf_reset(layout)

    def get_layout():
        schema = "org.pardus.pardus-gnome-greeter"
        schema_key = "layout-name"
        return str(Ptk.utils.gsettings_get(schema, schema_key))[1:-1]

    def set_layout(toggle_button):
        enable_extensions_schema = "org.gnome.shell"
        enable_extensions_key = "disable-user-extensions"
        Ptk.utils.gsettings_set(
            enable_extensions_schema,
            enable_extensions_key,
            GLib.Variant.new_boolean(False),
        )

        state = toggle_button.get_active()
        layout_name = None
        layout_name = toggle_button.get_name()

        if state:
            set_layout_name(layout_name)
            LayoutManager.reset_layout()
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
                    if "type" in conf.keys() and conf["type"] == "string":
                        lc_value = f"'{conf['value']}'"
                        dconf_set(conf["path"], lc_value)
                    else:
                        dconf_set(conf["path"], conf["value"])
