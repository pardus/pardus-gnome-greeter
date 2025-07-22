import gi
import threading
import os
import sys

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, GdkPixbuf

# Add the managers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'managers'))
from WallpaperManager import WallpaperManager

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/WallpaperPage.ui')
class WallpaperPage(Adw.PreferencesPage):
    __gtype_name__ = 'WallpaperPage'
    
    # Template children
    current_wallpaper_row = Gtk.Template.Child("current_wallpaper_row")
    current_wallpaper_preview = Gtk.Template.Child("current_wallpaper_preview")
    wallpapers_scrolled = Gtk.Template.Child("wallpapers_scrolled")
    wallpapers_flowbox = Gtk.Template.Child("wallpapers_flowbox")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize wallpaper manager
        self.wallpaper_manager = WallpaperManager()
        self.wallpapers = []
        self.current_selection = None
        
        # Connect signals
        self.wallpapers_flowbox.connect("child-activated", self.on_wallpaper_selected)
        
        # Load current wallpaper info
        GLib.idle_add(self.update_current_wallpaper_info)
        
        # Load wallpapers in background thread
        thread = threading.Thread(target=self.load_wallpapers_background)
        thread.daemon = True
        thread.start()
        
    def update_current_wallpaper_info(self):
        """Update the current wallpaper display"""
        try:
            current_wallpaper = self.wallpaper_manager.get_current_wallpaper()
            if current_wallpaper and os.path.exists(current_wallpaper):
                name = self.wallpaper_manager.get_wallpaper_name(current_wallpaper)
                self.current_wallpaper_row.set_subtitle(name)
                
                # Create small preview
                try:
                    pixbuf = self.wallpaper_manager.create_thumbnail(current_wallpaper, 48, 32)
                    if pixbuf:
                        self.current_wallpaper_preview.set_from_pixbuf(pixbuf)
                except Exception as e:
                    print(f"Error creating current wallpaper preview: {e}")
            else:
                self.current_wallpaper_row.set_subtitle("No wallpaper set")
        except Exception as e:
            print(f"Error updating current wallpaper info: {e}")
            self.current_wallpaper_row.set_subtitle("Error loading current wallpaper")
            
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
            pixbuf = self.wallpaper_manager.create_thumbnail(wallpaper_path, 160, 90)
            if pixbuf:
                GLib.idle_add(self.add_wallpaper_to_flowbox, wallpaper_path, pixbuf, current_wallpaper)
        except Exception as e:
            print(f"Error creating thumbnail for {wallpaper_path}: {e}")
            
    def add_wallpaper_to_flowbox(self, wallpaper_path, pixbuf, current_wallpaper):
        """Add wallpaper thumbnail to the flowbox"""
        try:
            # Create container box (like old implementation)
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            container.set_margin_top(8)
            container.set_margin_bottom(8)
            container.set_margin_start(8)
            container.set_margin_end(8)
            
            # Create image (like old implementation)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            image.set_halign(Gtk.Align.CENTER)
            image.set_valign(Gtk.Align.CENTER)
            image.set_size_request(160, 90)
            
            # Create frame for image
            frame = Gtk.Frame()
            frame.set_child(image)
            frame.add_css_class("card")
            frame.add_css_class("wallpaper-thumbnail")
            frame.set_size_request(160  , 90)
            
            # Create label for wallpaper name
            name = self.wallpaper_manager.get_wallpaper_name(wallpaper_path)
            label = Gtk.Label(label=name)
            label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
            label.set_max_width_chars(20)
            label.add_css_class("caption")
            
            # Add to container
            container.append(frame)
            container.append(label)
            
            # Create FlowBoxChild (like old implementation)
            child = Gtk.FlowBoxChild()
            child.set_child(container)
            
            # Store wallpaper path as data
            child.wallpaper_path = wallpaper_path
            
            # Add selection styling if this is current wallpaper
            if current_wallpaper and wallpaper_path == current_wallpaper:
                frame.add_css_class("selected")
                self.current_selection = child
                self.wallpapers_flowbox.select_child(child)
            
            # Add to FlowBox (like old implementation)
            self.wallpapers_flowbox.append(child)
                
        except Exception as e:
            print(f"Error adding wallpaper to flowbox: {e}")
            

        
    def on_wallpaper_selected(self, flowbox, flowbox_child):
        """Handle wallpaper selection (like old implementation)"""
        try:
            if not hasattr(flowbox_child, 'wallpaper_path'):
                return
                
            wallpaper_path = flowbox_child.wallpaper_path
            
            # Update selection styling
            if self.current_selection:
                # Remove selected class from previous selection
                container = self.current_selection.get_child()
                if container and container.get_first_child():
                    frame = container.get_first_child()
                    frame.remove_css_class("selected")
            
            # Add selected class to new selection
            container = flowbox_child.get_child()
            if container and container.get_first_child():
                frame = container.get_first_child()
                frame.add_css_class("selected")
            
            self.current_selection = flowbox_child
            
            # Set wallpaper
            success = self.wallpaper_manager.set_wallpaper(wallpaper_path)
            if success:
                print(f"Wallpaper changed to: {wallpaper_path}")
                # Update current wallpaper info
                GLib.idle_add(self.update_current_wallpaper_info)
            else:
                print(f"Failed to set wallpaper: {wallpaper_path}")
                
        except Exception as e:
            print(f"Error setting wallpaper: {e}") 