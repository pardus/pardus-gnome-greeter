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

# Cursor Size Slider Component
@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/CursorSizeSlider.ui')
class CursorSizeSlider(Adw.ActionRow):
    __gtype_name__ = 'CursorSizeSlider'

    cursor_size_scale = Gtk.Template.Child()
    labels_box = Gtk.Template.Child()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.settings = Gio.Settings.new(CURSOR_SCHEMA)
        self.setup_labels()
        self.load_settings()
        self.cursor_size_scale.connect("value-changed", self.on_value_changed)

    def setup_labels(self):
        # Add labels for each step
        labels = [_("Small"), _("Medium"), _("Large")]
        for i, label_text in enumerate(labels):
            label = Gtk.Label(label=label_text)
            label.set_hexpand(True)
            if i == 0:
                label.set_xalign(0.0)  # Left align first label
            elif i == len(labels) - 1:
                label.set_xalign(1.0)  # Right align last label
            else:
                label.set_xalign(0.5)  # Center align middle labels
            self.labels_box.append(label)
        
        # Add tick marks to the slider
        for i in range(len(labels)):
            self.cursor_size_scale.add_mark(i, Gtk.PositionType.BOTTOM, None)

    def load_settings(self):
        cursor_size = self.settings.get_int(CURSOR_KEY)
        if cursor_size <= 24:
            value = 0  # Small
        elif cursor_size <= 32:
            value = 1  # Medium
        else:
            value = 2  # Large
        
        self.cursor_size_scale.set_value(value)
        # Update fill level to match the value
        self.cursor_size_scale.set_fill_level(value)

    def on_value_changed(self, widget):
        value = int(widget.get_value())
        cursor_size_mapping = {
            0: 16,  # Small
            1: 24,  # Medium
            2: 32   # Large
        }
        size = cursor_size_mapping.get(value, 24)
        self.settings.set_int(CURSOR_KEY, size)
        # Update fill level to match the new value
        widget.set_fill_level(value)

# Desktop Icon Slider Component
@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/DesktopIconSlider.ui')
class DesktopIconSlider(Adw.ActionRow):
    __gtype_name__ = 'DesktopIconSlider'

    desktop_icon_scale = Gtk.Template.Child()
    labels_box = Gtk.Template.Child()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.settings = Gio.Settings.new(DESKTOP_ICONS_SCHEMA)
        self.setup_labels()
        self.load_settings()
        self.desktop_icon_scale.connect("value-changed", self.on_value_changed)

    def setup_labels(self):
        # Add labels for each step
        labels = [_("Tiny"), _("Small"), _("Standard"), _("Large")]
        for i, label_text in enumerate(labels):
            label = Gtk.Label(label=label_text)
            label.set_hexpand(True)
            if i == 0:
                label.set_xalign(0.0)  # Left align first label
            elif i == len(labels) - 1:
                label.set_xalign(1.0)  # Right align last label
            else:
                label.set_xalign(0.5)  # Center align middle labels
            self.labels_box.append(label)
        
        # Add tick marks to the slider
        for i in range(len(labels)):
            self.desktop_icon_scale.add_mark(i, Gtk.PositionType.BOTTOM, None)

    def load_settings(self):
        desktop_icon_size = self.settings.get_string(DESKTOP_ICONS_KEY)
        desktop_icon_mapping = {
            'tiny': 0,
            'small': 1,
            'standard': 2,
            'large': 3
        }
        desktop_value = desktop_icon_mapping.get(desktop_icon_size, 2)
        self.desktop_icon_scale.set_value(desktop_value)
        # Update fill level to match the value
        self.desktop_icon_scale.set_fill_level(desktop_value)

    def on_value_changed(self, widget):
        value = int(widget.get_value())
        desktop_icon_mapping = {
            0: 'tiny',
            1: 'small',
            2: 'standard',
            3: 'large'
        }
        size = desktop_icon_mapping.get(value, 'standard')
        self.settings.set_string(DESKTOP_ICONS_KEY, size)
        # Update fill level to match the new value
        widget.set_fill_level(value)

