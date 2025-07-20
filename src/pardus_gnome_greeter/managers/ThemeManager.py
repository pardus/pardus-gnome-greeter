import os
from gi.repository import Gio

class ThemeManager:
    def __init__(self):
        self.interface_settings = Gio.Settings.new("org.gnome.desktop.interface")
        try:
            # Try to access GNOME Shell theme settings (for accent colors)
            self.shell_settings = Gio.Settings.new("org.gnome.shell.extensions.user-theme")
        except:
            self.shell_settings = None
        
    def get_current_color_scheme(self):
        """Get current color scheme (default or prefer-dark)"""
        try:
            return self.interface_settings.get_string("color-scheme")
        except:
            return "default"
            
    def get_current_accent_color(self):
        """Get current accent color"""
        try:
            return self.interface_settings.get_string("accent-color")
        except:
            return "blue"  # Default accent color
        
    def get_current_gtk_theme(self):
        """Get current GTK theme"""
        try:
            return self.interface_settings.get_string("gtk-theme")
        except:
            return "Adwaita"
        
    def set_color_scheme(self, scheme):
        """Set color scheme (default or prefer-dark)"""
        try:
            self.interface_settings.set_string("color-scheme", scheme)
            return True
        except Exception as e:
            print(f"Error setting color scheme: {e}")
            return False
        
    def set_gtk_theme(self, theme):
        """Set GTK theme"""
        try:
            self.interface_settings.set_string("gtk-theme", theme)
            return True
        except Exception as e:
            print(f"Error setting GTK theme: {e}")
            return False
            
    def set_accent_color(self, color_name):
        """Set accent color using gsettings"""
        try:
            # Set accent color through gsettings
            self.interface_settings.set_string("accent-color", color_name)
            print(f"Successfully set accent color to: {color_name}")
            return True
                
        except Exception as e:
            print(f"Error setting accent color: {e}")
            return False
        
    def apply_light_theme(self):
        """Apply light theme"""
        success = True
        success &= self.set_color_scheme("default")
        success &= self.set_gtk_theme("Adwaita")
        return success
        
    def apply_dark_theme(self):
        """Apply dark theme"""
        success = True
        success &= self.set_color_scheme("prefer-dark")
        success &= self.set_gtk_theme("Adwaita")
        return success
        
    def is_dark_theme_active(self):
        """Check if dark theme is currently active"""
        try:
            color_scheme = self.get_current_color_scheme()
            return color_scheme == "prefer-dark"
        except:
            return False
                
    def is_light_theme_active(self):
        """Check if light theme is currently active"""
        try:
            color_scheme = self.get_current_color_scheme()
            return color_scheme in ["default", ""] or color_scheme is None
        except:
            return True  # Default to light
            
    def get_theme_info(self):
        """Get detailed theme information"""
        return {
            "color_scheme": self.get_current_color_scheme(),
            "gtk_theme": self.get_current_gtk_theme(),
            "accent_color": self.get_current_accent_color(),
            "is_dark": self.is_dark_theme_active(),
            "is_light": self.is_light_theme_active()
        } 