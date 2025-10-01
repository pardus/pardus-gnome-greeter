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
from ..managers.ThemeManager import ThemeManager
from ..managers.LiveWallpaperManager import LiveWallpaperManager
# from ..components.LiveWallpaperSourceRow import LiveWallpaperSourceRow  # Disabled due to GResource issue

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
    
    update_frequency_group = Gtk.Template.Child("update_frequency_group")
    shuffle_interval_spin = Gtk.Template.Child("shuffle_interval_spin")
    update_now_button = Gtk.Template.Child("update_now_button")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize managers
        self.wallpaper_manager = WallpaperManager()
        self.live_wallpaper_manager = LiveWallpaperManager()
        self.wallpapers = []
        self.current_selection = None
        
        # Dynamic source rows
        self.source_rows = {}
        
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
        if self.update_now_button:
            self.update_now_button.connect("clicked", self.on_update_now_clicked)
        
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
        
        # Check wallpaper status for today
        self.check_daily_wallpaper_status()
        
        # Load wallpapers in background thread
        thread = threading.Thread(target=self.load_wallpapers_background)
        thread.daemon = True
        thread.start()
    
    def on_wallpaper_type_toggled(self, toggle_group, param):
        """Handle wallpaper type toggle group change"""
        active_index = toggle_group.get_active()
        if active_index is None:
            return
            
        if self.content_stack:
            if active_index == 0:  # Static toggle
                self.content_stack.set_visible_child_name("static")
            elif active_index == 1:  # Live toggle
                self.content_stack.set_visible_child_name("live")
    

    

    
    def on_live_wallpaper_toggled(self, switch, param):
        """Handle live wallpaper enable/disable"""
        try:
            state = switch.get_active()
            success = self.live_wallpaper_manager.set_enabled(state)
            if success:
                if self.live_wallpaper_options:
                    self.live_wallpaper_options.set_sensitive(state)
                if state:
                    # Start background service
                    self.live_wallpaper_manager.start_background_service()
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
        except Exception as e:
            print(f"Error updating interval: {e}")
    
    def on_update_now_clicked(self, button):
        """Handle manual wallpaper update"""
        try:
            button.set_sensitive(False)
            button.set_label(_("Updating..."))
            
            def update_in_background():
                success = self.live_wallpaper_manager.update_wallpaper_now()
                
                def update_ui():
                    button.set_sensitive(True)
                    if success:
                        button.set_label(_("Updated!"))
                        GLib.timeout_add_seconds(2, lambda: button.set_label(_("Update Now")))
                    else:
                        button.set_label(_("Failed"))
                        GLib.timeout_add_seconds(2, lambda: button.set_label(_("Update Now")))
                    return False
                
                GLib.idle_add(update_ui)
            
            thread = threading.Thread(target=update_in_background, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Error updating wallpaper: {e}")
            button.set_sensitive(True)
            button.set_label(_("Update Now"))
    
    def check_daily_wallpaper_status(self):
        """Check status of today's wallpapers for each source"""
        sources = ['bing', 'nasa', 'wikipedia']
        
        for source in sources:
            # Start with loading state
            self.update_source_status(source, 'loading')
            
            # Check if wallpaper exists for today
            thread = threading.Thread(
                target=self.check_source_wallpaper_background,
                args=(source,),
                daemon=True
            )
            thread.start()
    
    def check_source_wallpaper_background(self, source):
        """Check if wallpaper exists for source in background"""
        try:
            daily_dir = self.live_wallpaper_manager.get_daily_cache_dir()
            
            # Look for existing wallpaper
            existing_file = None
            if os.path.exists(daily_dir):
                for filename in os.listdir(daily_dir):
                    if filename.startswith(f"{source}-") and filename.endswith(('.jpg', '.jpeg', '.png')):
                        existing_file = os.path.join(daily_dir, filename)
                        break
            
            if existing_file:
                # Wallpaper exists, show preview
                GLib.idle_add(self.update_source_status, source, 'available', existing_file)
            else:
                # Download wallpaper
                GLib.idle_add(self.update_source_status, source, 'downloading')
                
                wallpaper_info = self.live_wallpaper_manager.download_wallpaper_from_source(source)
                
                if wallpaper_info:
                    GLib.idle_add(self.update_source_status, source, 'available', wallpaper_info['filepath'])
                else:
                    GLib.idle_add(self.update_source_status, source, 'error')
                    
        except Exception as e:
            print(f"Error checking {source} wallpaper: {e}")
            GLib.idle_add(self.update_source_status, source, 'error')
    
    def update_source_status(self, source, status, filepath=None):
        """Update UI status for a source"""
        try:
            # Get widgets for this source
            preview_widget = getattr(self, f"{source}_preview", None)
            status_icon = getattr(self, f"{source}_status_icon", None)
            action_button = getattr(self, f"{source}_action_button", None)
            
            if not all([preview_widget, status_icon, action_button]):
                return
            
            if status == 'loading':
                # Show spinner
                status_icon.set_from_icon_name("content-loading-symbolic")
                status_icon.add_css_class("spinning")
                action_button.set_sensitive(False)
                action_button.set_icon_name("content-loading-symbolic")
                
            elif status == 'downloading':
                # Show download in progress
                status_icon.set_from_icon_name("folder-download-symbolic")
                status_icon.add_css_class("spinning")
                action_button.set_sensitive(False)
                action_button.set_icon_name("content-loading-symbolic")
                
            elif status == 'available' and filepath:
                # Show success and preview
                status_icon.set_from_icon_name("emblem-ok-symbolic")
                status_icon.remove_css_class("spinning")
                status_icon.add_css_class("success")
                
                action_button.set_sensitive(True)
                action_button.set_icon_name("media-playback-start-symbolic")
                action_button.set_tooltip_text(_("Set as wallpaper"))
                
                # Load preview image
                if os.path.exists(filepath):
                    try:
                        texture = Gdk.Texture.new_from_filename(filepath)
                        preview_widget.set_paintable(texture)
                        preview_widget.set_tooltip_text(_("Click to set as wallpaper"))
                    except Exception as e:
                        print(f"Error loading preview for {source}: {e}")
                        
            elif status == 'error':
                # Show error state
                status_icon.set_from_icon_name("dialog-error-symbolic")
                status_icon.remove_css_class("spinning")
                status_icon.add_css_class("error")
                
                action_button.set_sensitive(True)
                action_button.set_icon_name("view-refresh-symbolic")
                action_button.set_tooltip_text(_("Retry download"))
                
        except Exception as e:
            print(f"Error updating {source} status: {e}")
    
    def on_download_source(self, source):
        """Handle download button click for a source"""
        try:
            # Update UI to downloading state
            self.update_source_status(source, 'downloading')
            
            # Download in background
            thread = threading.Thread(
                target=self.download_source_background,
                args=(source,),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            print(f"Error starting download for {source}: {e}")
    
    def download_source_background(self, source):
        """Download wallpaper for source in background"""
        try:
            wallpaper_info = self.live_wallpaper_manager.download_wallpaper_from_source(source)
            
            if wallpaper_info:
                GLib.idle_add(self.update_source_status, source, 'available', wallpaper_info['filepath'])
            else:
                GLib.idle_add(self.update_source_status, source, 'error')
                
        except Exception as e:
            print(f"Error downloading {source} wallpaper: {e}")
            GLib.idle_add(self.update_source_status, source, 'error')
    
    def on_preview_clicked(self, source):
        """Handle preview image click"""
        try:
            daily_dir = self.live_wallpaper_manager.get_daily_cache_dir()
            
            # Find wallpaper file for this source
            if os.path.exists(daily_dir):
                for filename in os.listdir(daily_dir):
                    if filename.startswith(f"{source}-") and filename.endswith(('.jpg', '.jpeg', '.png')):
                        filepath = os.path.join(daily_dir, filename)
                        
                        # Set as wallpaper
                        success = self.wallpaper_manager.set_wallpaper(filepath)
                        if success:
                            print(f"Set wallpaper from {source}: {filename}")
                        break
                        
        except Exception as e:
            print(f"Error setting wallpaper from {source}: {e}")

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
    
    def create_source_rows(self):
        """Create dynamic source rows from JSON configuration"""
        try:
            if not self.wallpaper_sources_group:
                print("Wallpaper sources group not found")
                return
            
            # Get available sources from manager
            sources = self.live_wallpaper_manager.get_available_sources()
            
            for source_id, source_config in sources.items():
                # Only create rows for enabled sources
                if source_config.get('enabled', False):
                    self.create_source_row(source_id, source_config)
                    
        except Exception as e:
            print(f"Error creating source rows: {e}")
    
    def create_source_row(self, source_id, source_config):
        """Create a single source row component"""
        try:
            # TODO: Re-enable when GResource is properly configured
            print(f"Would create source row for {source_id}: {source_config['name']}")
            
            # # Create the component
            # source_row = LiveWallpaperSourceRow(source_id, source_config)
            # source_row.set_live_wallpaper_manager(self.live_wallpaper_manager)
            # 
            # # Connect signals
            # source_row.connect('source-toggled', self.on_dynamic_source_toggled)
            # source_row.connect('download-requested', self.on_dynamic_download_requested)
            # source_row.connect('wallpaper-set-requested', self.on_dynamic_wallpaper_set_requested)
            # 
            # # Add to container
            # self.wallpaper_sources_group.add(source_row)
            # 
            # # Store reference
            # self.source_rows[source_id] = source_row
            # 
            # # Load initial data
            # self.load_source_data(source_id)
            
        except Exception as e:
            print(f"Error creating source row for {source_id}: {e}")
    
    def load_source_data(self, source_id):
        """Load data for a source in background"""
        def fetch_data():
            try:
                # Set loading state
                if source_id in self.source_rows:
                    GLib.idle_add(self.source_rows[source_id].set_status, 'loading')
                
                # Check if wallpaper already exists for today
                daily_dir = self.live_wallpaper_manager.get_daily_cache_dir()
                existing_file = None
                
                if os.path.exists(daily_dir):
                    for filename in os.listdir(daily_dir):
                        if filename.startswith(f"{source_id}-") and filename.endswith(('.jpg', '.jpeg', '.png')):
                            existing_file = os.path.join(daily_dir, filename)
                            break
                
                if existing_file:
                    # Create data object for existing file
                    from ..managers.LiveWallpaperManager import LiveWallpaperData
                    data = LiveWallpaperData(
                        source=source_id,
                        title=f'{source_id.title()} Daily',
                        description='Today\'s wallpaper',
                        image_url='',
                        filepath=existing_file,
                        status='available'
                    )
                    GLib.idle_add(self.update_source_row_data, source_id, data)
                else:
                    # Fetch fresh data
                    data = self.live_wallpaper_manager.fetch_wallpaper_info_from_source(source_id)
                    GLib.idle_add(self.update_source_row_data, source_id, data)
                    
            except Exception as e:
                print(f"Error fetching data for {source_id}: {e}")
                from ..managers.LiveWallpaperManager import LiveWallpaperData
                error_data = LiveWallpaperData._create_error_instance(source_id, str(e))
                GLib.idle_add(self.update_source_row_data, source_id, error_data)
        
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
            # Set downloading state
            source_row.set_status('downloading')
            
            def download_in_background():
                try:
                    result = self.live_wallpaper_manager.download_wallpaper_from_source(source_id)
                    if result:
                        # Create LiveWallpaperData from result
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
                        error_data = LiveWallpaperData._create_error_instance(source_id, 'Download failed')
                        GLib.idle_add(source_row.set_wallpaper_data, error_data)
                        
                except Exception as e:
                    print(f"Error downloading {source_id}: {e}")
                    error_data = LiveWallpaperData._create_error_instance(source_id, str(e))
                    GLib.idle_add(source_row.set_wallpaper_data, error_data)
            
            threading.Thread(target=download_in_background, daemon=True).start()
            
        except Exception as e:
            print(f"Error handling download request for {source_id}: {e}")
    
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
    
    def refresh_all_sources(self):
        """Refresh data for all source rows"""
        try:
            for source_id in self.source_rows.keys():
                self.load_source_data(source_id)
        except Exception as e:
            print(f"Error refreshing sources: {e}")
    
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
    
    def refresh_source_data(self):
        """Refresh data for all source rows"""
        try:
            for source_id in self.source_rows.keys():
                self.load_source_data(source_id)
        except Exception as e:
            print(f"Error refreshing source data: {e}")   
    def create_source_rows(self):
        """Create dynamic source rows from JSON configuration"""
        try:
            if not self.wallpaper_sources_group:
                print("Wallpaper sources group not found")
                return
            
            # Get available sources from manager
            sources = self.live_wallpaper_manager.get_available_sources()
            print(f"Creating source rows for {len(sources)} sources")
            
            for source_id, source_config in sources.items():
                # Only create rows for enabled sources
                if source_config.get('enabled', False):
                    print(f"Creating row for {source_id}")
                    self.create_source_row(source_id, source_config)
                else:
                    print(f"Skipping disabled source: {source_id}")
                    
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
            source_row.connect('source-toggled', self.on_dynamic_source_toggled)
            source_row.connect('download-requested', self.on_dynamic_download_requested)
            source_row.connect('wallpaper-set-requested', self.on_dynamic_wallpaper_set_requested)
            
            # Add to container
            self.wallpaper_sources_group.add(source_row)
            print(f"Added source row for {source_id} to container")
            
            # Store reference
            self.source_rows[source_id] = source_row
            
            # Load initial data
            self.load_source_data(source_id)
            
        except Exception as e:
            print(f"Error creating source row for {source_id}: {e}") 
   
    def on_live_wallpaper_toggled(self, switch, param):
        """Handle live wallpaper enable/disable"""
        try:
            state = switch.get_active()
            success = self.live_wallpaper_manager.set_enabled(state)
            if success:
                if self.live_wallpaper_options:
                    self.live_wallpaper_options.set_sensitive(state)
                if state:
                    # Start background service
                    self.live_wallpaper_manager.start_background_service()
                print(f"Live wallpapers {'enabled' if state else 'disabled'}")
            else:
                # Revert switch state on failure
                switch.set_active(not state)
        except Exception as e:
            print(f"Error toggling live wallpaper: {e}")
            switch.set_active(not state)    
  
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