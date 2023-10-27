import gi

from libpardus import Ptk
from gi.repository import GLib

gi.require_version("Gtk", "4.0")


class ExtensionManager:
    def extension_operations(ext_type, ext_id):
        schema = "org.gnome.shell"
        enabled_key = "enabled-extensions"
        disabled_key = "disabled-extensions"

        enabled_extensions = list(Ptk.utils.gsettings_get(schema, enabled_key))
        disabled_extensions = list(Ptk.utils.gsettings_get(schema, disabled_key))

        if ext_type == "enable":
            if ext_id in disabled_extensions:
                disabled_extensions.remove(ext_id)
            enabled_extensions.append(ext_id)
        else:
            if ext_id in enabled_extensions:
                enabled_extensions.remove(ext_id)
            disabled_extensions.append(ext_id)

        glist_enabled_extensions = GLib.Variant.new_strv(enabled_extensions)
        glist_disabled_extensions = GLib.Variant.new_strv(disabled_extensions)
        Ptk.utils.gsettings_set(schema, enabled_key, glist_enabled_extensions)
        Ptk.utils.gsettings_set(schema, disabled_key, glist_disabled_extensions)

    def get_extensions(ext_type: str):
        schema = "org.gnome.shell"
        types = ["enabled-extensions", "disabled-extensions"]
        extensions = []
        if ext_type == "all":
            for ext_type in types:
                extensions += Ptk.utils.gsettings_get(schema, ext_type)
        else:
            extensions = Ptk.utils.gsettings_get(schema, ext_type)
        return extensions
