
import json
import os
from gi.repository import Gio, GLib

class LayoutManager:
    def __init__(self, config_path="data/json/layout_config.json"):
        self.config_path = config_path
        self.layouts = self._load_layouts()
        self.dbus_proxy = self._get_dbus_proxy()
        
        self.all_managed_extensions = self._get_all_managed_extensions()
        self.all_managed_settings = self._get_all_managed_settings()
        
    def get_available_layouts(self):
        """Return list of available layout names"""
        return list(self.layouts.keys())
    
    def get_layout_info(self, layout_name):
        """Get layout information"""
        return self.layouts.get(layout_name, {})

    def _load_layouts(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Layout configuration not found at: {self.config_path}")
        with open(self.config_path, 'r') as f:
            return json.load(f)

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
            settings = Gio.Settings.new(schema_id)

            # --- Start of new type conversion logic ---
            # Try to intelligently convert the value from JSON to the correct Python type,
            # as GSettings is strict about types.
            
            final_value = value
            
            # 1. Handle booleans explicitly
            if str(value).lower() == 'true':
                final_value = True
            elif str(value).lower() == 'false':
                final_value = False
            
            # 2. Handle numbers (integers and floats)
            # Only try to convert if it's not already a bool
            if not isinstance(final_value, bool):
                try:
                    # Try converting to integer first
                    final_value = int(str(value))
                except (ValueError, TypeError):
                    try:
                        # If int conversion fails, try float
                        final_value = float(str(value))
                    except (ValueError, TypeError):
                        # If all fails, it's a string
                        pass

            # --- End of new type conversion logic ---

            if isinstance(final_value, bool):
                settings.set_boolean(key, final_value)
            elif isinstance(final_value, int):
                settings.set_int(key, final_value)
            elif isinstance(final_value, float):
                settings.set_double(key, final_value)
            else: # Fallback to string for everything else
                # Remove extra quotes from string values if they exist
                final_value_str = str(final_value).strip("'\"")
                settings.set_string(key, final_value_str)
            
            print(f"SUCCESS: Set {schema_id} [{key}] to {final_value} (Type: {type(final_value).__name__})")

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
        if self.dbus_proxy:
            for ext_uuid in self.all_managed_extensions:
                try:
                    self.dbus_proxy.DisableExtension('(s)', ext_uuid)
                    print(f"SUCCESS: Disabled extension {ext_uuid}")
                except GLib.Error as e:
                    # Ignore errors, extension might already be disabled
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
        if not self.dbus_proxy:
            print("ERROR: DBus proxy not available. Cannot manage extensions.")
        else:
            # Enable extensions
            for ext_uuid in layout_data.get("enable", []):
                try:
                    self.dbus_proxy.EnableExtension('(s)', ext_uuid)
                    print(f"SUCCESS: Enabled extension {ext_uuid}")
                except GLib.Error as e:
                    print(f"ERROR: Failed to enable extension {ext_uuid}: {e.message}")
            
            # Disable extensions (for this specific layout)
            for ext_uuid in layout_data.get("disable", []):
                try:
                    self.dbus_proxy.DisableExtension('(s)', ext_uuid)
                    print(f"SUCCESS: Disabled extension {ext_uuid}")
                except GLib.Error as e:
                    # Ignore, might already be disabled from reset phase
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

        manager = LayoutManager(config_path="data/json/layout_config.json")
        
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