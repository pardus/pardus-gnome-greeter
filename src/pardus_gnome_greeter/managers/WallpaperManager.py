import os
import glob
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, GLib
from pathlib import Path
from .settings import background_settings, theme_settings

class WallpaperManager:
    def __init__(self):
        # Common wallpaper directories
        self.wallpaper_dirs = [
            "/usr/share/backgrounds"
        ]
        
        # Supported image formats
        self.supported_formats = {
            "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp", "*.svg"
        }
        
    def get_current_wallpaper(self):
        """Get current wallpaper URI"""
        try:
            # Check color scheme to get appropriate wallpaper
            color_scheme = theme_settings.get("color-scheme")
            
            if color_scheme == "prefer-dark":
                uri = background_settings.get("picture-uri-dark")
            else:
                uri = background_settings.get("picture-uri")
                
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
            if not os.path.exists(file_path):
                print(f"Wallpaper file does not exist: {file_path}")
                return False
            
            uri = f"file://{file_path}"
            result1 = background_settings.set("picture-uri", uri)
            result2 = background_settings.set("picture-uri-dark", uri)
            
            if result1 is False or result2 is False:
                print(f"Failed to set wallpaper settings for: {file_path}")
                return False
            
            print(f"Wallpaper set successfully: {file_path}")
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
    
    def create_thumbnail(self, file_path, width=160, height=120):
        """Create thumbnail for wallpaper preview"""
        try:
            # Load the original image
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
            
            # Scale to exact dimensions (stretch to fit)
            scaled_pixbuf = pixbuf.scale_simple(
                width, height, 
                GdkPixbuf.InterpType.BILINEAR
            )
            
            return scaled_pixbuf
        except Exception as e:
            print(f"Error creating thumbnail for {file_path}: {e}")
            return None
            
    def get_wallpaper_name(self, file_path):
        """Get display name for wallpaper"""
        return os.path.splitext(os.path.basename(file_path))[0] 