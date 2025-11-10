import json
import os
import dbus
from gi.repository import Gio, GLib

class ExtensionManager:
    def __init__(self, extensions_file="/tr/org/pardus/pardus-gnome-greeter/json/extensions.json"):
        self.extensions_file = extensions_file
        self.extensions = self._load_extensions()
        self.dbus_service = None
        try:
            bus = dbus.SessionBus()
            self.dbus_service = bus.get_object('org.gnome.Shell.Extensions', "/org/gnome/Shell/Extensions")
        except Exception as e:
            print(f"Could not connect to dbus service: {e}")
        
    def _load_extensions(self):
        """Load extensions from JSON file in GResource with fallback to filesystem"""
        # Try GResource first
        try:
            file = Gio.File.new_for_uri(f'resource://{self.extensions_file}')
            success, data, _ = file.load_contents(None)
            if success:
                json_data = data.decode('utf-8')
                return json.loads(json_data)
        except Exception as e:
            pass  # Fall through to filesystem fallback
        
        # Fallback: Try to load from filesystem
        try:
            filename = os.path.basename(self.extensions_file)
            fallback_paths = [
                f"/usr/share/pardus-gnome-greeter/json/{filename}",
                f"/usr/local/share/pardus-gnome-greeter/json/{filename}",
            ]
            
            for fallback_path in fallback_paths:
                if os.path.exists(fallback_path):
                    with open(fallback_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            print(f"Warning: Could not load extensions from GResource ({self.extensions_file}) or filesystem")
            return []
        except Exception as e:
            print(f"Error loading extensions: {e}")
            return []
    
    def get_extensions(self):
        """Get all extensions"""
        return self.extensions
    
    def get_enabled_extensions(self):
        """Get currently enabled extensions"""
        if not self.dbus_service:
            return []
        
        enabled_extensions = []
        try:
            extensions = self.dbus_service.ListExtensions(dbus_interface='org.gnome.Shell.Extensions')
            for ext_id, ext_info in extensions.items():
                if 'state' in ext_info and ext_info['state'] == 1:
                    enabled_extensions.append(ext_id)
        except Exception as e:
            print(f"Failed to get enabled extensions via D-Bus: {e}")
        return enabled_extensions

    def is_extension_enabled(self, extension_id):
        """Check if an extension is enabled"""
        if not self.dbus_service:
            return False
        try:
            extensions = self.dbus_service.ListExtensions(dbus_interface='org.gnome.Shell.Extensions')
            if extension_id in extensions:
                ext_info = extensions[extension_id]
                return 'state' in ext_info and ext_info['state'] == 1
        except Exception as e:
            print(f"Failed to check if extension is enabled via D-Bus: {e}")
        return False
    
    def enable_extension(self, extension_id):
        """Enable an extension"""
        if not self.dbus_service:
            return False
        try:
            self.dbus_service.EnableExtension(extension_id, dbus_interface='org.gnome.Shell.Extensions')
            print(f"Enabled extension: {extension_id}")
            return True
        except Exception as e:
            print(f"Error enabling extension {extension_id}: {e}")
        return False
    
    def disable_extension(self, extension_id):
        """Disable an extension"""
        if not self.dbus_service:
            return False
        try:
            self.dbus_service.DisableExtension(extension_id, dbus_interface='org.gnome.Shell.Extensions')
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

    def get_sorted_extensions(self):
        """Get extensions sorted by installation status (installed first)"""
        extensions = self.get_extensions()
        installed = []
        not_installed = []
        
        for extension in extensions:
            if self.is_extension_installed(extension['id']):
                installed.append(extension)
            else:
                not_installed.append(extension)
        
        return installed + not_installed 