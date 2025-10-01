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

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/LiveWallpaperSourceRow.ui')
class LiveWallpaperSourceRow(Adw.ActionRow):
    __gtype_name__ = 'PardusLiveWallpaperSourceRow'
    
    # Define signals
    __gsignals__ = {
        'source-toggled': (GObject.SignalFlags.RUN_FIRST, None, (str, bool)),
        'download-requested': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'wallpaper-set-requested': (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
    }
    
    # Template children
    source_checkbox = Gtk.Template.Child("source_checkbox")
    preview_container = Gtk.Template.Child("preview_container")
    preview_image = Gtk.Template.Child("preview_image")
    download_button_row = Gtk.Template.Child("download_button_row")
    preview_button = Gtk.Template.Child("preview_button")
    action_button = Gtk.Template.Child("action_button")
    
    def __init__(self, source_id, source_info, **kwargs):
        super().__init__(**kwargs)
        
        self.source_id = source_id
        self.source_info = source_info
        self.wallpaper_data = None
        self.live_wallpaper_manager = None
        
        # Set basic info
        self.set_title(source_info['name'])
        self.set_subtitle(source_info['description'])
        
        # Connect signals
        self.source_checkbox.connect("toggled", self.on_checkbox_toggled)
        self.download_button_row.connect("clicked", self.on_download_button_clicked)
        self.preview_button.connect("clicked", self.on_preview_button_clicked)
        self.action_button.connect("clicked", self.on_action_button_clicked)
        
        # Initial button states - preview and action disabled until downloaded
        self.preview_button.set_sensitive(False)
        self.action_button.set_sensitive(False)
        
        # Preview click gesture
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self.on_preview_clicked)
        self.preview_container.add_controller(gesture)
        
        # Initial state
        self.set_status('loading')
    
    def set_live_wallpaper_manager(self, manager):
        """Set the live wallpaper manager reference"""
        self.live_wallpaper_manager = manager
    
    def set_wallpaper_data(self, wallpaper_data):
        """Set wallpaper data and update UI accordingly"""
        if wallpaper_data:
            self.set_status(wallpaper_data.status, wallpaper_data)
            
            # Update title and subtitle if they're different
            if wallpaper_data.title and wallpaper_data.title != self.source_info['name']:
                self.set_subtitle(f"{self.source_info['description']} - {wallpaper_data.title}")
        else:
            self.set_status('error')
    
    def set_download_progress(self, progress_percent):
        """Set download progress (0-100)"""
        if progress_percent >= 0 and progress_percent <= 100:
            self.action_button.set_tooltip_text(f"{_('Downloading...')} {progress_percent}%")
            
            # Optional: Add progress indication to icon or styling
            if progress_percent == 100:
                self.action_button.set_tooltip_text(_("Download complete"))
    
    def pulse_loading_animation(self):
        """Pulse the loading animation (for indefinite progress)"""
        # Status icon removed - no longer needed
        pass
    
    def set_checkbox_active(self, active):
        """Set checkbox state"""
        if self.source_checkbox:
            self.source_checkbox.set_active(active)
    
    def is_checkbox_active(self):
        """Get checkbox state"""
        if self.source_checkbox:
            return self.source_checkbox.get_active()
        return False
    
    # Status icon mapping
    STATUS_ICONS = {
        'pending': 'content-loading-symbolic',
        'loading': 'content-loading-symbolic',
        'downloading': 'folder-download-symbolic',
        'available': 'emblem-ok-symbolic',
        'error': 'dialog-error-symbolic'
    }
    
    # Action button icon mapping
    ACTION_ICONS = {
        'pending': 'folder-download-symbolic',
        'loading': 'folder-download-symbolic',
        'downloading': 'content-loading-symbolic',
        'available': 'media-playback-start-symbolic',
        'error': 'view-refresh-symbolic'
    }
    
    # CSS class mapping
    STATUS_CSS_CLASSES = {
        'pending': ['spinning'],
        'loading': ['spinning'],
        'downloading': ['spinning'],
        'available': ['success'],
        'error': ['error']
    }
    
    ACTION_CSS_CLASSES = {
        'pending': ['download'],
        'loading': ['download'],
        'downloading': [],
        'available': ['play'],
        'error': ['error']
    }
    
    def set_status(self, status, wallpaper_data=None):
        """Update status and UI elements"""
        self.wallpaper_data = wallpaper_data
        
        # Clear previous CSS classes
        self._clear_css_classes()
        
        # Apply status-specific styling
        self._apply_status_styling(status, wallpaper_data)
    
    def _clear_css_classes(self):
        """Clear all status-related CSS classes"""
        css_classes_to_clear = ['spinning', 'success', 'error', 'play', 'download']
        
        for css_class in css_classes_to_clear:
            self.action_button.remove_css_class(css_class)
    
    def _apply_status_styling(self, status, wallpaper_data):
        """Apply styling based on status"""
        # Set action button icon
        action_icon = self.ACTION_ICONS.get(status, 'folder-download-symbolic')
        self.action_button.set_icon_name(action_icon)
        
        # Apply action button CSS classes
        for css_class in self.ACTION_CSS_CLASSES.get(status, []):
            self.action_button.add_css_class(css_class)
        
        # Update download button based on status
        if status == 'available':
            self.update_button_states_after_download()
        elif status in ['downloading']:
            self.download_button_row.set_sensitive(False)
            self.download_button_row.set_tooltip_text(_("Downloading..."))
        
        # Set button sensitivity and tooltip
        self._set_button_state(status, wallpaper_data)
        
        # Load preview image if available
        if status == 'available' and wallpaper_data:
            self._load_preview_image(wallpaper_data)
    
    def _set_button_state(self, status, wallpaper_data):
        """Set button sensitivity and tooltip based on status"""
        tooltips = {
            'pending': _("Loading..."),
            'loading': _("Loading..."),
            'downloading': _("Downloading..."),
            'available': _("Set as wallpaper"),
            'error': _("Retry download")
        }
        
        # Button is disabled during loading/downloading
        sensitive = status not in ['pending', 'loading', 'downloading']
        self.action_button.set_sensitive(sensitive)
        
        # Set tooltip
        tooltip = tooltips.get(status, _("Unknown status"))
        self.action_button.set_tooltip_text(tooltip)
    
    def _load_preview_image(self, wallpaper_data):
        """Load preview image from file or URL with fallback handling"""
        try:
            # First try to load from local file
            if wallpaper_data.filepath and os.path.exists(wallpaper_data.filepath):
                self._load_image_from_file(wallpaper_data.filepath, wallpaper_data.title)
                return
            
            # If no local file, try to load thumbnail from URL in background
            if wallpaper_data.thumbnail_url and wallpaper_data.thumbnail_url.startswith('http'):
                self._load_thumbnail_from_url(wallpaper_data)
            else:
                # Set fallback image
                self._set_fallback_image(wallpaper_data.title)
                
        except Exception as e:
            print(f"Error loading preview for {self.source_id}: {e}")
            self._set_fallback_image(wallpaper_data.title, str(e))
    
    def _load_image_from_file(self, filepath, title):
        """Load image from local file with error handling"""
        try:
            # For GtkImage, use set_from_file instead of set_paintable
            self.preview_image.set_from_file(filepath)
            self.preview_image.set_tooltip_text(f"{title}\n{_('Click to set as wallpaper')}")
            
            # Add success styling
            self.preview_image.add_css_class("loaded")
            
        except Exception as e:
            print(f"Error loading image from {filepath}: {e}")
            self._set_fallback_image(title, str(e))
    
    def _set_fallback_image(self, title, error_msg=None):
        """Set fallback/placeholder image"""
        try:
            # For GtkImage, use set_from_icon_name instead of set_paintable
            self.preview_image.set_from_icon_name("image-x-generic-symbolic")
            
            # Set tooltip
            tooltip = f"{title}\n{_('Preview not available')}"
            if error_msg:
                tooltip += f"\n{_('Error')}: {error_msg}"
            self.preview_image.set_tooltip_text(tooltip)
            
            # Add fallback styling
            self.preview_image.add_css_class("fallback")
            
        except Exception as e:
            print(f"Error setting fallback image: {e}")
            # Last resort: just set tooltip
            self.preview_image.set_tooltip_text(f"{title}\n{_('Preview not available')}")
    
    def _load_thumbnail_from_url(self, wallpaper_data):
        """Load thumbnail from URL in background thread with caching"""
        # Show loading state
        self.preview_image.add_css_class("loading")
        
        def download_thumbnail():
            try:
                import requests
                import hashlib
                
                # Create cache directory
                cache_dir = os.path.expanduser("~/.cache/pardus-gnome-greeter/thumbnails")
                os.makedirs(cache_dir, exist_ok=True)
                
                # Generate cache filename based on URL hash
                url_hash = hashlib.md5(wallpaper_data.thumbnail_url.encode()).hexdigest()
                cache_path = os.path.join(cache_dir, f"{self.source_id}_{url_hash}.jpg")
                
                # Check if cached version exists and is recent (less than 1 day old)
                if os.path.exists(cache_path):
                    cache_age = time.time() - os.path.getmtime(cache_path)
                    if cache_age < 86400:  # 24 hours
                        GLib.idle_add(self._set_thumbnail_from_file, cache_path, wallpaper_data.title, False)
                        return
                
                # Download thumbnail
                headers = {'User-Agent': 'PardusGnomeGreeter/1.0'}
                response = requests.get(wallpaper_data.thumbnail_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Save to cache
                    with open(cache_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Load in main thread
                    GLib.idle_add(self._set_thumbnail_from_file, cache_path, wallpaper_data.title, False)
                else:
                    GLib.idle_add(self._set_fallback_image, wallpaper_data.title, f"HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"Error downloading thumbnail for {self.source_id}: {e}")
                GLib.idle_add(self._set_fallback_image, wallpaper_data.title, str(e))
        
        # Start download in background
        threading.Thread(target=download_thumbnail, daemon=True).start()
    
    def _set_thumbnail_from_file(self, filepath, title, cleanup=True):
        """Set thumbnail from file (called in main thread)"""
        try:
            if os.path.exists(filepath):
                # Remove loading state
                self.preview_image.remove_css_class("loading")
                
                # Load and set image using GtkImage method
                self.preview_image.set_from_file(filepath)
                self.preview_image.set_tooltip_text(f"{title}\n{_('Click to set as wallpaper')}")
                
                # Add loaded styling
                self.preview_image.add_css_class("loaded")
                
                # Clean up temp file if requested
                if cleanup:
                    try:
                        os.unlink(filepath)
                    except:
                        pass  # Ignore cleanup errors
            else:
                self._set_fallback_image(title, "File not found")
                
        except Exception as e:
            print(f"Error setting thumbnail: {e}")
            self._set_fallback_image(title, str(e))
        
        return False  # Don't repeat this idle callback
    
    def on_checkbox_toggled(self, checkbox):
        """Handle checkbox toggle"""
        # Emit custom signal for parent to handle
        self.emit("source-toggled", self.source_id, checkbox.get_active())
    
    def on_action_button_clicked(self, button):
        """Handle action button click"""
        current_status = self.wallpaper_data.status if self.wallpaper_data else 'pending'
        
        if current_status == 'available' and self.wallpaper_data:
            # Set as wallpaper (play button functionality)
            self.emit("wallpaper-set-requested", self.source_id, self.wallpaper_data.filepath)
            
            # Provide visual feedback
            self._show_action_feedback("Setting wallpaper...")
            
        elif current_status in ['pending', 'error']:
            # Download/retry (download button functionality)
            self.emit("download-requested", self.source_id)
            
            # Update to downloading state immediately for better UX
            self.set_status('downloading')
            
        # Note: downloading state buttons are disabled, so no action needed
    
    def _show_action_feedback(self, message):
        """Show temporary feedback message"""
        original_tooltip = self.action_button.get_tooltip_text()
        self.action_button.set_tooltip_text(message)
        
        # Restore original tooltip after 2 seconds
        def restore_tooltip():
            self.action_button.set_tooltip_text(original_tooltip)
            return False
        
        GLib.timeout_add_seconds(2, restore_tooltip)
    
    def on_preview_clicked(self, gesture, n_press, x, y):
        """Handle preview image click"""
        if self.wallpaper_data and self.wallpaper_data.status == 'available':
            self.emit("wallpaper-set-requested", self.source_id, self.wallpaper_data.filepath)

    def on_preview_button_clicked(self, button):
        """Handle preview button click - show modal dialog"""
        print(f"Preview button clicked for {self.source_id}")
        
        # Import the dialog class
        try:
            from .WallpaperPreviewDialog import WallpaperPreviewDialog
            
            # Create and show the dialog
            dialog = WallpaperPreviewDialog(
                source_id=self.source_id,
                source_info=self.source_info,
                wallpaper_data=self.wallpaper_data
            )
            
            # Get the parent window
            parent_window = self.get_root()
            if parent_window:
                dialog.present(parent_window)
            else:
                dialog.present()
                
        except ImportError as e:
            print(f"Error importing WallpaperPreviewDialog: {e}")
            # Fallback: just print info
            print(f"Would show preview for: {self.source_info['name']}")
            if self.wallpaper_data:
                print(f"Status: {self.wallpaper_data.status}")
                print(f"File: {getattr(self.wallpaper_data, 'filepath', 'N/A')}")    

    def on_download_button_clicked(self, button):
        """Handle download button click"""
        print(f"Download button clicked for {self.source_id}")
        
        # Trigger download
        self.emit("download-requested", self.source_id)
        
        # Update button states
        self.download_button_row.set_sensitive(False)
        self.download_button_row.set_tooltip_text(_("Downloading..."))
        
        # Enable other buttons after download completes
        # This will be handled in set_wallpaper_data when status becomes 'available'
    
    def update_button_states_after_download(self):
        """Update button states after successful download"""
        self.download_button_row.set_sensitive(False)
        self.download_button_row.set_tooltip_text(_("Downloaded"))
        self.preview_button.set_sensitive(True)
        self.action_button.set_sensitive(True)