# File Manager Icon Slider Component
@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/FileManagerIconSlider.ui')
class FileManagerIconSlider(Adw.ActionRow):
    __gtype_name__ = 'FileManagerIconSlider'

    file_manager_icon_scale = Gtk.Template.Child()
    labels_box = Gtk.Template.Child()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.settings = Gio.Settings.new(NAUTILUS_SCHEMA)
        self.setup_labels()
        self.load_settings()
        self.file_manager_icon_scale.connect("value-changed", self.on_value_changed)

    def setup_labels(self):
        # Add labels for each step
        labels = [_("Small"), _("Small+"), _("Medium"), _("Large"), _("Extra Large")]
        for i, label_text in enumerate(labels):
            label = Gtk.Label(label=label_text)
            label.set_hexpand(True)
            if i == 0:
                label.set_xalign(0.0)  # Left align first label
            elif i == len(labels) - 1:
                label.set_xalign(1.0)  # Right align last label
            else:
                label.set_xalign(0.5)  # Center align middle labels
            self.labels_box.append(label)
        
        # Add tick marks to the slider
        for i in range(len(labels)):
            self.file_manager_icon_scale.add_mark(i, Gtk.PositionType.BOTTOM, None)

    def load_settings(self):
        nautilus_icon_size = self.settings.get_string(NAUTILUS_KEY)
        nautilus_icon_mapping = {
            'small': 0,
            'small-plus': 1,
            'medium': 2,
            'large': 3,
            'extra-large': 4
        }
        nautilus_value = nautilus_icon_mapping.get(nautilus_icon_size, 2)
        self.file_manager_icon_scale.set_value(nautilus_value)
        # Update fill level to match the value
        self.file_manager_icon_scale.set_fill_level(nautilus_value)

    def on_value_changed(self, widget):
        value = int(widget.get_value())
        nautilus_icon_mapping = {
            0: 'small',
            1: 'small-plus',
            2: 'medium',
            3: 'large',
            4: 'extra-large'
        }
        size = nautilus_icon_mapping.get(value, 'medium')
        self.settings.set_string(NAUTILUS_KEY, size)
        # Update fill level to match the new value
        widget.set_fill_level(value)

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

        display_manager.get_monitors(self.on_monitors_loaded)

    def on_monitors_loaded(self, monitors_config):
        # Remove existing monitors group if it exists
        if self.monitors_group:
            self.remove(self.monitors_group)
        
        # Create monitors group
        self.monitors_group = Adw.PreferencesGroup(title="Monitors")
        self.add(self.monitors_group)
        
        # Add monitors if available
        if monitors_config:
            for monitor_info in monitors_config:
                title = monitor_info.get('name', f"Monitor {monitor_info['id']}")
                expander_row = Adw.ExpanderRow(title=title)
                self.monitors_group.add(expander_row)

                # Add resolution selection
                resolution_row = Adw.ComboRow(title="Resolution")
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
                scale_row = Adw.ComboRow(title="Scale")
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
        
        # Add cursor size group after monitors
        self.add_cursor_size_group()
        
        # Add desktop icons group after cursor size
        self.add_desktop_icons_group()
        
        # Add file manager group after desktop icons
        self.add_file_manager_group()

    def add_cursor_size_group(self):
        # Create cursor size group
        cursor_group = Adw.PreferencesGroup(title="Cursor")
        self.add(cursor_group)
        
        # Create cursor size slider using UI template
        cursor_slider = CursorSizeSlider()
        cursor_group.add(cursor_slider)

    def add_desktop_icons_group(self):
        # Create desktop icons group
        desktop_group = Adw.PreferencesGroup(title="Desktop Icons")
        self.add(desktop_group)
        
        # Create desktop icon slider using UI template
        desktop_slider = DesktopIconSlider()
        desktop_group.add(desktop_slider)

    def add_file_manager_group(self):
        # Create file manager group
        file_manager_group = Adw.PreferencesGroup(title="File Manager")
        self.add(file_manager_group)
        
        # Create file manager icon slider using UI template
        file_manager_slider = FileManagerIconSlider()
        file_manager_group.add(file_manager_slider)
        

    
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
            



 