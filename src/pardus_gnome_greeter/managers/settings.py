from gi.repository import Gio, GLib

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
            variant = self.settings.get_value(key)
            # Create a new GLib.Variant with the correct type
            if variant.is_of_type(GLib.VariantType.new('b')):
                new_variant = GLib.Variant('b', bool(value))
            elif variant.is_of_type(GLib.VariantType.new('i')) or variant.is_of_type(GLib.VariantType.new('n')) or variant.is_of_type(GLib.VariantType.new('q')):
                new_variant = GLib.Variant('i', int(value))
            elif variant.is_of_type(GLib.VariantType.new('d')):
                new_variant = GLib.Variant('d', float(value))
            else: # Default to string
                new_variant = GLib.Variant('s', str(value))
            
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