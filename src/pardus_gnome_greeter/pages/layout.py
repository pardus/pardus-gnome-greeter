import locale
import gi
import os
import threading
import time
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio, GdkPixbuf, Gdk, GObject

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

from ..managers.LayoutManager import LayoutManager


class GifPaintable(GObject.Object, Gdk.Paintable):
    def __init__(self, path):
        super().__init__()
        self.animation = GdkPixbuf.PixbufAnimation.new_from_file(path)
        self.iterator = self.animation.get_iter()
        self.delay = self.iterator.get_delay_time()
        self.timeout = GLib.timeout_add(self.delay, self.on_delay)

        self.invalidate_contents()

    def on_delay(self):
        delay = self.iterator.get_delay_time()
        self.timeout = GLib.timeout_add(delay, self.on_delay)
        self.invalidate_contents()

        return GLib.SOURCE_REMOVE

    def do_get_intrinsic_height(self):
        return self.animation.get_height()

    def do_get_intrinsic_width(self):
        return self.animation.get_width()

    def invalidate_contents(self):
        self.emit("invalidate-contents")

    def do_snapshot(self, snapshot, width, height):
        timeval = GLib.TimeVal()
        timeval.tv_usec = GLib.get_real_time()
        self.iterator.advance(timeval)
        pixbuf = self.iterator.get_pixbuf()
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)

        texture.snapshot(snapshot, width, height)


