import json
import re
from gi.repository import Gio

class ShortcutManager:
    def __init__(self, 
                 custom_shortcuts_path="/tr/org/pardus/pardus-gnome-greeter/json/custom_shortcuts.json",
                 standard_shortcuts_path="/tr/org/pardus/pardus-gnome-greeter/json/shortcuts.json"):
        self.custom_shortcuts_path = custom_shortcuts_path
        self.standard_shortcuts_path = standard_shortcuts_path
        self.media_keys_schema_id = "org.gnome.settings-daemon.plugins.media-keys"
        self.custom_binding_schema_id = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"
        self.custom_bindings_key = "custom-keybindings"
        self.media_keys_settings = Gio.Settings.new(self.media_keys_schema_id)

    def _load_json_from_gresource(self, path):
        """Loads a JSON file from the GResource bundle."""
        try:
            file = Gio.File.new_for_uri(f'resource://{path}')
            success, data, _ = file.load_contents(None)
            if not success:
                print(f"Failed to load contents from GResource path: {path}")
                return None
            json_data = data.decode('utf-8')
            return json.loads(json_data)
        except Exception as e:
            print(f"Error loading JSON from {path}: {e}")
            return None

    def apply_standard_shortcuts(self):
        """Applies standard keyboard shortcuts by setting existing GSettings keys."""
        shortcuts = self._load_json_from_gresource(self.standard_shortcuts_path)
        if not shortcuts:
            print("No standard shortcuts to apply.")
            return

        print("--- Applying Standard Keyboard Shortcuts ---")
        for shortcut in shortcuts:
            schema_id = shortcut.get("schema")
            key = shortcut.get("key")
            binding = shortcut.get("binding")

            if not all([schema_id, key, binding]):
                print(f"Skipping invalid standard shortcut entry: {shortcut}")
                continue
            
            try:
                settings = Gio.Settings.new(schema_id)
                settings.set_strv(key, [binding])
                print(f"SUCCESS: Set shortcut for {schema_id} [{key}] to '{binding}'.")
            except Exception as e:
                print(f"ERROR: Failed to set shortcut for {schema_id} [{key}]. Error: {e}")
        print("--- Finished Applying Standard Shortcuts ---")

    def apply_custom_shortcuts(self):
        """
        Applies custom keyboard shortcuts using the 'customX' naming scheme.
        This function is idempotent and avoids creating duplicate shortcuts
        by checking the name and command of existing shortcuts.
        """
        shortcuts_to_add = self._load_json_from_gresource(self.custom_shortcuts_path)
        if not shortcuts_to_add:
            print("No custom shortcuts to apply.")
            return

        print("--- Applying Custom Keyboard Shortcuts ---")
        
        existing_paths = self.media_keys_settings.get_strv(self.custom_bindings_key)
        
        # Create a set of existing shortcuts for quick lookup
        existing_shortcuts = set()
        for path in existing_paths:
            try:
                settings = Gio.Settings.new_with_path(self.custom_binding_schema_id, path)
                name = settings.get_string("name")
                command = settings.get_string("command")
                existing_shortcuts.add((name, command))
            except Exception:
                continue

        next_custom_index = 0
        if existing_paths:
            indices = [int(i) for i in re.findall(r'custom(\d+)', " ".join(existing_paths))]
            if indices:
                next_custom_index = max(indices) + 1

        new_paths_to_add = []

        for shortcut in shortcuts_to_add:
            name = shortcut.get("name")
            command = shortcut.get("command")
            binding = shortcut.get("binding")

            if not all([name, command, binding]):
                print(f"Skipping invalid shortcut entry: {shortcut}")
                continue

            if (name, command) in existing_shortcuts:
                print(f"Shortcut '{name}' with command '{command}' already exists. Skipping.")
                continue

            # Construct the new path using the customX scheme
            new_path = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{next_custom_index}/"
            
            try:
                shortcut_settings = Gio.Settings.new_with_path(self.custom_binding_schema_id, new_path)
                shortcut_settings.set_string("name", name)
                shortcut_settings.set_string("command", command)
                shortcut_settings.set_string("binding", binding)
                
                new_paths_to_add.append(new_path)
                existing_shortcuts.add((name, command)) # Add to set to handle duplicates in the JSON
                print(f"SUCCESS: Prepared new shortcut '{name}' at path {new_path}.")
                next_custom_index += 1

            except Exception as e:
                print(f"ERROR: Failed to create settings for shortcut '{name}'. Error: {e}")

        if new_paths_to_add:
            updated_paths = existing_paths + new_paths_to_add
            try:
                self.media_keys_settings.set_strv(self.custom_bindings_key, updated_paths)
                print(f"SUCCESS: Added {len(new_paths_to_add)} new shortcut(s) to the system list.")
            except Exception as e:
                print(f"ERROR: Failed to update custom-keybindings list. Error: {e}")
        else:
            print("No new custom shortcuts were added.")

        print("--- Finished Applying Custom Shortcuts ---")


# Example usage (for testing)
if __name__ == '__main__':
    manager = ShortcutManager()
    manager.apply_standard_shortcuts()
    manager.apply_custom_shortcuts()
