import locale
import gi
import threading
import os
import sys
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Gdk

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

# Add the managers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'managers'))
from WallpaperManager import WallpaperManager

# WallpaperThumbnail template class
@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/WallpaperThumbnail.ui')
class WallpaperThumbnail(Gtk.Box):
    __gtype_name__ = 'WallpaperThumbnail'
    
    # Template children
    picture = Gtk.Template.Child("picture")
    
    def __init__(self):
        super().__init__()
        
        # Set size request
        self.picture.set_size_request(160, 120)
        
        # Selection state
        self._selected = False
    
    def load_wallpaper(self, wallpaper_path):
        """Load wallpaper from file path"""
        try:
            if os.path.exists(wallpaper_path):
                texture = Gdk.Texture.new_from_filename(wallpaper_path)
                self.picture.set_paintable(texture)
        except Exception as e:
            print(f"Error loading wallpaper {wallpaper_path}: {e}")
    
    def load_pixbuf(self, pixbuf):
        """Load wallpaper from GdkPixbuf"""
        try:
            if pixbuf:
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                self.picture.set_paintable(texture)
        except Exception as e:
            print(f"Error loading pixbuf: {e}")
    
    def set_selected(self, selected):
        """Set selection state"""
        self._selected = selected
        if selected:
            self.add_css_class("selected")
        else:
            self.remove_css_class("selected")
    
    def is_selected(self):
        """Get selection state"""
        return self._selected

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/WallpaperPage.ui')
class WallpaperPage(Adw.PreferencesPage):
    __gtype_name__ = 'WallpaperPage'
    
    # Template children
    wallpapers_flowbox = Gtk.Template.Child("wallpapers_flowbox")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize wallpaper manager
        self.wallpaper_manager = WallpaperManager()
        self.wallpapers = []
        self.current_selection = None
        
        # Connect signals
        self.wallpapers_flowbox.connect("child-activated", self.on_wallpaper_selected)
        
        # Load wallpapers in background thread
        thread = threading.Thread(target=self.load_wallpapers_background)
        thread.daemon = True
        thread.start()
        
    def load_wallpapers_background(self):
        """Load wallpapers in background thread"""
        try:
            self.wallpapers = self.wallpaper_manager.get_wallpapers()
            GLib.idle_add(self.populate_wallpapers_ui)
        except Exception as e:
            print(f"Error loading wallpapers: {e}")
            
    def populate_wallpapers_ui(self):
        """Populate the UI with wallpaper thumbnails"""
        try:
            if not self.wallpapers:
                print("No wallpapers found")
                return
            
            # Get current wallpaper for selection
            current_wallpaper = self.wallpaper_manager.get_current_wallpaper()
            
            # Create wallpaper thumbnails in smaller batches
            batch_size = 5
            total_wallpapers = len(self.wallpapers)
            
            for i in range(0, total_wallpapers, batch_size):
                batch = self.wallpapers[i:i + batch_size]
                GLib.idle_add(self.create_wallpaper_batch, batch, current_wallpaper)
                
        except Exception as e:
            print(f"Error populating wallpapers UI: {e}")
            
    def create_wallpaper_batch(self, wallpaper_batch, current_wallpaper):
        """Create a batch of wallpaper thumbnails"""
        for wallpaper_path in wallpaper_batch:
            try:
                # Create thumbnail in a separate thread
                thread = threading.Thread(
                    target=self.create_wallpaper_thumbnail,
                    args=(wallpaper_path, current_wallpaper)
                )
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"Error creating thumbnail thread for {wallpaper_path}: {e}")
                
    def create_wallpaper_thumbnail(self, wallpaper_path, current_wallpaper):
        """Create thumbnail for a single wallpaper"""
        try:
            pixbuf = self.wallpaper_manager.create_thumbnail(wallpaper_path, 160, 120)
            if pixbuf:
                GLib.idle_add(self.add_wallpaper_to_flowbox, wallpaper_path, pixbuf, current_wallpaper)
        except Exception as e:
            print(f"Error creating thumbnail for {wallpaper_path}: {e}")
            
    def add_wallpaper_to_flowbox(self, wallpaper_path, pixbuf, current_wallpaper):
        """Add wallpaper thumbnail to the flowbox"""
        try:
            # Create wallpaper thumbnail component
            thumbnail = WallpaperThumbnail()
            
            # Load the pixbuf if available
            if pixbuf:
                thumbnail.load_pixbuf(pixbuf)
            else:
                thumbnail.load_wallpaper(wallpaper_path)
            
            child = Gtk.FlowBoxChild()
            child.set_child(thumbnail)
            child.wallpaper_path = wallpaper_path
            
            if current_wallpaper and wallpaper_path == current_wallpaper:
                thumbnail.set_selected(True)
                self.current_selection = child
                self.wallpapers_flowbox.select_child(child)
            
            self.wallpapers_flowbox.append(child)
                
        except Exception as e:
            print(f"Error adding wallpaper to flowbox: {e}")

    def on_wallpaper_selected(self, flowbox, flowbox_child):
        """Handle wallpaper selection"""
        try:
            if not hasattr(flowbox_child, 'wallpaper_path'):
                return
                
            wallpaper_path = flowbox_child.wallpaper_path
            
            if self.current_selection:
                prev_thumbnail = self.current_selection.get_child()
                if prev_thumbnail and hasattr(prev_thumbnail, 'set_selected'):
                    prev_thumbnail.set_selected(False)
            
            new_thumbnail = flowbox_child.get_child()
            if new_thumbnail and hasattr(new_thumbnail, 'set_selected'):
                new_thumbnail.set_selected(True)
            
            self.current_selection = flowbox_child
            
            success = self.wallpaper_manager.set_wallpaper(wallpaper_path)
            if success:
                print(f"Wallpaper changed to: {wallpaper_path}")
            else:
                print(f"Failed to set wallpaper: {wallpaper_path}")
                
        except Exception as e:
            print(f"Error setting wallpaper: {e}") 