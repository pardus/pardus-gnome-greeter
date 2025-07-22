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

            scale_row = Adw.ComboRow(title="Scale")
            store = Gtk.StringList()
            
            supported_scales = monitor_info.get('supported_scales', [1.0])
            for scale_value in supported_scales:
                store.append(f"{int(scale_value * 100)}%")
            
            scale_row.set_model(store)
            
            try:
                current_scale = monitor_info.get('scale', 1.0)
                current_scale_index = supported_scales.index(current_scale)
                scale_row.set_selected(current_scale_index)
            except ValueError:
                scale_row.set_selected(0)

            scale_row.connect("notify::selected", self.on_scale_changed, monitor_info['id'], supported_scales)
            expander_row.add_row(scale_row)
    
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