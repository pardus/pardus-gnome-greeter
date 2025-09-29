import json
import os
from gi.repository import Gio, GLib

# Import ExtensionManager
from .ExtensionManager import ExtensionManager
from .settings import app_settings, SettingsManager

class LayoutManager:
    def __init__(self, config_path="/tr/org/pardus/pardus-gnome-greeter/json/layout_config.json"):
        self.config_path = config_path
        self.layouts = self._load_layouts()
        self.dbus_proxy = self._get_dbus_proxy()
        
        # Initialize ExtensionManager
        self.extension_manager = ExtensionManager()
        
        self.all_managed_extensions = self._get_all_managed_extensions()
        self.all_managed_settings = self._get_all_managed_settings()
        
    def get_available_layouts(self):
        """Return list of available layout names"""
        return list(self.layouts.keys())
    
    def get_layout_info(self, layout_name):
        """Get layout information"""
        return self.layouts.get(layout_name, {})

    def _load_layouts(self):
        try:
            file = Gio.File.new_for_uri(f'resource://{self.config_path}')
            data = file.load_contents(None)[1]
            json_data = data.decode('utf-8')
            return json.loads(json_data)
        except Exception as e:
            raise FileNotFoundError(f"Layout configuration not found in GResource at: {self.config_path}\n{e}")

    def _get_dbus_proxy(self):
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            proxy = Gio.DBusProxy.new_sync(
                bus,
                Gio.DBusProxyFlags.NONE,
                None,
                'org.gnome.Shell',
                '/org/gnome/Shell',
                'org.gnome.Shell.Extensions',
                None
            )
            return proxy
        except GLib.Error as e:
            print(f"Failed to create DBus proxy: {e.message}")
            return None

    def _get_all_managed_extensions(self):
        all_extensions = set()
        for layout_data in self.layouts.values():
            for ext in layout_data.get("enable", []):
                all_extensions.add(ext)
            for ext in layout_data.get("disable", []):
                all_extensions.add(ext)
        return list(all_extensions)

    def _get_all_managed_settings(self):
        all_settings = set()
        for layout_data in self.layouts.values():
            for config in layout_data.get("config", []):
                path = config.get("path")
                if not path:
                    continue
                
                parts = path.split('/')
                if len(parts) > 2:
                    schema_id = '.'.join(parts[1:-1])
                    key = parts[-1]
                    all_settings.add((schema_id, key))
        return list(all_settings)

    def _set_gsetting(self, schema_id, key, value, value_type=None):
        try:
            # Use the generic SettingsManager for dynamic schemas
            settings_manager = SettingsManager(schema_id)
            settings_manager.set(key, value)
            print(f"SUCCESS: Set {schema_id} [{key}] to {value} (Type: {type(value).__name__})")

        except GLib.Error as e:
            print(f"ERROR: Failed to set GSetting {schema_id} [{key}]: {e.message}")
        except Exception as e:
            print(f"UNEXPECTED ERROR: Could not set gsetting {schema_id} [{key}]: {e}")


    def _reset_to_defaults(self):
        print("--- Starting Reset to Defaults ---")
        
        # 1. Reset all GSettings for every schema we manage.
        # This is more robust than resetting individual keys, as it clears ALL settings
        # for a schema, preventing state from leaking between layouts.
        # We do this *before* disabling extensions to ensure their schemas are available.
        unique_schemas = {schema_id for schema_id, key in self.all_managed_settings}
        for schema_id in unique_schemas:
            try:
                settings = Gio.Settings.new(schema_id)
                print(f"--- Resetting all keys for schema: {schema_id} ---")
                all_keys = settings.list_keys()
                for key in all_keys:
                    if settings.is_writable(key):
                        settings.reset(key)
                print(f"SUCCESS: Completed reset for schema {schema_id}")
            except Exception as e:
                print(f"Warning: Failed to reset schema {schema_id}. It might not be installed. Error: {e}")

        # 2. Disable all known extensions to ensure a clean slate for the new layout.
        for ext_uuid in self.all_managed_extensions:
            try:
                self.extension_manager.disable_extension(ext_uuid)
                print(f"SUCCESS: Disabled extension {ext_uuid}")
            except Exception as e:
                # Ignore errors, extension might already be disabled
                print(f"Warning: Failed to disable extension {ext_uuid}: {e}")
                pass
        
        print("--- Finished Reset ---")

    def apply_layout(self, layout_name):
        layout_data = self.layouts.get(layout_name)
        if not layout_data:
            print(f"ERROR: Layout '{layout_name}' not found in configuration.")
            return

        print(f"--- Applying layout: {layout_name} ---")

        # 1. Reset everything to a known default state
        self._reset_to_defaults()

        # 2. Apply the new configuration
        # Enable extensions
        for ext_uuid in layout_data.get("enable", []):
            try:
                self.extension_manager.enable_extension(ext_uuid)
                print(f"SUCCESS: Enabled extension {ext_uuid}")
            except Exception as e:
                print(f"ERROR: Failed to enable extension {ext_uuid}: {e}")
        
        # Disable extensions (for this specific layout)
        for ext_uuid in layout_data.get("disable", []):
            try:
                self.extension_manager.disable_extension(ext_uuid)
                print(f"SUCCESS: Disabled extension {ext_uuid}")
            except Exception as e:
                # Ignore, might already be disabled from reset phase
                print(f"Warning: Failed to disable extension {ext_uuid}: {e}")
                pass
        
        # Apply gsettings configurations
        for config in layout_data.get("config", []):
            path = config.get("path")
            value = config.get("value")
            value_type = config.get("type")

            if not path or value is None:
                continue
            
            parts = path.split('/')
            if len(parts) > 2:
                schema_id = ".".join(parts[1:-1])
                key = parts[-1]
                self._set_gsetting(schema_id, key, value, value_type)
        
        print(f"--- Finished applying layout: {layout_name} ---")


