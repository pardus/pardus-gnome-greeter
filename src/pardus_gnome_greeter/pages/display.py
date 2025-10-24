import locale
import gi
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)
from ..managers.DisplayManager import display_manager

CURSOR_SCHEMA = "org.gnome.desktop.interface"
CURSOR_KEY = "cursor-size"

DESKTOP_ICONS_SCHEMA = "org.gnome.shell.extensions.ding"
DESKTOP_ICONS_KEY = "icon-size"

NAUTILUS_SCHEMA = "org.gnome.nautilus.icon-view"
NAUTILUS_KEY = "default-zoom-level"

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/DisplayPage.ui')
class DisplayPage(Adw.PreferencesPage):
    __gtype_name__ = 'DisplayPage'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.settings = Gio.Settings.new(CURSOR_SCHEMA)
        self.desktop_icons_settings = Gio.Settings.new(DESKTOP_ICONS_SCHEMA)
        self.nautilus_settings = Gio.Settings.new(NAUTILUS_SCHEMA)
        self.monitors_group = None

        # Maps for settings
        self.cursor_size_map = {0: 24, 1: 32, 2: 48} # Small, Medium, Large
        self.desktop_icons_map = {0: 'tiny', 1: 'small', 2: 'standard', 3: 'large'}
        self.nautilus_zoom_map = {0: 'small', 1: 'small-plus', 2: 'medium', 3: 'large', 4: 'extra-large'}

        display_manager.get_monitors(self.on_monitors_loaded)

    def on_monitors_loaded(self, monitors_config):
        # Remove existing monitors group if it exists
        if self.monitors_group:
            self.remove(self.monitors_group)
        
        # Create monitors group
        self.monitors_group = Adw.PreferencesGroup(title=_("Monitors"))
        self.add(self.monitors_group)
        
        # Add monitors if available
        if monitors_config:
            for monitor_info in monitors_config:
                title = monitor_info.get('name', f"Monitor {monitor_info['id']}")
                expander_row = Adw.ExpanderRow(title=title)
                self.monitors_group.add(expander_row)

                # Add resolution selection
                resolution_row = Adw.ComboRow(title=_("Resolution"))
                resolution_store = Gtk.StringList()
                supported_resolutions = monitor_info.get('supported_resolutions', [])
                for res_info in supported_resolutions:
                    resolution_text = f"{res_info['resolution']} @ {res_info['refresh_rate']:.0f}Hz"
                    resolution_store.append(resolution_text)
                resolution_row.set_model(resolution_store)
                # Set current resolution as selected
                current_resolution = monitor_info.get('current_resolution')
                if current_resolution:
                    current_res_text = f"{current_resolution['resolution']} @ {current_resolution['refresh_rate']:.0f}Hz"
                    for i, res_info in enumerate(supported_resolutions):
                        res_text = f"{res_info['resolution']} @ {res_info['refresh_rate']:.0f}Hz"
                        if res_text == current_res_text:
                            resolution_row.set_selected(i)
                            break
                resolution_row.connect("notify::selected", self.on_resolution_changed, monitor_info['id'], supported_resolutions)
                expander_row.add_row(resolution_row)

                # Add scale selection (independent)
                scale_row = Adw.ComboRow(title=_("Scale"))
                scale_store = Gtk.StringList()
                supported_scales = monitor_info.get('supported_scales', [1.0])
                for scale in supported_scales:
                    scale_store.append(f"{int(scale * 100)}%")
                scale_row.set_model(scale_store)
                # Set current scale as selected
                current_scale = monitor_info.get('scale', 1.0)
                for i, scale in enumerate(supported_scales):
                    if abs(scale - current_scale) < 0.1:
                        scale_row.set_selected(i)
                        break
                scale_row.connect("notify::selected", self.on_scale_changed, monitor_info['id'], supported_scales)
                expander_row.add_row(scale_row)

                # Store references (not needed for independence, but for future use)
                resolution_row.scale_row = scale_row
                resolution_row.supported_resolutions = supported_resolutions
        
        # Add scaling group after monitors
        self.add_scaling_group()

    def add_scaling_group(self):
        # Create a single group for all scaling options
        scaling_group = Adw.PreferencesGroup(title=_("Interface Scaling"))
        self.add(scaling_group)

        # Cursor Size
        cursor_labels = [_("Small"), _("Medium"), _("Large")]
        cursor_model = Gtk.StringList.new(cursor_labels)
        self.cursor_size_row = Adw.ComboRow(title=_("Cursor Size"), model=cursor_model)
        scaling_group.add(self.cursor_size_row)
        
        current_cursor_size = self.settings.get_int(CURSOR_KEY)
        rev_cursor_map = {v: k for k, v in self.cursor_size_map.items()}
        cursor_selected_index = rev_cursor_map.get(current_cursor_size, 1) # Default to Medium
        self.cursor_size_row.set_selected(cursor_selected_index)
        self.cursor_size_row.connect("notify::selected", self.on_cursor_size_changed)

        # Desktop Icons
        desktop_labels = [_("Tiny"), _("Small"), _("Standard"), _("Large")]
        desktop_model = Gtk.StringList.new(desktop_labels)
        self.desktop_icons_row = Adw.ComboRow(title=_("Desktop Icon Size"), model=desktop_model)
        scaling_group.add(self.desktop_icons_row)
        
        current_desktop_size = self.desktop_icons_settings.get_string(DESKTOP_ICONS_KEY)
        rev_desktop_map = {v: k for k, v in self.desktop_icons_map.items()}
        desktop_selected_index = rev_desktop_map.get(current_desktop_size, 2) # Default to Standard
        self.desktop_icons_row.set_selected(desktop_selected_index)
        self.desktop_icons_row.connect("notify::selected", self.on_desktop_icon_size_changed)

        # File Manager Icons
        nautilus_labels = [_("Small"), _("Small+"), _("Medium"), _("Large"), _("Extra Large")]
        nautilus_model = Gtk.StringList.new(nautilus_labels)
        self.nautilus_zoom_row = Adw.ComboRow(title=_("File Manager Icon Size"), model=nautilus_model)
        scaling_group.add(self.nautilus_zoom_row)
        
        current_nautilus_zoom = self.nautilus_settings.get_string(NAUTILUS_KEY)
        rev_nautilus_map = {v: k for k, v in self.nautilus_zoom_map.items()}
        nautilus_selected_index = rev_nautilus_map.get(current_nautilus_zoom, 2) # Default to Medium
        self.nautilus_zoom_row.set_selected(nautilus_selected_index)
        self.nautilus_zoom_row.connect("notify::selected", self.on_nautilus_zoom_changed)

    def on_cursor_size_changed(self, combo, _):
        selected_index = combo.get_selected()
        new_size = self.cursor_size_map.get(selected_index)
        if new_size is not None:
            self.settings.set_int(CURSOR_KEY, new_size)

    def on_desktop_icon_size_changed(self, combo, _):
        selected_index = combo.get_selected()
        new_size = self.desktop_icons_map.get(selected_index)
        if new_size is not None:
            self.desktop_icons_settings.set_string(DESKTOP_ICONS_KEY, new_size)

    def on_nautilus_zoom_changed(self, combo, _):
        selected_index = combo.get_selected()
        new_zoom = self.nautilus_zoom_map.get(selected_index)
        if new_zoom is not None:
            self.nautilus_settings.set_string(NAUTILUS_KEY, new_zoom)
    
    def on_scale_changed(self, widget, _, monitor_id, scales):
        selected_index = widget.get_selected()
        if selected_index < 0 or selected_index >= len(scales):
            return
        new_scale = scales[selected_index]
        
        # Apply the scale change - we need to get the current mode_id
        # For now, we'll use a default mode_id of 0, but ideally we should track the current mode
        success = display_manager.apply_scale_change(monitor_id, 0, new_scale)
        if success:
            pass
        else:
            pass

    def on_resolution_changed(self, widget, _, monitor_id, resolutions):
        selected_index = widget.get_selected()
        if selected_index < 0 or selected_index >= len(resolutions):
            return
        new_resolution = resolutions[selected_index]
        print(f"Monitor {monitor_id} resolution changed to: {new_resolution['resolution']} @ {new_resolution['refresh_rate']:.0f}Hz")
        print(f"  Mode ID: {new_resolution['mode_id']}")
        
        # Apply the resolution change (with default scale 1.0)
        success = display_manager.apply_resolution_change(monitor_id, new_resolution['mode_id'])
        if success:
            print(f"Successfully applied resolution change")
        else:
            print(f"Failed to apply resolution change")
            



 