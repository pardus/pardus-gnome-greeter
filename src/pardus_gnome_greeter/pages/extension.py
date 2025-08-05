import locale
import gi
import os
import sys
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gdk

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

# Add the managers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'managers'))
from ExtensionManager import ExtensionManager

# Extension descriptions dictionary
EXTENSION_DESCRIPTIONS = {
    "drive-menu@gnome-shell-extensions.gcampax.github.com": _("Add a status menu for accessing and unmounting removable devices."),
    "caffeine@patapon.info": _("Disable screensaver and auto-suspend."),
    "appindicatorsupport@rgcjonas.gmail.com": _("Enables support for AppIndicator, KStatusNotifierItem, and legacy Tray icons in the Shell."),
    "noannoyance@daase.net": _("Eliminates the 'Windows is ready' notification and brings the window into focus."),
    "pano@elhan.io": _("Cutting-edge clipboard manager for GNOME Shell."),
    "clipboard-indicator@tudmotu.com": _("Adds clipboard indicator to top panel, caches history."),
    "bluetooth-battery-meter@maniacx.github.com": _("Provides quick access to Bluetooth"),
}

# ExtensionCard template class
@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/components/ExtensionCard.ui')
class ExtensionCard(Gtk.Box):
    __gtype_name__ = 'ExtensionCard'
    
    # Template children
    image = Gtk.Template.Child("image")
    name_label = Gtk.Template.Child("name_label")
    desc_label = Gtk.Template.Child("desc_label")
    switch = Gtk.Template.Child("switch")
    
    def __init__(self):
        super().__init__()
        
        # Set size request
        self.set_size_request(280, 200)
        
        # Extension data
        self.extension_id = None
        self.extension_manager = None
        
    def load_extension(self, extension_data, extension_manager):
        """Load extension data into the card"""
        self.extension_id = extension_data.get('id')
        self.extension_manager = extension_manager
        
        # Set name and description
        if hasattr(self, 'name_label') and self.name_label:
            name = extension_data.get('name', '')
            self.name_label.set_text(name)
        
        if hasattr(self, 'desc_label') and self.desc_label:
            # Get description from our translations dictionary
            description = EXTENSION_DESCRIPTIONS.get(self.extension_id, extension_data.get('description', ''))
            self.desc_label.set_text(description)
        
        # Set image size if template child is available
        if hasattr(self, 'image') and self.image:
            self.image.set_size_request(200, 120)
        
        # Load image
        image_path = extension_data.get('image', '')
        if image_path and os.path.exists(image_path) and hasattr(self, 'image') and self.image:
            try:
                texture = Gdk.Texture.new_from_filename(image_path)
                self.image.set_paintable(texture)
            except Exception as e:
                print(f"Error loading extension image {image_path}: {e}")
        
        # Set switch state
        if self.extension_manager and hasattr(self, 'switch') and self.switch:
            is_enabled = self.extension_manager.is_extension_enabled(self.extension_id)
            self.switch.set_active(is_enabled)
            
            # Connect switch signal
            self.switch.connect("state-set", self._on_switch_toggled)
        
        # Disable card if extension is not installed
        if self.extension_manager and not self.extension_manager.is_extension_installed(self.extension_id):
            self.set_sensitive(False)
            self.get_style_context().add_class("extension-card-disabled")
    
    def _on_switch_toggled(self, switch, state):
        """Handle switch toggle"""
        if self.extension_manager and self.extension_id:
            if state:
                self.extension_manager.enable_extension(self.extension_id)
            else:
                self.extension_manager.disable_extension(self.extension_id)

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/ExtensionPage.ui')
class ExtensionPage(Adw.PreferencesPage):
    __gtype_name__ = 'ExtensionPage'
    
    # Template children
    extensions_flowbox = Gtk.Template.Child("extensions_flowbox")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize extension manager
        self.extension_manager = ExtensionManager()
        self.extension_cards = {}
        
        # Load extensions
        self._load_extensions()
        
        print("ExtensionPage created.")
    
    def _load_extensions(self):
        """Load and display extensions"""
        extensions = self.extension_manager.get_sorted_extensions()
        
        for extension in extensions:
            card = ExtensionCard()
            card.load_extension(extension, self.extension_manager)
            
            child = Gtk.FlowBoxChild()
            child.set_child(card)
            self.extensions_flowbox.append(child)
            self.extension_cards[extension['id']] = card 