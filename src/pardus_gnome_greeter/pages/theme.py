import locale
import gi
from locale import gettext as _
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio
import os
import sys

# Add the managers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'managers'))
from ..managers.ThemeManager import ThemeManager

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/ThemePage.ui')
class ThemePage(Adw.PreferencesPage):
    __gtype_name__ = 'ThemePage'
    
    # Template children with explicit names
    light_theme_button = Gtk.Template.Child("light_theme_button")
    dark_theme_button = Gtk.Template.Child("dark_theme_button")
    accent_colors_container = Gtk.Template.Child("accent_colors_container")
    icon_themes_container = Gtk.Template.Child("icon_themes_container")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Setup accent colors
        self.setup_accent_colors()
        self.setup_icon_themes()
        
        # Connect signals
        self.light_theme_button.connect("toggled", self.on_theme_button_toggled)
        self.dark_theme_button.connect("toggled", self.on_theme_button_toggled)
        
        
        # Set initial state
        GLib.idle_add(self.update_button_states)
        GLib.idle_add(self.update_accent_color_states)
        GLib.idle_add(self.update_icon_theme_states)
    
    def setup_icon_themes(self):
        """Setup icon theme selection"""
        self.icon_theme_buttons = {}
        first_button = None
        
        try:
            resource_path = "/tr/org/pardus/pardus-gnome-greeter/json/icon_themes.json"
            data_bytes = Gio.resources_lookup_data(resource_path, 0)
            data_str = data_bytes.get_data().decode('utf-8')
            icon_themes = json.loads(data_str)
            
            for theme in icon_themes:
                name = theme["name"]
                icon = theme["icon"]
                theme_name = theme["theme"]
                
                button = Gtk.ToggleButton()
                button.set_name(theme_name)
                button.add_css_class("card")
                button.set_tooltip_text(_(name.title()))
                button.set_size_request(100, 64)

                if first_button is None:
                    first_button = button
                else:
                    button.set_group(first_button)
                
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                box.set_halign(Gtk.Align.CENTER)
                box.set_valign(Gtk.Align.CENTER)

                img_resource_path = f"/tr/org/pardus/pardus-gnome-greeter/assets/icon-themes/{icon}"
                img = Gtk.Image.new_from_resource(img_resource_path)
                img.set_pixel_size(48)
                
                label = Gtk.Label(label=_(name.title()))
                label.add_css_class("caption")
                
                box.append(img)
                box.append(label)
                button.set_child(box)
                
                button.connect("toggled", self.on_icon_theme_toggled)
                self.icon_themes_container.append(button)
                
                self.icon_theme_buttons[theme_name] = button

        except (GLib.Error, json.JSONDecodeError) as e:
            print(f"Error setting up icon themes: {e}")

    def on_icon_theme_toggled(self, button):
        """Handle icon theme change"""
        if not button.get_active():
            return
            
        theme_name = button.get_name()
        
        try:
            self.theme_manager.set_icon_theme(theme_name)
        except Exception as e:
            print(f"Error setting icon theme: {e}")
            
    def update_icon_theme_states(self):
        """Update icon theme button states based on current setting"""
        try:
            current_icon_theme = self.theme_manager.get_current_icon_theme()
            
            for name, button in self.icon_theme_buttons.items():
                button.handler_block_by_func(self.on_icon_theme_toggled)
            
            if current_icon_theme in self.icon_theme_buttons:
                self.icon_theme_buttons[current_icon_theme].set_active(True)
            else:
                self.icon_theme_buttons["Adwaita"].set_active(True)
            
            for name, button in self.icon_theme_buttons.items():
                button.handler_unblock_by_func(self.on_icon_theme_toggled)
                
        except Exception as e:
            print(f"Error updating icon theme states: {e}")
            try:
                self.icon_theme_buttons["Adwaita"].set_active(True)
            except:
                pass
                
        return False

    def setup_accent_colors(self):
        """Setup accent color selection"""
        colors = [
            ("blue", "#3584e4"),
            ("teal", "#2ec27e"), 
            ("green", "#33d17a"),
            ("yellow", "#f6d32d"),
            ("orange", "#ff7800"),
            ("red", "#e01b24"),
            ("pink", "#c061cb"),
            ("purple", "#9141ac"),
            ("slate", "#6c758f"),
        ]
        
        self.accent_color_buttons = {}
        first_button = None
        
        for name, color in colors:
            button = Gtk.ToggleButton()
            button.set_name(name)
            button.add_css_class("accent-color-button")
            button.add_css_class(f"accent-{name}")
            button.set_tooltip_text(_(name.title()))
            button.set_size_request(32, 32)
            
            if first_button is None:
                first_button = button
            else:
                button.set_group(first_button)
                
            button.connect("toggled", self.on_accent_color_toggled)
            self.accent_colors_container.append(button)
            
            # Store button reference for later state updates
            self.accent_color_buttons[name] = button
    
    def update_accent_color_states(self):
        """Update accent color button states based on current setting"""
        try:
            current_accent = self.theme_manager.get_current_accent_color()
            print(f"Current accent color: {current_accent}")
            
            # Block signals to avoid recursion
            for name, button in self.accent_color_buttons.items():
                button.handler_block_by_func(self.on_accent_color_toggled)
            
            # Set the correct button as active
            if current_accent in self.accent_color_buttons:
                self.accent_color_buttons[current_accent].set_active(True)
                print(f"Set {current_accent} button as active")
            else:
                # Default to blue if current accent is unknown
                self.accent_color_buttons["blue"].set_active(True)
                print("Defaulted to blue accent color")
            
            # Unblock signals
            for name, button in self.accent_color_buttons.items():
                button.handler_unblock_by_func(self.on_accent_color_toggled)
                
        except Exception as e:
            print(f"Error updating accent color states: {e}")
            # Default to blue on error
            try:
                self.accent_color_buttons["blue"].set_active(True)
            except:
                pass
                
        return False  # Don't repeat the timeout
    
    def on_accent_color_toggled(self, button):
        """Handle accent color change"""
        if not button.get_active():
            return
            
        color_name = button.get_name()
        print(f"Selected accent color: {color_name}")
        
        # Apply the accent color through theme manager
        try:
            self.theme_manager.set_accent_color(color_name)
        except Exception as e:
            print(f"Error setting accent color: {e}")
        
    def on_theme_button_toggled(self, button):
        """Handle theme button toggle"""
        if not button.get_active():
            return
            
        button_name = button.get_name()
        
        try:
            if button_name == "light":
                self.theme_manager.apply_light_theme()
                print("Applied light theme")
            elif button_name == "dark":
                self.theme_manager.apply_dark_theme()
                print("Applied dark theme")
                
            # Update button states after a small delay to ensure settings are applied
            GLib.timeout_add(200, self.update_button_states)
            
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def update_button_states(self):
        """Update button states based on current theme"""
        try:
            # Get current theme state
            is_dark = self.theme_manager.is_dark_theme_active()
            is_light = self.theme_manager.is_light_theme_active()
            
            print(f"Theme state: dark={is_dark}, light={is_light}")
            
            # Temporarily disconnect signals to avoid recursion
            self.light_theme_button.handler_block_by_func(self.on_theme_button_toggled)
            self.dark_theme_button.handler_block_by_func(self.on_theme_button_toggled)
            
            # Set button states based on current theme
            if is_dark:
                self.dark_theme_button.set_active(True)
                print("Set dark button active")
            elif is_light:
                self.light_theme_button.set_active(True)  
                print("Set light button active")
            else:
                # Default to light if no specific theme is detected
                self.light_theme_button.set_active(True)
                print("Defaulted to light theme")
            
            # Reconnect signals
            self.light_theme_button.handler_unblock_by_func(self.on_theme_button_toggled)
            self.dark_theme_button.handler_unblock_by_func(self.on_theme_button_toggled)
            
        except Exception as e:
            print(f"Error updating button states: {e}")
            # Default to light theme on error
            try:
                self.light_theme_button.set_active(True)
            except:
                pass
            
        return False  # Don't repeat the timeout
        
    def refresh_theme_state(self):
        """Public method to refresh theme state from outside"""
        self.update_button_states()
        self.update_accent_color_states()
        self.update_icon_theme_states() 