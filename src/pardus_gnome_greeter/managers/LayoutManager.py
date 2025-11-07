import json
import os
from gi.repository import Gio, GLib

# Import ExtensionManager
from .ExtensionManager import ExtensionManager
from .settings import app_settings, SettingsManager

class LayoutManager:
    def __init__(self, config_path="/tr/org/pardus/pardus-gnome-greeter/json/layout_config.json"):
        self.config_path = config_path
        
        try:
            config_data = self._load_layouts()
            self.global_resets = config_data.pop("global_resets", [])
            self.always_enabled_extensions = config_data.pop("always_enabled_extensions", [])
            self.layouts = config_data
        except Exception as e:
            print(f"Warning: Could not initialize LayoutManager: {e}")
            self.layouts = {}
            self.global_resets = []

        # For sequential layout application
        self.task_queue = []
        self.is_applying_layout = False
        
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

    def get_current_layout(self):
        """
        Detects the current layout by first checking the saved gsetting,
        and then falling back to checking which extensions are enabled.
        Returns the name of the current layout, or 'gnome' as a fallback.
        """
        try:
            # First, try to get the layout from GSettings
            saved_layout = app_settings.get("layout-name")
            if saved_layout and saved_layout in self.layouts:
                print(f"Detected current layout from GSettings: {saved_layout}")
                return saved_layout
        except Exception as e:
            print(f"Could not read saved layout from GSettings, falling back to extension check. Error: {e}")

        # Fallback to extension-based detection if GSetting is not available
        try:
            enabled_extensions = self.extension_manager.get_enabled_extensions()
            enabled_set = set(enabled_extensions)

            # Check layouts in a specific order for priority
            layout_priority = ['pardus', 'xp', '10', 'ubuntu', 'mac', 'gnome']

            for layout_name in layout_priority:
                layout_info = self.layouts.get(layout_name)
                if not layout_info:
                    continue

                # Get the extensions that this layout enables
                required_extensions = set(layout_info.get("enable", []))

                # If all required extensions for this layout are enabled, we have a match
                if required_extensions.issubset(enabled_set):
                    # A simple check for disabled extensions to resolve ambiguity
                    # For example, both 'mac' and 'ubuntu' might use 'dash-to-dock'
                    # We can refine this by checking a key setting if needed
                    disabled_extensions = set(layout_info.get("disable", []))
                    if not disabled_extensions.intersection(enabled_set):
                        print(f"Detected current layout: {layout_name}")
                        return layout_name
            
            # Fallback to 'gnome' if no other layout matches
            print("Could not detect a specific layout, falling back to 'gnome'")
            return 'gnome'

        except Exception as e:
            print(f"Error detecting current layout by extensions: {e}")
            return 'gnome'  # Fallback in case of error

    def _load_layouts(self):
        try:
            file = Gio.File.new_for_uri(f'resource://{self.config_path}')
            success, data, _ = file.load_contents(None)
            if not success:
                raise FileNotFoundError(f"Failed to load layout config from GResource: {self.config_path}")
            json_data = data.decode('utf-8')
            return json.loads(json_data)
        except Exception as e:
            raise FileNotFoundError(f"Layout configuration not found in GResource at: {self.config_path}\n{e}")

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
                schema_id = config.get("schema")
                key = config.get("key")
                if schema_id and key:
                    all_settings.add((schema_id, key))
        return list(all_settings)

    def _set_gsetting(self, schema_id, key, value, value_type=None):
        try:
            # Check if schema exists before trying to use it to prevent crashes
            schema_source = Gio.SettingsSchemaSource.get_default()
            if not schema_source.lookup(schema_id, True):
                print(f"Warning: Schema '{schema_id}' not found. Skipping setting key '{key}'.")
                return
            
            print(f"DEBUG: Setting {schema_id} [{key}] - value type: {type(value).__name__}, value length: {len(str(value)) if isinstance(value, str) else 'N/A'}")
                
            # Use the generic SettingsManager for dynamic schemas
            settings_manager = SettingsManager(schema_id)
            success = settings_manager.set(key, value)
            
            if success:
                print(f"SUCCESS: Set {schema_id} [{key}] to {value} (Type: {type(value).__name__})")
            else:
                print(f"ERROR: Failed to set {schema_id} [{key}] - SettingsManager.set returned False")

        except GLib.Error as e:
            print(f"ERROR: Failed to set GSetting {schema_id} [{key}]: {e.message}")
        except Exception as e:
            print(f"UNEXPECTED ERROR: Could not set gsetting {schema_id} [{key}]: {e}")


    def _task_reset_settings(self):
        """Resets all managed GSettings to their default values."""
        if self.global_resets:
            print("--- Applying Global Resets ---")
            for reset_config in self.global_resets:
                schema_id, key, value, value_type = (
                    reset_config.get("schema"),
                    reset_config.get("key"),
                    reset_config.get("value"),
                    reset_config.get("type"),
                )
                if schema_id and key and value is not None:
                    self._set_gsetting(schema_id, key, value, value_type)

        unique_schemas = {schema_id for schema_id, key in self.all_managed_settings}
        for schema_id in unique_schemas:
            try:
                # Check if schema exists before trying to use it to prevent crashes
                schema_source = Gio.SettingsSchemaSource.get_default()
                if not schema_source.lookup(schema_id, True):
                    print(f"Warning: Schema '{schema_id}' not found. Skipping reset for this schema.")
                    continue

                settings = Gio.Settings.new(schema_id)
                print(f"--- Resetting all keys for schema: {schema_id} ---")
                for key in settings.list_keys():
                    if settings.is_writable(key):
                        settings.reset(key)
            except Exception as e:
                print(f"Warning: Failed to reset schema {schema_id}. It might not be installed. Error: {e}")

    def _task_apply_layout_extensions(self, layout_name):
        """Enables and disables extensions specific to the chosen layout."""
        layout_data = self.layouts.get(layout_name, {})
        
        for ext_uuid in layout_data.get("enable", []):
            try:
                self.extension_manager.enable_extension(ext_uuid)
            except Exception as e:
                print(f"ERROR: Failed to enable extension {ext_uuid}: {e}")
        
        for ext_uuid in layout_data.get("disable", []):
            if ext_uuid in self.always_enabled_extensions:
                print(f"INFO: Skipping disable for '{ext_uuid}' as it is marked as always enabled.")
                continue
            try:
                self.extension_manager.disable_extension(ext_uuid)
            except Exception as e:
                print(f"Warning: Failed to disable extension {ext_uuid}: {e}")

    def _task_apply_layout_gsettings(self, layout_name):
        """Applies the GSettings configurations for the chosen layout."""
        layout_data = self.layouts.get(layout_name, {})

        for config in layout_data.get("config", []):
            schema_id, key, value, value_type = (
                config.get("schema"),
                config.get("key"),
                config.get("value"),
                config.get("type"),
            )
            if schema_id and key and value is not None:
                # Debug: value tipini kontrol et
                print(f"DEBUG: Processing config - schema: {schema_id}, key: {key}, value type: {type(value).__name__}, value: {str(value)[:100]}...")
                
                # pipelines key'i için value JSON'da string olarak tutuluyor
                # SettingsManager.set metodunda string'i dict'e çevirip GLib.Variant'a geçiriyoruz
                self._set_gsetting(schema_id, key, value, value_type)
        
        app_settings.set("layout-name", layout_name)
        print(f"SUCCESS: Set layout-name to {layout_name}")

    def _process_next_task(self):
        if not self.task_queue:
            self.is_applying_layout = False
            print("--- Layout application finished successfully ---")
            return False

        task_func, task_args, delay = self.task_queue.pop(0)

        try:
            print(f"--- Running task: {task_func.__name__} ---")
            task_func(*task_args)
        except Exception as e:
            print(f"ERROR: An error occurred in task {task_func.__name__}: {e}")
            self.is_applying_layout = False
            self.task_queue = []
            return False

        if self.task_queue:
            GLib.timeout_add(delay, self._process_next_task)
        else:
            self.is_applying_layout = False
            print("--- Layout application finished successfully ---")

        return False

    def apply_layout(self, layout_name):
        layout_data = self.layouts.get(layout_name)
        if not layout_data:
            print(f"ERROR: Layout '{layout_name}' not found in configuration.")
            return

        if self.is_applying_layout:
            print("WARNING: Another layout application is already in progress. Ignoring request.")
            return

        self.is_applying_layout = True
        print(f"--- Applying layout: {layout_name} ---")

        self.task_queue = [
            (self._task_reset_settings, [], 300),
            (self._task_apply_layout_extensions, [layout_name], 500),
            (self._task_apply_layout_gsettings, [layout_name], 100),
        ]

        self._process_next_task()

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