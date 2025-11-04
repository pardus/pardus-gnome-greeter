from gi.repository import Gio, GLib
import json

class SettingsManager:
    def __init__(self, schema_id):
        self.settings = Gio.Settings.new(schema_id)

    def get(self, key):
        """Gets a setting value."""
        return self.settings.get_value(key).unpack()

    def get_strv(self, key):
        """Gets a string array value."""
        return self.settings.get_strv(key)

    def set(self, key, value):
        """Sets a setting value."""
        try:
            # Get the expected GVariant type string directly from the original variant.
            # This is the most compatible and direct method.
            original_variant = self.settings.get_value(key)
            type_string = original_variant.get_type_string()

            # Create a new GLib.Variant with the correct type signature and value.
            new_variant = GLib.Variant(type_string, value)

            return self.settings.set_value(key, new_variant)
        except Exception as e:
            print(f"Error setting {key} = {value}: {e}")
            return False

    def set_strv(self, key, value):
        """Sets a string array value."""
        try:
            return self.settings.set_strv(key, value)
        except Exception as e:
            print(f"Error setting strv {key} = {value}: {e}")
            return False


# Application specific settings
app_settings = SettingsManager("tr.org.pardus.pardus-gnome-greeter")

# GNOME Desktop Interface settings (for themes, fonts, etc.)
theme_settings = SettingsManager("org.gnome.desktop.interface")

# GNOME Shell settings
shell_settings = SettingsManager("org.gnome.shell")

# GNOME Desktop Background settings
background_settings = SettingsManager("org.gnome.desktop.background")