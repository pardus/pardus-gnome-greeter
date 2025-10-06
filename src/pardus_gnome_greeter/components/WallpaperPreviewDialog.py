import locale
import gi
import os
import threading
import time
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gdk, GObject

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/WallpaperPreviewDialog.ui')
class WallpaperPreviewDialog(Adw.Dialog):
    __gtype_name__ = 'PardusWallpaperPreviewDialog'
    
    # Template children
    header_bar = Gtk.Template.Child("header_bar")
    window_title = Gtk.Template.Child("window_title")
    set_wallpaper_button = Gtk.Template.Child("set_wallpaper_button")
    loading_spinner = Gtk.Template.Child("loading_spinner")
    preview_image = Gtk.Template.Child("preview_image")
    error_container = Gtk.Template.Child("error_container")
    error_label = Gtk.Template.Child("error_label")
    retry_button = Gtk.Template.Child("retry_button")
    wallpaper_title = Gtk.Template.Child("wallpaper_title")
    wallpaper_description = Gtk.Template.Child("wallpaper_description")
    source_label = Gtk.Template.Child("source_label")
    date_label = Gtk.Template.Child("date_label")
    
    def __init__(self, source_id, source_info, wallpaper_data=None, **kwargs):
        super().__init__(**kwargs)
        
        self.source_id = source_id
        self.source_info = source_info
        self.wallpaper_data = wallpaper_data
        
        # Connect signals
        self.set_wallpaper_button.connect("clicked", self.on_set_wallpaper_clicked)
        self.retry_button.connect("clicked", self.on_retry_clicked)
        
        # Initialize UI
        self.setup_ui()
        self.load_preview()
    
    def setup_ui(self):
        """Setup initial UI state"""
        # Set title and subtitle - use wallpaper data if available
        if self.wallpaper_data and hasattr(self.wallpaper_data, 'title') and self.wallpaper_data.title:
            # Use actual wallpaper title
            self.window_title.set_title(self.wallpaper_data.title)
            self.wallpaper_title.set_text(self.wallpaper_data.title)
        else:
            # Fallback to source name
            self.window_title.set_title(self.source_info['name'])
            self.wallpaper_title.set_text(self.source_info['name'])
        
        # Set subtitle to source name
        self.window_title.set_subtitle(self.source_info['name'])
        
        # Set wallpaper description - use wallpaper data if available
        if self.wallpaper_data and hasattr(self.wallpaper_data, 'description') and self.wallpaper_data.description:
            self.wallpaper_description.set_text(self.wallpaper_data.description)
        elif self.wallpaper_data and hasattr(self.wallpaper_data, 'copyright') and self.wallpaper_data.copyright:
            # Some sources use 'copyright' field for description
            self.wallpaper_description.set_text(self.wallpaper_data.copyright)
        else:
            # Fallback to source description
            self.wallpaper_description.set_text(self.source_info['description'])
        
        # Set source info
        self.source_label.set_text(self.source_info['name'])
        
        # Set date - use wallpaper date if available
        if self.wallpaper_data and hasattr(self.wallpaper_data, 'date') and self.wallpaper_data.date:
            # Convert date to string if it's a datetime object
            if hasattr(self.wallpaper_data.date, 'strftime'):
                date_str = self.wallpaper_data.date.strftime("%B %d, %Y")
            else:
                date_str = str(self.wallpaper_data.date)
            self.date_label.set_text(date_str)
        else:
            # Fallback to current date
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            self.date_label.set_text(current_date)
        
        # Initial button state
        self.set_wallpaper_button.set_sensitive(True)
    
    def load_preview(self):
        """Load wallpaper preview"""
        self.show_loading_state()
        
        if not self.wallpaper_data:
            self.show_error_state(_("No wallpaper data available"))
            return
        
        # Debug: Print available wallpaper data fields
        print(f"Wallpaper data fields for {self.source_id}:")
        for attr in dir(self.wallpaper_data):
            if not attr.startswith('_'):
                value = getattr(self.wallpaper_data, attr)
                if not callable(value):
                    print(f"  {attr}: {value}")
        
        # Try to load from local file first
        if (hasattr(self.wallpaper_data, 'filepath') and 
            self.wallpaper_data.filepath and 
            os.path.exists(self.wallpaper_data.filepath)):
            self.load_image_from_file(self.wallpaper_data.filepath)
        else:
            # Try different URL fields that APIs might provide
            image_url = None
            
            # Check for various URL field names
            url_fields = ['url', 'image_url', 'hd_url', 'full_url', 'download_url', 'hdurl']
            for field in url_fields:
                if (hasattr(self.wallpaper_data, field) and 
                    getattr(self.wallpaper_data, field) and 
                    str(getattr(self.wallpaper_data, field)).startswith('http')):
                    image_url = getattr(self.wallpaper_data, field)
                    break
            
            if image_url:
                self.load_image_from_url(image_url)
            else:
                self.show_error_state(_("No image source available"))
    
    def load_image_from_file(self, filepath):
        """Load image from local file"""
        try:
            # Check if file is a supported image format
            supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext not in supported_extensions:
                self.show_error_state(f"{_('Unsupported file format')}: {file_ext}\n{_('Only image files are supported')}")
                return
            
            texture = Gdk.Texture.new_from_filename(filepath)
            self.preview_image.set_paintable(texture)
            self.show_image_state()
            
            # Button already enabled by default
            
        except Exception as e:
            print(f"Error loading image from file: {e}")
            self.show_error_state(f"{_('Failed to load image')}: {str(e)}")
    
    def load_image_from_url(self, url):
        """Load image from URL in background thread"""
        def download_and_load():
            try:
                import requests
                
                # Download image
                headers = {'User-Agent': 'PardusGnomeGreeter/1.0'}
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    # Create temporary file
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(response.content)
                        tmp_filepath = tmp_file.name
                    
                    # Load in main thread
                    GLib.idle_add(self.load_image_from_file, tmp_filepath)
                    
                    # Clean up temp file after a delay
                    def cleanup():
                        try:
                            os.unlink(tmp_filepath)
                        except:
                            pass
                        return False
                    
                    GLib.timeout_add_seconds(5, cleanup)
                    
                else:
                    GLib.idle_add(self.show_error_state, f"{_('Download failed')}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"Error downloading image: {e}")
                GLib.idle_add(self.show_error_state, f"{_('Download failed')}: {str(e)}")
        
        # Start download in background
        threading.Thread(target=download_and_load, daemon=True).start()
    
    def show_loading_state(self):
        """Show loading spinner"""
        self.loading_spinner.set_visible(True)
        self.loading_spinner.set_spinning(True)
        self.preview_image.set_visible(False)
        self.error_container.set_visible(False)
    
    def show_image_state(self):
        """Show loaded image"""
        self.loading_spinner.set_visible(False)
        self.loading_spinner.set_spinning(False)
        self.preview_image.set_visible(True)
        self.error_container.set_visible(False)
    
    def show_error_state(self, error_message):
        """Show error state"""
        self.loading_spinner.set_visible(False)
        self.loading_spinner.set_spinning(False)
        self.preview_image.set_visible(False)
        self.error_container.set_visible(True)
        self.error_label.set_text(error_message)
        
        # Keep set wallpaper button enabled
    

    def on_set_wallpaper_clicked(self, button):
        """Handle set wallpaper button click"""
        print(f"Set wallpaper requested for {self.source_id}")
        # TODO: Implement set wallpaper functionality
        
        # Close dialog after setting wallpaper
        self.close()
    
    def on_retry_clicked(self, button):
        """Handle retry button click"""
        self.load_preview()    

    def on_preview_clicked(self, button):
        """Handle preview button click - zoom/fullscreen functionality"""
        print(f"Preview clicked for {self.source_id}")
        # TODO: Implement fullscreen preview or zoom functionality    

    def update_wallpaper_info(self, wallpaper_data):
        """Update UI with fresh wallpaper data"""
        self.wallpaper_data = wallpaper_data
        
        if wallpaper_data:
            # Update title if available
            if hasattr(wallpaper_data, 'title') and wallpaper_data.title:
                self.window_title.set_title(wallpaper_data.title)
                self.wallpaper_title.set_text(wallpaper_data.title)
            
            # Update description if available
            if hasattr(wallpaper_data, 'description') and wallpaper_data.description:
                self.wallpaper_description.set_text(wallpaper_data.description)
            elif hasattr(wallpaper_data, 'copyright') and wallpaper_data.copyright:
                self.wallpaper_description.set_text(wallpaper_data.copyright)
            
            # Update date if available
            if hasattr(wallpaper_data, 'date') and wallpaper_data.date:
                # Convert date to string if it's a datetime object
                if hasattr(wallpaper_data.date, 'strftime'):
                    date_str = wallpaper_data.date.strftime("%B %d, %Y")
                else:
                    date_str = str(wallpaper_data.date)
                self.date_label.set_text(date_str)
            
            # Reload preview with new data
            self.load_preview()