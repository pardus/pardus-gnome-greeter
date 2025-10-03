import locale
import gi
import json
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/AddWallpaperSourcesDialog.ui')
class AddWallpaperSourcesDialog(Adw.Dialog):
    __gtype_name__ = 'PardusAddWallpaperSourcesDialog'
    
    # Define signal
    __gsignals__ = {
        'sources-added': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }
    
    # Template children
    sources_group = Gtk.Template.Child("sources_group")
    cancel_button = Gtk.Template.Child("cancel_button")
    add_button = Gtk.Template.Child("add_button")
    
    def __init__(self, available_sources, current_sources, **kwargs):
        super().__init__(**kwargs)
        
        self.available_sources = available_sources
        self.current_sources = current_sources or []
        self.source_rows = {}
        
        # Connect signals
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        self.add_button.connect("clicked", self.on_add_clicked)
        
        # Populate sources
        self.populate_sources()
    
    def populate_sources(self):
        """Populate available sources in sorted order"""
        # Sort sources by priority:
        # 1. No API key required (reddit, wikipedia)
        # 2. Optional API key (nasa - has DEMO_KEY)
        # 3. Required API key (unsplash, pexels)
        
        def get_source_priority(item):
            source_id, source_config = item
            headers = source_config.get('headers', {})
            api_url = source_config.get('api_url', '')
            
            # Check if API key is required
            has_api_key_in_headers = any('API' in str(v).upper() or 'KEY' in str(v).upper() 
                                         for v in headers.values())
            has_api_key_in_url = 'api_key=' in api_url.lower() or 'apikey=' in api_url.lower()
            
            # Check if it has DEMO_KEY (optional)
            has_demo_key = 'DEMO_KEY' in api_url or 'demo' in api_url.lower()
            
            if not has_api_key_in_headers and not has_api_key_in_url:
                return 0  # No API key - highest priority
            elif has_demo_key:
                return 1  # Optional API key (DEMO_KEY available)
            else:
                return 2  # Required API key - lowest priority
        
        # Sort sources
        sorted_sources = sorted(self.available_sources.items(), key=get_source_priority)
        
        # Create rows in sorted order
        for source_id, source_config in sorted_sources:
            # Create source row
            row = self.create_source_row(source_id, source_config)
            self.sources_group.add(row)
            self.source_rows[source_id] = row
            
            # Check if source is currently added
            if source_id in self.current_sources:
                row.checkbox.set_active(True)
    
    def create_source_row(self, source_id, source_config):
        """Create a source selection row"""
        # Check if API key is required
        headers = source_config.get('headers', {})
        api_url = source_config.get('api_url', '')
        
        # Check if API key is in headers or URL
        requires_api_key = (
            any('API' in str(v).upper() or 'KEY' in str(v).upper() for v in headers.values()) or
            'api_key=' in api_url.lower() or
            'apikey=' in api_url.lower()
        )
        
        # Create appropriate row type
        if requires_api_key:
            # ExpanderRow for sources with API key
            row = Adw.ExpanderRow()
        else:
            # Simple ActionRow for sources without API key
            row = Adw.ActionRow()
        
        row.set_title(source_config['name'])
        row.set_subtitle(source_config['description'])
        
        # Checkbox
        checkbox = Gtk.CheckButton()
        checkbox.set_valign(Gtk.Align.CENTER)
        row.add_prefix(checkbox)
        row.checkbox = checkbox
        row.source_id = source_id
        
        if requires_api_key:
            # API Key warning icon
            warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            warning_icon.set_tooltip_text(_("API Key Required"))
            warning_icon.add_css_class("warning")
            row.add_suffix(warning_icon)
            
            # API Key input row
            api_key_row = Adw.ActionRow()
            api_key_row.set_title(_("API Key"))
            
            # API Key entry
            api_key_entry = Gtk.Entry()
            api_key_entry.set_placeholder_text(_("Enter your API key"))
            api_key_entry.set_valign(Gtk.Align.CENTER)
            api_key_entry.set_hexpand(True)
            api_key_row.add_suffix(api_key_entry)
            row.api_key_entry = api_key_entry
            
            row.add_row(api_key_row)
            
            # Get API Key button
            get_key_row = Adw.ActionRow()
            get_key_row.set_title(_("Get Free API Key"))
            
            get_key_button = Gtk.LinkButton()
            get_key_button.set_label(_("Get API Key"))
            get_key_button.set_valign(Gtk.Align.CENTER)
            
            # Set URL based on source
            if source_id == 'nasa':
                get_key_button.set_uri("https://api.nasa.gov/")
                # Add rate limit warning
                warning_label = Gtk.Label()
                warning_label.set_markup(
                    f'<span size="small" foreground="#f66151">{_("⚠️ Rate limited without API key")}</span>'
                )
                warning_label.set_xalign(0)
                get_key_row.add_suffix(warning_label)
            elif source_id == 'unsplash':
                get_key_button.set_uri("https://unsplash.com/developers")
            elif source_id == 'pexels':
                get_key_button.set_uri("https://www.pexels.com/api/")
            
            get_key_row.add_suffix(get_key_button)
            row.add_row(get_key_row)
        else:
            row.api_key_entry = None
        
        return row
    
    def on_cancel_clicked(self, button):
        """Handle cancel button click"""
        self.close()
    
    def on_add_clicked(self, button):
        """Handle add button click"""
        selected_sources = []
        
        for source_id, row in self.source_rows.items():
            # Add source if checked
            if row.checkbox.get_active():
                source_data = {
                    'source_id': source_id,
                    'enabled': True
                }
                
                # Add API key if provided
                if hasattr(row, 'api_key_entry') and row.api_key_entry:
                    api_key = row.api_key_entry.get_text().strip()
                    if api_key:
                        source_data['api_key'] = api_key
                
                selected_sources.append(source_data)
            else:
                # If unchecked and was previously added, mark as disabled
                if source_id in self.current_sources:
                    selected_sources.append({
                        'source_id': source_id,
                        'enabled': False
                    })
        
        # Emit signal with selected sources
        self.emit('sources-added', selected_sources)
        self.close()
