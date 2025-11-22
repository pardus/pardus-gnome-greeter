import locale
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio
import os
import sys

# Add the managers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'managers'))
from ..managers.ExtensionManager import ExtensionManager
from ..managers.ThemeManager import ThemeManager

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/TimePage.ui')
class TimePage(Adw.PreferencesPage):
    __gtype_name__ = 'TimePage'
    
    # Template children
    clock_format_switch = Gtk.Template.Child("clock_format_switch")
    time_only_button = Gtk.Template.Child("time_only_button")
    date_time_button = Gtk.Template.Child("date_time_button")
    font_size_spinbutton = Gtk.Template.Child("font_size_spinbutton")
    show_seconds_switch = Gtk.Template.Child("show_seconds_switch")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize managers
        self.extension_manager = ExtensionManager()
        
        # Extension settings
        self.clock_extension_id = "date-menu-formatter@marcinjakubowski.github.com"
        self.schema = "org.gnome.shell.extensions.date-menu-formatter"
        self.pattern_key = "pattern"
        self.font_size_key = "font-size"

        # Keep a persistent settings object to listen for changes
        self.settings = Gio.Settings.new(self.schema)
        self.settings.connect("changed", self.on_settings_changed)
        
        # Listen for extension enable/disable state changes in Gnome Shell
        self.shell_settings = Gio.Settings.new("org.gnome.shell")
        self.shell_settings.connect("changed::enabled-extensions", self.on_shell_settings_changed)
        self.shell_settings.connect("changed::disabled-extensions", self.on_shell_settings_changed)
        
        # State update flag to prevent signal loops
        self._updating = False
        
        # Format types (Luxon format for the extension)
        self.format_types = {
            "time": "H:mm",
            "time-sec": "H:mm:ss",
            "date": "H:mm\ndd.MM.yyyy",
            "date-sec": "H:mm:ss\ndd.MM.yyyy",
        }
        
        # Connect signals
        self.clock_format_switch.connect("state-set", self.on_extension_toggle)
        self.time_only_button.connect("toggled", self.on_format_change, "time")
        self.date_time_button.connect("toggled", self.on_format_change, "date")
        self.font_size_spinbutton.connect("value-changed", self.on_font_size_change)
        self.show_seconds_switch.connect("state-set", self.on_seconds_toggle)
        
        # Update when the page becomes visible
        self.connect("map", self.on_page_mapped)

        # Set initial state
        GLib.idle_add(self.update_initial_state)
    
    def on_page_mapped(self, widget):
        """Called when the page becomes visible"""
        self.update_initial_state()

    def on_shell_settings_changed(self, settings, key):
        """Called when enabled/disabled extensions change"""
        GLib.idle_add(self.update_initial_state)

    def on_settings_changed(self, settings, key):
        """Called when settings change externally"""
        # Update on ANY setting change in the extension schema
        GLib.idle_add(self.update_initial_state)
    
    def update_initial_state(self):
        """Update the initial state of all widgets"""
        if self._updating:
            return

        self._updating = True
        try:
            # Check if extension is enabled
            is_enabled = self.extension_manager.is_extension_enabled(self.clock_extension_id)
            self.clock_format_switch.set_active(is_enabled)
            
            # Get current pattern
            current_pattern = self.settings.get_string(self.pattern_key)
            
            # Set format buttons based on pattern (detects Luxon components)
            if any(c in current_pattern for c in ['d', 'M', 'y', 'E', 'c']):
                self.date_time_button.set_active(True)
            else:
                self.time_only_button.set_active(True)
            
            # Set seconds switch
            if 'ss' in current_pattern:
                self.show_seconds_switch.set_active(True)
            else:
                self.show_seconds_switch.set_active(False)
            
            # Set font size
            font_size = self.settings.get_int(self.font_size_key)
            self.font_size_spinbutton.set_value(font_size)
            
            # Update sensitivity
            self.update_sensitivity(is_enabled)
            
        except Exception as e:
            print(f"Error updating initial state: {e}")
        finally:
            self._updating = False
    
    def update_sensitivity(self, enabled):
        """Update sensitivity of widgets based on extension state"""
        self.time_only_button.set_sensitive(enabled)
        self.date_time_button.set_sensitive(enabled)
        self.font_size_spinbutton.set_sensitive(enabled)
        self.show_seconds_switch.set_sensitive(enabled)
    
    def on_extension_toggle(self, switch, state):
        """Handle extension enable/disable"""
        if self._updating:
            return

        try:
            if state:
                self.extension_manager.enable_extension(self.clock_extension_id)
            else:
                self.extension_manager.disable_extension(self.clock_extension_id)
            
            self.update_sensitivity(state)
            
        except Exception as e:
            print(f"Error toggling extension: {e}")
    
    def on_format_change(self, button, format_type):
        """Handle format type change"""
        if self._updating:
            return

        if not button.get_active():
            return
            
        try:
            # Check if seconds should be shown
            show_seconds = self.show_seconds_switch.get_active()
            
            # Determine the pattern
            if show_seconds:
                pattern = self.format_types[f"{format_type}-sec"]
            else:
                pattern = self.format_types[format_type]
            
            # Set the pattern
            self.settings.set_string(self.pattern_key, pattern)
            
        except Exception as e:
            print(f"Error changing format: {e}")
    
    def on_font_size_change(self, spinbutton):
        """Handle font size change"""
        if self._updating:
            return

        try:
            size = int(spinbutton.get_value())
            self.settings.set_int(self.font_size_key, size)
            
        except Exception as e:
            print(f"Error changing font size: {e}")
    
    def on_seconds_toggle(self, switch, state):
        """Handle seconds display toggle"""
        if self._updating:
            return

        try:
            # Determine current format type
            if self.date_time_button.get_active():
                format_type = "date"
            else:
                format_type = "time"
            
            # Set the pattern
            if state:
                pattern = self.format_types[f"{format_type}-sec"]
            else:
                pattern = self.format_types[format_type]
            
            self.settings.set_string(self.pattern_key, pattern)
            
        except Exception as e:
            print(f"Error toggling seconds: {e}") 