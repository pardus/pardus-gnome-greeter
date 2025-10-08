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
from ..managers.WallpaperManager import WallpaperManager

# WallpaperThumbnail template class
@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/WallpaperThumbnail.ui')
class WallpaperThumbnail(Gtk.Box):
    __gtype_name__ = 'WallpaperThumbnail'
    
    # Template children
    picture = Gtk.Template.Child("picture")
    selected_check = Gtk.Template.Child("selected_check")
    
    def __init__(self):
        super().__init__()
        
        # Set size request
        self.picture.set_size_request(160, 120)
        
        # Selection state
        self._selected = False
        
        # Initially hide checkmark
        self.selected_check.set_opacity(0)
    
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
        
        # Show/hide checkmark
        if selected:
            self.selected_check.set_opacity(1)
        else:
            self.selected_check.set_opacity(0)
    
    def is_selected(self):
        """Get selection state"""
        return self._selected

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/WallpaperPage.ui')
class WallpaperPage(Adw.PreferencesPage):
    __gtype_name__ = 'WallpaperPage'
    
    # Template children
    live_wallpaper_row = Gtk.Template.Child("live_wallpaper_row")
    wallpapers_flowbox = Gtk.Template.Child("wallpapers_flowbox")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize manager
        self.wallpaper_manager = WallpaperManager()
        self.wallpapers = []
        self.current_selection = None
        
        # Connect signals
        if self.live_wallpaper_row:
            self.live_wallpaper_row.connect("activated", self.on_live_wallpaper_clicked)
        if self.wallpapers_flowbox:
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
            
            # Create wallpaper thumbnails in batches
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
            if not self.wallpapers_flowbox:
                print("Wallpapers flowbox not found")
                return
                
            thumbnail = WallpaperThumbnail()
            
            if pixbuf:
                thumbnail.load_pixbuf(pixbuf)
            else:
                thumbnail.load_wallpaper(wallpaper_path)
            
            child = Gtk.FlowBoxChild()
            child.set_child(thumbnail)
            child.wallpaper_path = wallpaper_path
            child.thumbnail = thumbnail
            
            # Set initial selection state
            if current_wallpaper and wallpaper_path == current_wallpaper:
                child.add_css_class('active-item')
                thumbnail.set_selected(True)
                self.current_selection = child
            
            self.wallpapers_flowbox.append(child)
                
        except Exception as e:
            print(f"Error adding wallpaper to flowbox: {e}")

    def on_wallpaper_selected(self, flowbox, flowbox_child):
        """Handle wallpaper selection - GNOME Control Center style"""
        try:
            if not hasattr(flowbox_child, 'wallpaper_path'):
                return
                
            wallpaper_path = flowbox_child.wallpaper_path
            
            # Remove active-item class from previous selection
            if self.current_selection:
                self.current_selection.remove_css_class('active-item')
                if hasattr(self.current_selection, 'thumbnail'):
                    self.current_selection.thumbnail.set_selected(False)
            
            # Add active-item class to new selection
            flowbox_child.add_css_class('active-item')
            if hasattr(flowbox_child, 'thumbnail'):
                flowbox_child.thumbnail.set_selected(True)
            
            self.current_selection = flowbox_child
            
            # Set wallpaper immediately (like GNOME Control Center)
            success = self.wallpaper_manager.set_wallpaper(wallpaper_path)
            if success:
                print(f"Wallpaper changed to: {wallpaper_path}")
            else:
                print(f"Failed to set wallpaper: {wallpaper_path}")
                
        except Exception as e:
            print(f"Error setting wallpaper: {e}")
    
    def on_live_wallpaper_clicked(self, row):
        """Handle Pardus Live Wallpaper button click"""
        try:
            # Try to open extension preferences
            # First check if extension is installed
            extension_uuid = "pardus-wallpaper-extension@pardus.org.tr"
            
            # Try to open extension preferences using gnome-extensions
            result = os.system(f"gnome-extensions prefs {extension_uuid} 2>/dev/null")
            
            if result != 0:
                # Extension not found, show info dialog
                dialog = Adw.MessageDialog.new(
                    self.get_root(),
                    _("Extension Not Found"),
                    _("Pardus Live Wallpaper extension is not installed. Please install it from GNOME Extensions.")
                )
                dialog.add_response("ok", _("OK"))
                dialog.set_default_response("ok")
                dialog.set_close_response("ok")
                dialog.present()
                
        except Exception as e:
            print(f"Error opening live wallpaper settings: {e}")
