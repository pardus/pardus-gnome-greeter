import locale
import gi
import threading
import os
import sys
import json
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio, GdkPixbuf, Gdk

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

# Add the managers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'managers'))
from ..managers.WallpaperManager import WallpaperManager
from ..managers.ThemeManager import ThemeManager
from ..managers.LiveWallpaperManager import LiveWallpaperManager
from ..components.LiveWallpaperSourceRow import LiveWallpaperSourceRow

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
        
        # Show/hide checkmark with animation
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
    wallpaper_type_toggle_group = Gtk.Template.Child("wallpaper_type_toggle_group")
    static_toggle = Gtk.Template.Child("static_toggle")
    live_toggle = Gtk.Template.Child("live_toggle")
    content_stack = Gtk.Template.Child("content_stack")
    content_group = Gtk.Template.Child("content_group")
    wallpapers_flowbox = Gtk.Template.Child("wallpapers_flowbox")
    
    # Live wallpaper controls
    live_wallpaper_switch = Gtk.Template.Child("live_wallpaper_switch")
    live_wallpaper_options = Gtk.Template.Child("live_wallpaper_options")
    
    # Dynamic source container
    wallpaper_sources_group = Gtk.Template.Child("wallpaper_sources_group")
    add_source_button = Gtk.Template.Child("add_source_button")
    
    update_frequency_group = Gtk.Template.Child("update_frequency_group")
    shuffle_interval_spin = Gtk.Template.Child("shuffle_interval_spin")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize managers
        self.wallpaper_manager = WallpaperManager()
        self.live_wallpaper_manager = LiveWallpaperManager()
        self.wallpapers = []
        self.current_selection = None
        
        # Dynamic source rows
        self.source_rows = {}
        
        # Track active downloads to prevent duplicates
        self.active_downloads = set()
        self.download_lock = threading.Lock()
        
        # Track pending UI updates from file system events
        self.pending_ui_updates = {}  # source_id -> timeout_id
        self.ui_update_lock = threading.Lock()
        
        # File system monitor for real-time updates
        self.cache_monitor = None
        self.setup_cache_monitor()
        
        # Connect signals with error checking
        if self.wallpaper_type_toggle_group:
            self.wallpaper_type_toggle_group.connect("notify::active", self.on_wallpaper_type_toggled)
        if self.wallpapers_flowbox:
            self.wallpapers_flowbox.connect("child-activated", self.on_wallpaper_selected)
        
        # Live wallpaper signals
        if self.live_wallpaper_switch:
            self.live_wallpaper_switch.connect("notify::active", self.on_live_wallpaper_toggled)
            print("Live wallpaper switch signal connected")
        if self.shuffle_interval_spin:
            self.shuffle_interval_spin.connect("value-changed", self.on_interval_changed)
        if self.add_source_button:
            self.add_source_button.connect("clicked", self.on_add_source_clicked)
        
        # Create dynamic source rows
        self.create_source_rows()
        
        # Load initial settings
        self.load_settings()
        
        # Set initial state - activate static toggle (index 0)
        if self.wallpaper_type_toggle_group:
            self.wallpaper_type_toggle_group.set_active(0)
        if self.content_stack:
            self.content_stack.set_visible_child_name("static")
        
        # Settings will be loaded by load_settings() method
        
        # Load wallpapers in background thread
        thread = threading.Thread(target=self.load_wallpapers_background)
        thread.daemon = True
        thread.start()
    
    def on_live_wallpaper_toggled(self, switch, param):
        """Handle live wallpaper enable/disable"""
        try:
            state = switch.get_active()
            success = self.live_wallpaper_manager.set_enabled(state)
            if success:
                if self.live_wallpaper_options:
                    self.live_wallpaper_options.set_sensitive(state)
                
                if state:
                    # Start background service if not running
                    # (if already running, GSettings will update it automatically)
                    self.live_wallpaper_manager.start_background_service()
                # When disabled, daemon will stop its timers via GSettings automatically
                
                print(f"Live wallpapers {'enabled' if state else 'disabled'}")
            else:
                # Revert switch state on failure
                switch.set_active(not state)
        except Exception as e:
            print(f"Error toggling live wallpaper: {e}")
            switch.set_active(not state)
    

    
    def update_frequency_sensitivity(self, source_count):
        """Update frequency group sensitivity based on selected source count"""
        try:
            # Enable frequency settings only if multiple sources are selected
            multiple_sources = source_count > 1
            if self.update_frequency_group:
                self.update_frequency_group.set_sensitive(multiple_sources)
                
            # Update description based on state
            if hasattr(self, 'frequency_description'):
                if multiple_sources:
                    self.frequency_description.set_text(_("How often to switch between sources"))
                else:
                    self.frequency_description.set_text(_("Select multiple sources to enable frequency settings"))
                    
        except Exception as e:
            print(f"Error updating frequency sensitivity: {e}")
    
    def on_interval_changed(self, spin_button):
        """Handle cycle interval changes"""
        try:
            interval = int(spin_button.get_value())
            success = self.live_wallpaper_manager.set_shuffle_interval(interval)
            if success:
                print(f"Cycle interval updated: {interval} minutes")
                return True  # Signal handler should return True on success
            else:
                print(f"Failed to update cycle interval to {interval}")
                return False
        except Exception as e:
            print(f"Error updating interval: {e}")
            return False
    

    

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
            if not self.wallpapers_flowbox:
                print("Wallpapers flowbox not found")
                return
                
            # Create wallpaper thumbnail component
            thumbnail = WallpaperThumbnail()
            
            # Load the pixbuf if available
            if pixbuf:
                thumbnail.load_pixbuf(pixbuf)
            else:
                thumbnail.load_wallpaper(wallpaper_path)
            
            # Wrap in button with GNOME class (like GNOME Control Center)
            button = Gtk.Button()
            button.set_child(thumbnail)
            button.add_css_class('background-preview-button')
            button.set_has_frame(False)
            
            child = Gtk.FlowBoxChild()
            child.set_child(button)
            child.wallpaper_path = wallpaper_path
            
            if current_wallpaper and wallpaper_path == current_wallpaper:
                child.add_css_class('active-item')
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
            
            # Remove active-item class from previous selection
            if self.current_selection:
                self.current_selection.remove_css_class('active-item')
                prev_thumbnail = self.current_selection.get_child()
                if prev_thumbnail and hasattr(prev_thumbnail, 'set_selected'):
                    prev_thumbnail.set_selected(False)
            
            # Add active-item class to new selection
            flowbox_child.add_css_class('active-item')
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
    

    def load_source_data(self, source_id):
        """Load data for a source in background"""
        # Check if already downloading
        with self.download_lock:
            if source_id in self.active_downloads:
                print(f"⏭️  Skipping {source_id} - already downloading")
                return
            self.active_downloads.add(source_id)
        
        # Set loading state immediately
        if source_id in self.source_rows:
            self.source_rows[source_id].set_status('loading')
        
        # Use simple threading instead of Gio.Task
        def fetch_data():
            try:
                # Try to load metadata from cache first
                data = self.live_wallpaper_manager.load_metadata(source_id)
                
                if data:
                    print(f"📦 Cache check for {source_id}: data={bool(data)}, filepath={data.filepath if data else None}, exists={os.path.exists(data.filepath) if data and data.filepath else False}")
                else:
                    print(f"📦 Cache check for {source_id}: No metadata found")
                
                if data and data.filepath and os.path.exists(data.filepath):
                    # Wallpaper already downloaded
                    print(f"✅ Using cached wallpaper for {source_id}")
                    data.status = 'available'
                    GLib.idle_add(self.update_source_row_data, source_id, data)
                else:
                    # Need to download
                    print(f"⬇️  Downloading wallpaper for {source_id}...")
                    result = self.live_wallpaper_manager.download_wallpaper_from_source(source_id)
                    
                    if result and result.get('status') == 'available':
                        data = self.live_wallpaper_manager.load_metadata(source_id)
                        if data:
                            print(f"✓ Downloaded and loaded {source_id}")
                            GLib.idle_add(self.update_source_row_data, source_id, data)
                    else:
                        error_msg = result.get('error_message') if result else 'Download failed'
                        print(f"✗ Failed to download {source_id}: {error_msg}")
                        from ..managers.LiveWallpaperManager import LiveWallpaperData
                        error_data = LiveWallpaperData._create_error_instance(source_id, error_msg)
                        GLib.idle_add(self.update_source_row_data, source_id, error_data)
            except Exception as e:
                print(f"Error fetching data for {source_id}: {e}")
                from ..managers.LiveWallpaperManager import LiveWallpaperData
                error_data = LiveWallpaperData._create_error_instance(source_id, str(e))
                GLib.idle_add(self.update_source_row_data, source_id, error_data)
            finally:
                with self.download_lock:
                    self.active_downloads.discard(source_id)
        
        threading.Thread(target=fetch_data, daemon=True).start()
    

    def update_source_row_data(self, source_id, wallpaper_data):
        """Update source row with fetched data"""
        try:
            if source_id in self.source_rows:
                self.source_rows[source_id].set_wallpaper_data(wallpaper_data)
        except Exception as e:
            print(f"Error updating source row data for {source_id}: {e}")
    
    def on_dynamic_source_toggled(self, source_row, source_id, active):
        """Handle dynamic source toggle"""
        try:
            # Get currently selected sources
            selected_sources = []
            for sid, row in self.source_rows.items():
                if row.is_checkbox_active():
                    selected_sources.append(sid)
            
            # Ensure at least one source is selected
            if not selected_sources:
                source_row.set_checkbox_active(True)
                return
            
            # Update settings
            success = self.live_wallpaper_manager.set_selected_sources(selected_sources)
            if success:
                print(f"Selected sources updated: {selected_sources}")
                
            # Update frequency group sensitivity
            self.update_frequency_sensitivity(len(selected_sources))
            
        except Exception as e:
            print(f"Error handling source toggle: {e}")
    
    def on_dynamic_download_requested(self, source_row, source_id):
        """Handle download request from dynamic source row"""
        try:
            # Check if already downloading
            with self.download_lock:
                if source_id in self.active_downloads:
                    print(f"⏭️  Skipping {source_id} - already downloading")
                    return
                self.active_downloads.add(source_id)
            
            # Set downloading state
            source_row.set_status('downloading')
            
            def download_in_background():
                try:
                    # Progress callback
                    def progress_callback(current, total):
                        if total > 0:
                            progress_percent = int((current / total) * 100)
                            GLib.idle_add(source_row.set_download_progress, progress_percent)
                    
                    result = self.live_wallpaper_manager.download_wallpaper_from_source(
                        source_id, 
                        progress_callback=progress_callback
                    )
                    
                    if result:
                        from ..managers.LiveWallpaperManager import LiveWallpaperData
                        data = LiveWallpaperData(
                            source=result['source'],
                            title=result.get('title', f'{source_id.title()} Wallpaper'),
                            description=result.get('description', ''),
                            image_url=result.get('url', ''),
                            filepath=result.get('filepath'),
                            status='available'
                        )
                        GLib.idle_add(source_row.set_wallpaper_data, data)
                    else:
                        from ..managers.LiveWallpaperManager import LiveWallpaperData
                        error_data = LiveWallpaperData._create_error_instance(source_id, 'Download failed')
                        GLib.idle_add(source_row.set_wallpaper_data, error_data)
                except Exception as e:
                    print(f"Error downloading {source_id}: {e}")
                    from ..managers.LiveWallpaperManager import LiveWallpaperData
                    error_data = LiveWallpaperData._create_error_instance(source_id, str(e))
                    GLib.idle_add(source_row.set_wallpaper_data, error_data)
                finally:
                    with self.download_lock:
                        self.active_downloads.discard(source_id)
            
            threading.Thread(target=download_in_background, daemon=True).start()
            
        except Exception as e:
            print(f"Error handling download request for {source_id}: {e}")
            with self.download_lock:
                self.active_downloads.discard(source_id)
    

    def on_dynamic_wallpaper_set_requested(self, source_row, source_id, filepath):
        """Handle wallpaper set request from dynamic source row"""
        try:
            if filepath and os.path.exists(filepath):
                success = self.wallpaper_manager.set_wallpaper(filepath)
                if success:
                    print(f"Set wallpaper from {source_id}: {os.path.basename(filepath)}")
                    source_row._show_action_feedback(_("Wallpaper set!"))
                else:
                    print(f"Failed to set wallpaper from {source_id}")
                    source_row._show_action_feedback(_("Failed to set wallpaper"))
            else:
                print(f"Invalid filepath for {source_id}: {filepath}")
                source_row._show_action_feedback(_("File not found"))
                
        except Exception as e:
            print(f"Error setting wallpaper from {source_id}: {e}")
            source_row._show_action_feedback(_("Error setting wallpaper"))
    
    def load_settings(self):
        """Load initial settings"""
        try:
            # Load live wallpaper enabled state
            if self.live_wallpaper_switch:
                enabled = self.live_wallpaper_manager.is_enabled()
                self.live_wallpaper_switch.set_active(enabled)
                if self.live_wallpaper_options:
                    self.live_wallpaper_options.set_sensitive(enabled)
                print(f"Live wallpaper switch set to: {enabled}, options sensitive: {enabled}")
            
            # Load selected sources and update checkboxes
            selected_sources = self.live_wallpaper_manager.get_selected_sources()
            for source_id, row in self.source_rows.items():
                row.set_checkbox_active(source_id in selected_sources)
            
            # Load shuffle interval
            if self.shuffle_interval_spin:
                interval = self.live_wallpaper_manager.get_shuffle_interval()
                self.shuffle_interval_spin.set_value(interval)
            
            # Update frequency sensitivity
            self.update_frequency_sensitivity(len(selected_sources))
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    

    
    def add_new_source(self, source_id, source_config):
        """Add a new source row dynamically"""
        try:
            if source_id not in self.source_rows:
                self.create_source_row(source_id, source_config)
                print(f"Added new source: {source_id}")
        except Exception as e:
            print(f"Error adding new source {source_id}: {e}")
    
    def remove_source(self, source_id):
        """Remove a source row dynamically"""
        try:
            if source_id in self.source_rows:
                row = self.source_rows[source_id]
                self.wallpaper_sources_group.remove(row)
                del self.source_rows[source_id]
                print(f"Removed source: {source_id}")
        except Exception as e:
            print(f"Error removing source {source_id}: {e}")
    
    def update_source_config(self, source_id, new_config):
        """Update configuration for an existing source"""
        try:
            if source_id in self.source_rows:
                row = self.source_rows[source_id]
                # Update title and description
                row.set_title(new_config['name'])
                row.set_subtitle(new_config['description'])
                # Refresh data
                self.load_source_data(source_id)
                print(f"Updated config for source: {source_id}")
        except Exception as e:
            print(f"Error updating source config {source_id}: {e}")
            
            # Update frequency sensitivity
            self.update_frequency_sensitivity(len(selected_sources))
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    

    def create_source_rows(self):
        """Create dynamic source rows from user settings"""
        try:
            if not self.wallpaper_sources_group:
                print("Wallpaper sources group not found")
                return
            
            # Clear existing rows first
            print("Clearing existing source rows")
            for source_id in list(self.source_rows.keys()):
                row = self.source_rows[source_id]
                self.wallpaper_sources_group.remove(row)
            self.source_rows.clear()
            
            # Get available sources
            sources = self.live_wallpaper_manager.get_available_sources()
            
            # Get selected sources from LiveWallpaperManager (the correct source of truth)
            selected_source_ids = self.live_wallpaper_manager.get_selected_sources()
            
            print(f"Creating rows for selected sources: {selected_source_ids}")
            
            # Create rows for all selected sources
            for source_id in selected_source_ids:
                if source_id in sources:
                    print(f"Creating row for: {source_id}")
                    self.create_source_row(source_id, sources[source_id])
                else:
                    print(f"Warning: Source {source_id} not found in available sources")
                    
        except Exception as e:
            print(f"Error creating source rows: {e}")
    
    def create_source_row(self, source_id, source_config):
        """Create a single source row component"""
        try:
            # Import here to avoid GResource issues at module level
            from ..components.LiveWallpaperSourceRow import LiveWallpaperSourceRow
            
            # Create the component
            source_row = LiveWallpaperSourceRow(source_id, source_config)
            source_row.set_live_wallpaper_manager(self.live_wallpaper_manager)
            
            # Connect signals
            source_row.connect('download-requested', self.on_dynamic_download_requested)
            source_row.connect('wallpaper-set-requested', self.on_dynamic_wallpaper_set_requested)
            
            # Add to container
            self.wallpaper_sources_group.add(source_row)
            print(f"Added source row for {source_id} to container")
            
            # Store reference
            self.source_rows[source_id] = source_row
            
            # Don't load data here - it will be loaded when Live tab is activated
            # This prevents unnecessary downloads when app starts on Static tab
            
        except Exception as e:
            print(f"Error creating source row for {source_id}: {e}") 
   
    def on_wallpaper_type_toggled(self, toggle_group, param):
        """Handle wallpaper type toggle group change"""
        active_index = toggle_group.get_active()
        print(f"Wallpaper type toggled to index: {active_index}")
        
        if active_index is None:
            return
            
        if self.content_stack:
            if active_index == 0:  # Static toggle
                self.content_stack.set_visible_child_name("static")
                print("Switched to static wallpapers")
                
            elif active_index == 1:  # Live toggle
                self.content_stack.set_visible_child_name("live")
                print("Switched to live wallpapers")
                
                # Load data for all sources (will use cache if available)
                for source_id in self.source_rows.keys():
                    self.load_source_data(source_id)
                
                # File monitor will handle real-time updates automatically
    
    def setup_cache_monitor(self):
        """Setup file system monitor for cache directory (inotify-based)"""
        try:
            from gi.repository import Gio
            
            # Get today's cache directory
            cache_dir = self.live_wallpaper_manager.get_daily_cache_dir()
            
            # Create directory if it doesn't exist
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
            
            # Create GFile for the directory
            cache_file = Gio.File.new_for_path(cache_dir)
            
            # Create file monitor (uses inotify on Linux)
            self.cache_monitor = cache_file.monitor_directory(
                Gio.FileMonitorFlags.NONE,
                None
            )
            
            # Connect to changed signal
            self.cache_monitor.connect('changed', self.on_cache_changed)
            
            print(f"✓ File system monitor active on: {cache_dir}")
            print("  Using inotify for real-time updates")
            
        except Exception as e:
            print(f"Warning: Could not setup file monitor: {e}")
            print("  Falling back to manual refresh")
    
    def on_cache_changed(self, monitor, file, other_file, event_type):
        """Handle file system changes in cache directory (inotify callback)"""
        try:
            from gi.repository import Gio
            
            # Only process CHANGES_DONE_HINT (file fully written)
            # Skip CREATED to avoid duplicate updates
            if event_type != Gio.FileMonitorEvent.CHANGES_DONE_HINT:
                return
            
            filename = file.get_basename()
            
            # Check if it's a wallpaper file (image or metadata)
            if filename.endswith(('.jpg', '.jpeg', '.png', '.json')):
                # Extract source_id from filename
                source_id = filename.split('-')[0] if '-' in filename else filename.split('.')[0]
                
                # Check if this source is being tracked
                if source_id not in self.source_rows:
                    return
                
                # Debounce: cancel previous pending update for this source
                with self.ui_update_lock:
                    if source_id in self.pending_ui_updates:
                        # Cancel previous timeout
                        GLib.source_remove(self.pending_ui_updates[source_id])
                    
                    # Schedule new update
                    timeout_id = GLib.timeout_add(300, self.refresh_source_after_file_change, source_id)
                    self.pending_ui_updates[source_id] = timeout_id
                
        except Exception as e:
            print(f"Error handling cache change: {e}")
    
    def refresh_source_after_file_change(self, source_id):
        """Refresh specific source after file change (debounced)"""
        try:
            # Remove from pending updates
            with self.ui_update_lock:
                self.pending_ui_updates.pop(source_id, None)
            
            if source_id in self.source_rows:
                # Reload metadata
                wallpaper_data = self.live_wallpaper_manager.load_metadata(source_id)
                
                if wallpaper_data and wallpaper_data.filepath and os.path.exists(wallpaper_data.filepath):
                    print(f"✓ Auto-updating UI for {source_id} (file system event)")
                    wallpaper_data.status = 'available'
                    self.source_rows[source_id].set_wallpaper_data(wallpaper_data)
        except Exception as e:
            print(f"Error refreshing source {source_id}: {e}")
        
        return False  # Don't repeat timeout
    
    def refresh_all_sources(self):
        """Refresh all source rows (reload metadata and update UI)"""
        try:
            selected_sources = self.live_wallpaper_manager.get_selected_sources()
            
            for source_id in selected_sources:
                if source_id in self.source_rows:
                    # Reload metadata from cache
                    wallpaper_data = self.live_wallpaper_manager.load_metadata(source_id)
                    
                    if wallpaper_data and wallpaper_data.filepath and os.path.exists(wallpaper_data.filepath):
                        # Wallpaper is available - update UI
                        wallpaper_data.status = 'available'
                        self.source_rows[source_id].set_wallpaper_data(wallpaper_data)
        except Exception as e:
            print(f"Error refreshing sources: {e}")
    
    def get_user_sources(self):
        """Get user-added sources from LiveWallpaperManager (single source of truth)"""
        try:
            # Get selected sources from LiveWallpaperManager
            source_ids = self.live_wallpaper_manager.get_selected_sources()
            
            # Convert to user_sources format for compatibility
            user_sources = [{'source_id': sid, 'enabled': True} for sid in source_ids]
            return user_sources
        except Exception as e:
            print(f"Error getting user sources: {e}")
            return []
    
    def save_user_sources(self, user_sources):
        """Save user-added sources to LiveWallpaperManager (single source of truth)"""
        try:
            # Extract source IDs
            source_ids = [s.get('source_id') for s in user_sources if s.get('enabled', True)]
            
            # Save to LiveWallpaperManager
            self.live_wallpaper_manager.set_selected_sources(source_ids)
            print(f"Saved selected sources: {source_ids}")
            return True
        except Exception as e:
            print(f"Error saving user sources: {e}")
            return False
    
    def on_add_source_clicked(self, button):
        """Handle add source button click - show modal"""
        try:
            from ..components.AddWallpaperSourcesDialog import AddWallpaperSourcesDialog
            
            # Get available sources
            available_sources = self.live_wallpaper_manager.get_available_sources()
            
            # Get current user sources
            user_sources = self.get_user_sources()
            current_source_ids = [s.get('source_id') for s in user_sources]
            
            print(f"Current user sources: {user_sources}")
            print(f"Current source IDs: {current_source_ids}")
            
            # Create and show dialog
            dialog = AddWallpaperSourcesDialog(available_sources, current_source_ids)
            dialog.connect('sources-added', self.on_sources_added)
            
            # Present dialog
            parent_window = self.get_root()
            if parent_window:
                dialog.present(parent_window)
            else:
                dialog.present()
                
        except Exception as e:
            print(f"Error showing add source dialog: {e}")
    
    def on_sources_added(self, dialog, new_sources):
        """Handle sources added/removed from dialog"""
        try:
            print(f"Sources updated: {new_sources}")
            
            # Build new sources list (avoiding duplicates)
            enabled_sources = []
            seen_sources = set()
            
            for source in new_sources:
                source_id = source.get('source_id')
                
                # Skip if already added
                if source_id in seen_sources:
                    print(f"Skipping duplicate source: {source_id}")
                    continue
                
                if source.get('enabled', True):
                    # Source is enabled - add it
                    enabled_sources.append(source)
                    seen_sources.add(source_id)
                    
                    # Save API key if provided
                    if 'api_key' in source:
                        self.save_api_key(source_id, source['api_key'])
                else:
                    # Source is disabled - remove it
                    print(f"Removing source: {source_id}")
            
            print(f"Final enabled sources: {enabled_sources}")
            
            # Save user sources (this will save to LiveWallpaperManager)
            self.save_user_sources(enabled_sources)
            
            # Save API keys separately
            for source in enabled_sources:
                if 'api_key' in source:
                    self.save_api_key(source['source_id'], source['api_key'])
            
            # Recreate source rows
            self.create_source_rows()
            
            # Load data for enabled sources
            for source in enabled_sources:
                source_id = source.get('source_id')
                if source_id:
                    self.load_source_data(source_id)
            
        except Exception as e:
            print(f"Error handling sources update: {e}")
    
    def save_api_key(self, source_id, api_key):
        """Save API key for a source"""
        try:
            from ..managers.settings import app_settings
            
            # Get current API keys
            api_keys_json = app_settings.get('live-wallpaper-source-api-keys')
            api_keys = json.loads(api_keys_json) if api_keys_json else {}
            
            # Update API key
            api_keys[source_id] = api_key
            
            # Save back
            app_settings.set('live-wallpaper-source-api-keys', json.dumps(api_keys))
            
            print(f"Saved API key for {source_id}")
            return True
        except Exception as e:
            print(f"Error saving API key: {e}")
            return False
