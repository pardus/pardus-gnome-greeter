import gi
import subprocess

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import GLib, Gio


class Keybindings:
    def get_keybinding(self, schema, key, is_custom):
        if is_custom:
            binding = [self.get_custom_keybinding(key)[1:-1]]
        else:
            settings = Gio.Settings.new(schema)
            binding = settings.get_strv(key)

        while "" in binding:
            binding.remove("")
        if len(binding) > 0:
            for b_index, item in enumerate(binding):
                item = item.split(">")
                for index, string in enumerate(item):
                    if "<" in string:
                        item[index] = string[1:]
                binding[b_index] = item
        return binding

    def get_custom_keybinding(self, key):
        cmd = (
            "dconf read /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/%s/binding"
            % key
        )
        return subprocess.getoutput(cmd)

    def get_keybindings(self):
        cmd = ["gsettings", "list-recursively"]
        return subprocess.getoutput(cmd)

    def set_keybinding(self, schema, key, binding):
        settings = Gio.Settings.new(schema)
        value = GLib.Variant.new_strv([binding])
        settings.set_value(key, value)

    def set_custom_keybinding(self, id, name, binding, command):
        infos = [
            {"key": "name", "value": name},
            {"key": "binding", "value": binding},
            {"key": "command", "value": command},
        ]
        main_schema = "org.gnome.settings-daemon.plugins.media-keys"
        custom_schema_key = "custom-keybindings"

        schema = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"

        path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"

        for info in infos:
            schema_path = schema + ":" + path + id + "/"
            cmd = ["gsettings", "set", schema_path, info["key"], info["value"]]
            response = subprocess.run(cmd)

        settings = Gio.Settings.new(main_schema)
        variant = settings.get_value(custom_schema_key)

        keybinding_list = list(variant.unpack())
        new_key = f"""{path}{id}/"""

        if new_key not in keybinding_list:
            keybinding_list.append(new_key)

        new_variant = GLib.Variant.new_strv(keybinding_list)
        settings.set_value(custom_schema_key, new_variant)
