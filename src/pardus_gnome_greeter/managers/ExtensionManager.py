import json
import os
from gi.repository import Gio, GLib

class ExtensionManager:
    def __init__(self, extensions_file="data/json/extensions.json"):
        self.extensions_file = extensions_file
        self.extensions = self._load_extensions()
        self.shell_settings = Gio.Settings.new("org.gnome.shell")
        
    def _load_extensions(self):
        """Load extensions from JSON file"""
        try:
            with open(self.extensions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading extensions: {e}")
            return []
    
    def get_extensions(self):
        """Get all extensions"""
        return self.extensions
    
    def get_enabled_extensions(self):
        """Get currently enabled extensions"""
        try:
            return list(self.shell_settings.get_strv("enabled-extensions"))
        except Exception as e:
            print(f"Error getting enabled extensions: {e}")
            return []
    
    def is_extension_enabled(self, extension_id):
        """Check if an extension is enabled"""
        enabled_extensions = self.get_enabled_extensions()
        return extension_id in enabled_extensions
    
    def enable_extension(self, extension_id):
        """Enable an extension"""
        try:
            enabled_extensions = self.get_enabled_extensions()
            if extension_id not in enabled_extensions:
                enabled_extensions.append(extension_id)
                self.shell_settings.set_strv("enabled-extensions", enabled_extensions)
                print(f"Enabled extension: {extension_id}")
                return True
        except Exception as e:
            print(f"Error enabling extension {extension_id}: {e}")
        return False
    
    def disable_extension(self, extension_id):
        """Disable an extension"""
        try:
            enabled_extensions = self.get_enabled_extensions()
            if extension_id in enabled_extensions:
                enabled_extensions.remove(extension_id)
                self.shell_settings.set_strv("enabled-extensions", enabled_extensions)
                print(f"Disabled extension: {extension_id}")
                return True
        except Exception as e:
            print(f"Error disabling extension {extension_id}: {e}")
        return False
    
    def toggle_extension(self, extension_id):
        """Toggle extension state"""
        if self.is_extension_enabled(extension_id):
            return self.disable_extension(extension_id)
        else:
            return self.enable_extension(extension_id) 

    def is_extension_installed(self, extension_id):
        # Check user and system extension directories
        user_dir = os.path.expanduser("~/.local/share/gnome-shell/extensions")
        system_dir = "/usr/share/gnome-shell/extensions"
        for base in [user_dir, system_dir]:
            if os.path.isdir(base):
                for ext in os.listdir(base):
                    if ext == extension_id:
                        return True
        return False 