import os
from .settings import theme_settings, shell_settings

class ThemeManager:
    def __init__(self):
        # Callback system for theme changes
        self.accent_color_callbacks = []
        
    def add_accent_color_callback(self, callback):
        """Add a callback to be called when accent color changes"""
        self.accent_color_callbacks.append(callback)
        
    def notify_accent_color_change(self, color_name):
        """Notify all callbacks of accent color change"""
        for callback in self.accent_color_callbacks:
            try:
                callback(color_name)
            except Exception as e:
                print(f"Error in accent color callback: {e}")
        
    def get_current_color_scheme(self):
        """Get current color scheme (default or prefer-dark)"""
        try:
            return theme_settings.get("color-scheme")
        except:
            return "default"
            
    def get_current_accent_color(self):
        """Get current accent color"""
        try:
            return theme_settings.get("accent-color")
        except:
            return "blue"  # Default accent color
        
    def get_current_gtk_theme(self):
        """Get current GTK theme"""
        try:
            return theme_settings.get("gtk-theme")
        except:
            return "Adwaita"

    def get_current_icon_theme(self):
        """Get current icon theme"""
        try:
            return theme_settings.get("icon-theme")
        except:
            return "Adwaita"
        
    def set_color_scheme(self, scheme):
        """Set color scheme (default or prefer-dark)"""
        try:
            theme_settings.set("color-scheme", scheme)
            return True
        except Exception as e:
            print(f"Error setting color scheme: {e}")
            return False
        
    def set_gtk_theme(self, theme):
        """Set GTK theme"""
        try:
            theme_settings.set("gtk-theme", theme)
            return True
        except Exception as e:
            print(f"Error setting GTK theme: {e}")
            return False

    def set_icon_theme(self, theme):
        """Set icon theme"""
        try:
            theme_settings.set("icon-theme", theme)
            return True
        except Exception as e:
            print(f"Error setting icon theme: {e}")
            return False
            
    def set_accent_color(self, color_name):
        """Set accent color using gsettings"""
        try:
            # Set accent color through gsettings
            theme_settings.set("accent-color", color_name)
            print(f"Successfully set accent color to: {color_name}")
            
            # Notify callbacks
            self.notify_accent_color_change(color_name)
            
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
            "icon_theme": self.get_current_icon_theme(),
            "accent_color": self.get_current_accent_color(),
            "is_dark": self.is_dark_theme_active(),
            "is_light": self.is_light_theme_active()
        } 