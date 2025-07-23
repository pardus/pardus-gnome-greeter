import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib
from ..managers.DisplayManager import display_manager

CURSOR_SCHEMA = "org.gnome.desktop.interface"
CURSOR_KEY = "cursor-size"

FILE_MANAGER_SCHEMA = "org.gnome.nautilus.icon-view"
FILE_MANAGER_KEY = "default-zoom-level"

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/DisplayPage.ui')
class DisplayPage(Adw.PreferencesPage):
    __gtype_name__ = 'DisplayPage'

    cursor_size_row = Gtk.Template.Child()
    file_manager_icon_size_row = Gtk.Template.Child()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.settings = Gio.Settings.new(CURSOR_SCHEMA)
        self.file_manager_settings = Gio.Settings.new(FILE_MANAGER_SCHEMA)
        self.monitors_group = None

        self.load_settings()
        display_manager.get_monitors(self.on_monitors_loaded)

        self.cursor_size_row.connect("notify::selected", self.on_cursor_size_changed)
        self.file_manager_icon_size_row.connect("notify::selected", self.on_file_manager_icon_size_changed)

    def on_monitors_loaded(self, monitors_config):
        if self.monitors_group:
            self.remove(self.monitors_group)
        
        if not monitors_config:
            # Optionally show a message that no monitors were found
            return
        
        self.monitors_group = Adw.PreferencesGroup(title="Monitors")
        self.add(self.monitors_group)

        for monitor_info in monitors_config:
            title = monitor_info.get('name', f"Monitor {monitor_info['id']}")
            expander_row = Adw.ExpanderRow(title=title)
            self.monitors_group.add(expander_row)

            # Remove the old, non-functional scale row above the resolution row
            # scale_row = Adw.ComboRow(title="Scale")
            # store = Gtk.StringList()
            # supported_scales = monitor_info.get('supported_scales', [1.0])
            # for scale_value in supported_scales:
            #     store.append(f"{int(scale_value * 100)}%")
            # scale_row.set_model(store)
            # try:
            #     current_scale = monitor_info.get('scale', 1.0)
            #     current_scale_index = supported_scales.index(current_scale)
            #     scale_row.set_selected(current_scale_index)
            # except ValueError:
            #     scale_row.set_selected(0)
            # scale_row.connect("notify::selected", self.on_scale_changed, monitor_info['id'], supported_scales)
            # expander_row.add_row(scale_row)

            # Add resolution selection (and scale selection below it)
            resolution_row = Adw.ComboRow(title="Resolution")
            resolution_store = Gtk.StringList()
            
            supported_resolutions = monitor_info.get('supported_resolutions', [])
            if supported_resolutions:
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
                
                # Add scale selection for the resolution
                scale_for_resolution_row = Adw.ComboRow(title="Scale")
                scale_for_resolution_store = Gtk.StringList()
                
                # Get supported scales for current/selected resolution
                current_resolution_scales = []
                if current_resolution:
                    # Find current resolution in supported_resolutions to get its scales
                    for res_info in supported_resolutions:
                        if (res_info['resolution'] == current_resolution['resolution'] and 
                            abs(res_info['refresh_rate'] - current_resolution['refresh_rate']) < 0.1):
                            current_resolution_scales = res_info.get('supported_scales', [1.0])
                            print(f"DEBUG: Found current resolution {res_info['resolution']} with scales: {current_resolution_scales}")
                            break
                    
                    # If not found in supported_resolutions, use monitor's global supported_scales
                    if not current_resolution_scales:
                        current_resolution_scales = monitor_info.get('supported_scales', [1.0])
                        print(f"DEBUG: Using monitor global scales: {current_resolution_scales}")
                
                if not current_resolution_scales:
                    current_resolution_scales = [1.0]  # Fallback
                
                print(f"DEBUG: Final current_resolution_scales for monitor {monitor_info['id']}: {current_resolution_scales}")
                print(f"DEBUG: Monitor {monitor_info['id']} scales: {current_resolution_scales}")
                
                for scale_value in current_resolution_scales:
                    scale_text = f"{int(scale_value * 100)}%"
                    scale_for_resolution_store.append(scale_text)
                    print(f"DEBUG: Added scale option: {scale_text}")
                
                scale_for_resolution_row.set_model(scale_for_resolution_store)
                
                # Set current scale as selected
                current_scale = monitor_info.get('scale', 1.0)
                print(f"DEBUG: Current scale for monitor {monitor_info['id']}: {current_scale}")
                
                try:
                    current_scale_index = current_resolution_scales.index(current_scale)
                    scale_for_resolution_row.set_selected(current_scale_index)
                    print(f"DEBUG: Set scale index to: {current_scale_index}")
                except ValueError:
                    scale_for_resolution_row.set_selected(0)  # Default to first scale
                    print(f"DEBUG: Current scale {current_scale} not found, defaulting to index 0")
                
                # Get current resolution mode_id for initial handler
                current_mode_id = None
                if current_resolution:
                    current_mode_id = current_resolution.get('mode_id')
                
                scale_for_resolution_row.connect("notify::selected", self.on_scale_for_resolution_changed, 
                                                 monitor_info['id'], current_resolution_scales, current_mode_id)
                expander_row.add_row(scale_for_resolution_row)
                
                print(f"DEBUG: Scale row added for monitor {monitor_info['id']} with {len(current_resolution_scales)} options")
                
                # Store references for updating scale options when resolution changes
                resolution_row.scale_row = scale_for_resolution_row
                resolution_row.supported_resolutions = supported_resolutions
                
            else:
                # If no resolutions found, show current resolution as read-only
                current_resolution = monitor_info.get('current_resolution')
                if current_resolution:
                    resolution_text = f"{current_resolution['resolution']} @ {current_resolution['refresh_rate']:.0f}Hz"
                    resolution_label_row = Adw.ActionRow(title="Resolution", subtitle=resolution_text)
                    expander_row.add_row(resolution_label_row)
    
    def load_settings(self):
        cursor_size = self.settings.get_int(CURSOR_KEY)
        if cursor_size <= 24:
            self.cursor_size_row.set_selected(0)
        elif cursor_size <= 32:
            self.cursor_size_row.set_selected(1)
        else:
            self.cursor_size_row.set_selected(2)

        file_manager_icon_size = self.file_manager_settings.get_string(FILE_MANAGER_KEY)
        if file_manager_icon_size == 'small':
            self.file_manager_icon_size_row.set_selected(0)
        elif file_manager_icon_size == 'standard':
            self.file_manager_icon_size_row.set_selected(1)
        else:
            self.file_manager_icon_size_row.set_selected(2)

    def on_scale_changed(self, widget, _, monitor_id, scales):
        selected_index = widget.get_selected()
        if selected_index < 0:
            return
        new_scale = scales[selected_index]
        print(f"Monitor {monitor_id} scale changed to: {new_scale}")
        # Applying this change requires a complex D-Bus call

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
            
        # Update scale options for the new resolution
        if hasattr(widget, 'scale_row') and widget.scale_row:
            # Get supported scales for the new resolution
            new_resolution_scales = new_resolution.get('supported_scales', [1.0])
            
            # Clear and update scale options
            scale_store = Gtk.StringList()
            for scale_value in new_resolution_scales:
                scale_store.append(f"{int(scale_value * 100)}%")
            
            widget.scale_row.set_model(scale_store)
            
            # Select 100% (1.0) as default if available, otherwise first option
            default_index = 0
            try:
                default_index = new_resolution_scales.index(1.0)
            except ValueError:
                pass
            
            widget.scale_row.set_selected(default_index)
            
            # Update the handler with new scales
            # Disconnect old handler
            for handler_id in getattr(widget.scale_row, '_scale_handlers', []):
                widget.scale_row.disconnect(handler_id)
            
            # Connect new handler
            handler_id = widget.scale_row.connect("notify::selected", self.on_scale_for_resolution_changed, 
                                                 monitor_id, new_resolution_scales, new_resolution['mode_id'])
            widget.scale_row._scale_handlers = [handler_id]

    def on_scale_for_resolution_changed(self, widget, _, monitor_id, scales, mode_id):
        selected_index = widget.get_selected()
        if selected_index < 0 or selected_index >= len(scales):
            return
        new_scale = scales[selected_index]
        print(f"Monitor {monitor_id} scale changed to: {new_scale}")
        
        # Apply the scale change using the current resolution mode_id
        success = display_manager.apply_scale_change(monitor_id, mode_id, new_scale)
        if success:
            print(f"Successfully applied scale change")
        else:
            print(f"Failed to apply scale change")

    def on_cursor_size_changed(self, widget, _):
        selected = widget.get_selected()
        if selected == 0:
            size = 24
        elif selected == 1:
            size = 32
        else:
            size = 48
        self.settings.set_int(CURSOR_KEY, size)

    def on_file_manager_icon_size_changed(self, widget, _):
        selected = widget.get_selected()
        if selected == 0:
            size = "small"
        elif selected == 1:
            size = "standard"
        else:
            size = "large"
        self.file_manager_settings.set_string(FILE_MANAGER_KEY, size) 