import os
import glob
from gi.repository import Gio, GdkPixbuf, GLib
from pathlib import Path

class WallpaperManager:
    def __init__(self):
        self.background_settings = Gio.Settings.new("org.gnome.desktop.background")
        
        # Common wallpaper directories
        self.wallpaper_dirs = [
            "/usr/share/backgrounds",
        ]
        
        # Supported image formats
        self.supported_formats = {
            "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp", "*.svg"
        }
        
    def get_current_wallpaper(self):
        """Get current wallpaper URI"""
        try:
            # Check color scheme to get appropriate wallpaper
            interface_settings = Gio.Settings.new("org.gnome.desktop.interface")
            color_scheme = interface_settings.get_string("color-scheme")
            
            if color_scheme == "prefer-dark":
                uri = self.background_settings.get_string("picture-uri-dark")
            else:
                uri = self.background_settings.get_string("picture-uri")
                
            # Remove file:// prefix if present
            if uri.startswith("file://"):
                uri = uri[7:]
            return uri
        except Exception as e:
            print(f"Error getting current wallpaper: {e}")
            return None
            
    def set_wallpaper(self, file_path):
        """Set wallpaper for both light and dark themes"""
        try:
            uri = f"file://{file_path}"
            self.background_settings.set_string("picture-uri", uri)
            self.background_settings.set_string("picture-uri-dark", uri)
            return True
        except Exception as e:
            print(f"Error setting wallpaper: {e}")
            return False
            
    def get_wallpapers(self):
        """Get list of available wallpapers"""
        wallpapers = []
        
        for directory in self.wallpaper_dirs:
            if not os.path.exists(directory):
                continue
                
            for format_ext in self.supported_formats:
                pattern = os.path.join(directory, "**", format_ext)
                files = glob.glob(pattern, recursive=True)
                wallpapers.extend(files)
        
        # Remove duplicates and sort
        wallpapers = list(set(wallpapers))
        wallpapers.sort()
        
        return wallpapers
    
    def create_thumbnail(self, file_path, width=200, height=130):
        """Create thumbnail for wallpaper preview"""
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
            
            # Scale while maintaining aspect ratio
            original_width = pixbuf.get_width()
            original_height = pixbuf.get_height()
            
            # Calculate scaling factor
            scale_x = width / original_width
            scale_y = height / original_height
            scale = min(scale_x, scale_y)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            scaled_pixbuf = pixbuf.scale_simple(
                new_width, new_height, 
                GdkPixbuf.InterpType.BILINEAR
            )
            
            return scaled_pixbuf
        except Exception as e:
            print(f"Error creating thumbnail for {file_path}: {e}")
            return None
            
    def get_wallpaper_name(self, file_path):
        """Get display name for wallpaper"""
        return os.path.splitext(os.path.basename(file_path))[0] 