from gi.repository import Gio, GLib

class SettingsManager:
    def __init__(self, schema_id):
        self.settings = Gio.Settings.new(schema_id)

    def get(self, key):
        """Gets a setting value."""
        return self.settings.get_value(key).unpack()

    def set(self, key, value):
        """Sets a setting value."""
        variant = self.settings.get_value(key)
        # Create a new GLib.Variant with the correct type
        if variant.is_of_type(GLib.VariantType.new('b')):
            new_variant = GLib.Variant('b', value)
        elif variant.is_of_type(GLib.VariantType.new('i')) or variant.is_of_type(GLib.VariantType.new('n')) or variant.is_of_type(GLib.VariantType.new('q')):
            new_variant = GLib.Variant('i', value)
        elif variant.is_of_type(GLib.VariantType.new('d')):
             new_variant = GLib.Variant('d', value)
        else: # Default to string
            new_variant = GLib.Variant('s', value)
        self.settings.set_value(key, new_variant)


# Application specific settings
app_settings = SettingsManager("tr.org.pardus.pardus-gnome-greeter")

# GNOME Desktop Interface settings (for themes, fonts, etc.)
theme_settings = SettingsManager("org.gnome.desktop.interface")

# GNOME Shell settings
shell_settings = SettingsManager("org.gnome.shell")

# GNOME Desktop Background settings
background_settings = SettingsManager("org.gnome.desktop.background")