@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/LayoutPage.ui')
class LayoutPage(Adw.PreferencesPage):
    __gtype_name__ = 'LayoutPage'
    
    layouts_grid = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize layout manager
        try:
            self.layout_manager = LayoutManager()
        except Exception as e:
            print(f"Warning: Could not initialize LayoutManager: {e}")
            self.layout_manager = None
        
        self.current_layout = None
        self.layout_cards = {}
        
        # Manually translate UI elements
        self._translate_ui_elements()
        
        # Setup layouts
        self._setup_layouts()
        
        # Set initial selection
        self._set_initial_selection()
    
    def _translate_ui_elements(self):
        """Manually translate UI elements that are not automatically translated"""
        try:
            # Find and translate the title and subtitle labels
            title_label = self.get_template_child(self.__class__, "title_label")
            subtitle_label = self.get_template_child(self.__class__, "subtitle_label")
            
            if title_label:
                # Get the original text and translate it
                original_text = "Choose Your Desktop Layout"
                title_label.set_label(_(original_text))
            
            if subtitle_label:
                # Get the original text and translate it
                original_text = "Select a desktop layout that suits your workflow. You can change this anytime later."
                subtitle_label.set_label(_(original_text))
                
        except Exception as e:
            print(f"Warning: Could not translate UI elements: {e}")
    
    def _setup_layouts(self):
        """Setup layout cards in fixed 2x3 grid"""
        if not self.layout_manager:
            return
            
        layouts = self.layout_manager.get_available_layouts()
        
        # Layout display information
        layout_info = {
            'gnome': {'name': _('Classic GNOME'), 'description': _('Traditional GNOME desktop experience')},
            'mac': {'name': _('Mac Style'), 'description': _('macOS-like interface with dock at bottom')},
            'ubuntu': {'name': _('Ubuntu Style'), 'description': _('Ubuntu Unity-like experience')},
            '10': {'name': _('Windows 10'), 'description': _('Windows 10 taskbar layout')},
            'xp': {'name': _('Windows XP'), 'description': _('Classic Windows XP experience')},
            'pardus': {'name': _('Pardus Style'), 'description': _('Custom Pardus desktop layout')}
        }
        
        # Fixed 2x3 grid layout
        layout_order = ['gnome', 'mac', 'ubuntu', '10', 'xp', 'pardus']
        
        row, col = 0, 0
        for layout_name in layout_order:
            if layout_name in layouts:
                info = layout_info.get(layout_name, {'name': layout_name.title(), 'description': f'{layout_name.title()} layout'})
                card = self._create_layout_card(layout_name, info['name'], info['description'])
                self.layout_cards[layout_name] = card
                
                # Place in 2x3 grid
                self.layouts_grid.attach(card, col, row, 1, 1)
                
                col += 1
                if col >= 3:  # 3 columns per row, so wrap to next row
                    col = 0
                    row += 1
    
    def _set_initial_selection(self):
        """Set the initial selection based on the current layout"""
        if self.layout_manager:
            try:
                current_layout_name = self.layout_manager.get_current_layout()
                if current_layout_name:
                    self._update_selection(current_layout_name)
            except Exception as e:
                print(f"Failed to set initial layout selection: {e}")

    def _create_layout_card(self, layout_id, name, description):
        """Create a layout card widget"""
        # Main card container with fixed size
        card = Gtk.Button()
        # Fixed size for all cards
        card.set_size_request(220, 160)  # Fixed width and height for all
        card.add_css_class("card")
        card.set_halign(Gtk.Align.CENTER)
        card.set_valign(Gtk.Align.CENTER)
        
        # Card content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_margin_top(16)
        content_box.set_margin_bottom(16)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)
        content_box.set_halign(Gtk.Align.CENTER)
        content_box.set_valign(Gtk.Align.CENTER)
        
        # Image container
        image_container = Gtk.Box()
        image_container.set_size_request(120, 120)  # Fixed image size
        image_container.set_halign(Gtk.Align.CENTER)
        image_container.set_valign(Gtk.Align.CENTER)
        image_container.set_homogeneous(True)  # Center box children
        
        # Create single picture widget (no stack needed)
        picture = Gtk.Picture()
        picture.set_size_request(120, 120)
        picture.set_can_shrink(True)
        picture.set_keep_aspect_ratio(True)
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        picture.set_halign(Gtk.Align.CENTER)
        picture.set_valign(Gtk.Align.CENTER)
        picture.add_css_class("layout-image")
        
        # Load static image initially
        static_path = f"data/assets/layouts/layout-{layout_id}.svg"
        if os.path.exists(static_path):
            picture.set_filename(static_path)
        
        image_container.append(picture)
        
        # Layout name
        name_label = Gtk.Label(label=name)
        name_label.add_css_class("heading")
        name_label.set_halign(Gtk.Align.CENTER)
        name_label.set_valign(Gtk.Align.CENTER)
        
        # Layout description
        desc_label = Gtk.Label(label=description)
        desc_label.add_css_class("caption")
        desc_label.add_css_class("dim-label")
        desc_label.set_halign(Gtk.Align.CENTER)
        desc_label.set_valign(Gtk.Align.CENTER)
        desc_label.set_wrap(True)
        desc_label.set_max_width_chars(22)
        desc_label.set_justify(Gtk.Justification.CENTER)
        
        # Add to content box
        content_box.append(image_container)
        content_box.append(name_label)
        content_box.append(desc_label)
        
        card.set_child(content_box)
        
        # Store references for hover effects
        card.picture = picture
        card.layout_id = layout_id
        card.static_path = static_path
        card.gif_path = f"data/assets/layouts/layout-{layout_id}.gif"
        
        # Connect signals
        card.connect("clicked", self._on_layout_selected)
        
        # Hover effects using motion controllers
        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("enter", self._on_card_enter)
        motion_controller.connect("leave", self._on_card_leave)
        card.add_controller(motion_controller)
        
        return card

    def _on_card_enter(self, controller, x, y):
        """Handle mouse enter on card"""
        card = controller.get_widget()
        
        # Switch to GIF using GifPaintable
        if os.path.exists(card.gif_path):
            try:
                gif_paintable = GifPaintable(card.gif_path)
                card.picture.set_paintable(gif_paintable)
            except Exception as e:
                print(f"Error loading GIF: {e}")
        
        # Add hover style
        card.add_css_class("card-hover")
    
    def _on_card_leave(self, controller):
        """Handle mouse leave from card"""
        card = controller.get_widget()
        
        # Switch back to static image
        if os.path.exists(card.static_path):
            card.picture.set_filename(card.static_path)
        
        # Remove hover style
        card.remove_css_class("card-hover")
    
    def _on_layout_selected(self, button):
        """Handle layout selection"""
        layout_id = button.layout_id
        
        if not self.layout_manager:
            print("Layout manager not available")
            return
        
        # Update visual selection
        self._update_selection(layout_id)
        
        # Apply layout directly; the manager handles asynchronicity
        self.layout_manager.apply_layout(layout_id)
    
    def _update_selection(self, selected_layout):
        """Update visual selection of cards"""
        for layout_name, card in self.layout_cards.items():
            if layout_name == selected_layout:
                card.add_css_class("selected")
                self.current_layout = selected_layout
            else:
                card.remove_css_class("selected")
    
    def _apply_layout_threaded(self, layout_id):
        """Apply layout in background thread"""
        try:
            print(f"Applying layout: {layout_id}")
            self.layout_manager.apply_layout(layout_id)
            
            # Show success notification on main thread
            GLib.idle_add(self._show_success_notification, layout_id)
            
        except Exception as e:
            print(f"Error applying layout {layout_id}: {e}")
            GLib.idle_add(self._show_error_notification, layout_id, str(e))
    
    def _show_success_notification(self, layout_id):
        """Show success notification"""
        # You can implement a toast notification here if available
        print(f"Layout '{layout_id}' applied successfully!")
        return False  # Remove from idle queue
    
    def _show_error_notification(self, layout_id, error_msg):
        """Show error notification"""
        print(f"Failed to apply layout '{layout_id}': {error_msg}")
        return False  # Remove from idle queue 