# Example usage (for testing purposes)
if __name__ == '__main__':
    # This assumes you run the script from the root of the project directory
    # For example: python3 src/pardus_gnome_greeter/managers/GnomeLayoutManager.py
    try:
        # A simple argument parser to apply a layout from the command line
        import argparse
        import sys
        parser = argparse.ArgumentParser(description="Apply a GNOME Shell layout.")
        parser.add_argument("-a", "--apply", metavar="LAYOUT", help="Apply the specified layout and exit.")
        args = parser.parse_args()

        manager = LayoutManager(config_path="/tr/org/pardus/pardus-gnome-greeter/json/layout_config.json")
        
        if args.apply:
            if args.apply in manager.layouts:
                print(f"Applying layout '{args.apply}' from command line...")
                manager.apply_layout(args.apply)
                print("Done.")
            else:
                print(f"Error: Layout '{args.apply}' not found.")
                print("Available layouts:", list(manager.layouts.keys()))
            sys.exit(0)

        # --- Default interactive test script ---
        print("\nAvailable layouts:", list(manager.layouts.keys()))
        
        layouts_to_test = ['gnome', 'mac', 'ubuntu', '10', 'xp', 'pardus']
        delay = 10  # seconds between each layout change

        for i, layout_name in enumerate(layouts_to_test):
            timeout = 5 + (i * delay)
            print(f"\nApplying '{layout_name}' layout in {timeout} seconds...")
            GLib.timeout_add_seconds(timeout, lambda name=layout_name: manager.apply_layout(name))

        # A main loop is needed for DBus calls to be processed
        loop = GLib.MainLoop()
        print("\nRunning test... Press Ctrl+C to exit after a few seconds.")
        # Exit after all tests are done
        total_duration = 5 + (len(layouts_to_test) * delay)
        GLib.timeout_add_seconds(total_duration, loop.quit)
        loop.run()

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 