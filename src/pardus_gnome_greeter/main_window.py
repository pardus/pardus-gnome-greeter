import locale
import gi
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib

from .pages.welcome import WelcomePage
from .pages.layout import LayoutPage
from .pages.theme import ThemePage
from .pages.wallpaper import WallpaperPage
from .pages.display import DisplayPage
from .pages.extension import ExtensionPage
from .pages.applications import ApplicationsPage
from .pages.time import TimePage
from .pages.outro import OutroPage
from .components.AboutDialog import create_about_dialog

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/MainWindow.ui')
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    split_view = Gtk.Template.Child("split_view")

    def __init__(self, start_page=None, **kwargs):
        super().__init__(**kwargs)
        
        # Set minimum window size (but still resizable)
        self.set_size_request(765, 750)

        # Load custom CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/tr/org/pardus/pardus-gnome-greeter/css/style.css')
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # 1. Create the Sidebar
        self.pages_listbox = Gtk.ListBox()
        self.pages_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.pages_listbox.add_css_class("navigation-sidebar")
        
        # Simple label instead of AdwHeaderBar
        sidebar_label = Gtk.Label(label=_("Settings"))
        sidebar_label.add_css_class("title-2")
        sidebar_label.set_margin_start(24)
        sidebar_label.set_margin_end(12)
        sidebar_label.set_margin_top(10)
        sidebar_label.set_margin_bottom(10)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_child(self.pages_listbox)
        
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.append(sidebar_label)
        sidebar_box.append(scrolled_window)

        # 2. Create the Content Area
        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)
        self.view_stack.set_hexpand(True)
        self.view_stack.set_size_request(0, -1)  # Allow shrinking
        
        # Create HeaderBar
        content_header = Adw.HeaderBar()
        content_header.add_css_class("content-header")
        
        # Menu button
        self.menu_button = Gtk.Button.new_from_icon_name("open-menu-symbolic")
        self.menu_button.connect('clicked', self._on_menu_button_clicked)
        content_header.pack_start(self.menu_button)

        # About button (to the left, next to menu button)
        self.about_button = Gtk.Button.new_from_icon_name("help-about-symbolic")
        self.about_button.set_tooltip_text(_("About"))
        self.about_button.connect('clicked', self._on_about_button_clicked)
        content_header.pack_start(self.about_button)
        
        content_title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.content_title_icon = Gtk.Image.new_from_icon_name("go-home-symbolic")
        self.content_title_label = Gtk.Label(label=_("Welcome"))
        content_title_box.append(self.content_title_icon)
        content_title_box.append(self.content_title_label)
        content_header.set_title_widget(content_title_box)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_size_request(0, -1)  # Allow shrinking
        content_box.append(content_header)
        content_box.append(self.view_stack)
        
        # Navigation Bar
        self.setup_navigation_bar(content_box)

        # 3. Assign the created widgets to the SplitView
        self.split_view.set_sidebar(sidebar_box)
        self.split_view.set_content(content_box)
        
        # Set sidebar width for responsive behavior (very narrow for mobile)
        self.split_view.set_min_sidebar_width(190)
        self.split_view.set_max_sidebar_width(260)
        
        # Allow content to shrink
        content_box.set_hexpand(True)
        self.view_stack.set_hexpand(True)
        
        self.load_pages()
        self.pages_listbox.connect('row-activated', self._on_row_activated)
        self.split_view.connect('notify::collapsed', self._on_split_view_collapsed)

        # Set start page if provided
        if start_page:
            for row in self.pages_listbox:
                if row.get_name() == start_page:
                    self.pages_listbox.select_row(row)
                    self.view_stack.set_visible_child_name(row.get_name())
                    break
            else: # If loop finishes without break
                self.pages_listbox.select_row(self.pages_listbox.get_row_at_index(0))
        else:
            self.pages_listbox.select_row(self.pages_listbox.get_row_at_index(0))

        self._on_split_view_collapsed(self.split_view, None)
        
        # Initial button state update
        self._update_navigation_buttons()


    def setup_navigation_bar(self, content_box):
        """Creates and appends the navigation bar to the content box"""
        
        # Main container for navigation buttons
        self.nav_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.nav_bar.set_margin_start(36)
        self.nav_bar.set_margin_end(36)
        self.nav_bar.set_margin_bottom(36)
        self.nav_bar.set_margin_top(24) # Increased top margin
        self.nav_bar.set_valign(Gtk.Align.END)
        self.nav_bar.add_css_class("navigation-bar")

        # Previous Button (Left aligned - Text only)
        self.prev_button = Gtk.Button(label=_("Previous"))
        self.prev_button.add_css_class("flat")
        self.prev_button.add_css_class("accent-color")
        self.prev_button.set_valign(Gtk.Align.CENTER)
        self.prev_button.connect("clicked", self._on_prev_clicked)
        self.nav_bar.append(self.prev_button)

        # Spacer to push Next button to the right
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.nav_bar.append(spacer)

        # Next Button (Right aligned - Filled)
        self.next_button = Gtk.Button()
        self.next_button.add_css_class("suggested-action")
        self.next_button.set_size_request(130, 46)
        self.next_button.set_valign(Gtk.Align.CENTER)
        self.next_button.connect("clicked", self._on_next_clicked)
        
        # Create custom content for Next button
        next_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.next_button_label = Gtk.Label(label=_("Next"))
        # self.next_button_icon = Gtk.Image.new_from_icon_name("go-next-symbolic") # Icon optional based on image
        
        next_box.append(self.next_button_label)
        # next_box.append(self.next_button_icon) 
        next_box.set_halign(Gtk.Align.CENTER)
        self.next_button.set_child(next_box)
        
        self.nav_bar.append(self.next_button)

        # Add nav bar to content box
        content_box.append(self.nav_bar)

    def _update_navigation_buttons(self):
        """Updates the state of navigation buttons based on current page"""
        selected_row = self.pages_listbox.get_selected_row()
        if not selected_row:
            return

        index = selected_row.get_index()
        
        # Count visible rows manually
        total_pages = 0
        i = 0
        while self.pages_listbox.get_row_at_index(i):
            i += 1
        total_pages = i

        # Update Previous Button
        self.prev_button.set_visible(index > 0)
        self.prev_button.set_sensitive(index > 0)

        # Update Next Button
        if index == 0:
            # Welcome page: Hide Next button (has its own start button)
            self.next_button.set_visible(False)
        elif index == total_pages - 1:
            # Last page (Outro): Hide Next/Finish button (has its own finish button)
            self.next_button.set_visible(False)
        else:
            # Normal pages: Show Next button
            self.next_button.set_visible(True)
            self.next_button_label.set_label(_("Next"))
            # self.next_button_icon.set_from_icon_name("go-next-symbolic")

    def _on_prev_clicked(self, button):
        selected_row = self.pages_listbox.get_selected_row()
        if selected_row:
            current_index = selected_row.get_index()
            if current_index > 0:
                prev_row = self.pages_listbox.get_row_at_index(current_index - 1)
                if prev_row:
                    self.pages_listbox.select_row(prev_row)
                    self._on_row_activated(self.pages_listbox, prev_row)

    def _on_next_clicked(self, button):
        selected_row = self.pages_listbox.get_selected_row()
        if selected_row:
            current_index = selected_row.get_index()
            # Check if it's the last page
            next_row = self.pages_listbox.get_row_at_index(current_index + 1)
            if next_row:
                self.pages_listbox.select_row(next_row)
                self._on_row_activated(self.pages_listbox, next_row)
            else:
                # It's the last page (Finish action)
                self.close()

    def _on_navigate_request(self, widget, page_name):
        # Find the row corresponding to the page name and activate it
        for row in self.pages_listbox:
            if row.get_name() == page_name:
                self.pages_listbox.select_row(row)
                self._on_row_activated(self.pages_listbox, row)
                break

    def _on_menu_button_clicked(self, button):
        self.split_view.set_show_sidebar(not self.split_view.get_show_sidebar())

    def _on_about_button_clicked(self, button):
        about_dialog = create_about_dialog()
        about_dialog.present()

    def _on_split_view_collapsed(self, split_view, param):
        is_collapsed = self.split_view.get_collapsed()
        self.menu_button.set_visible(is_collapsed)

    def _on_row_activated(self, listbox, row):
        name = row.get_name()
        self.view_stack.set_visible_child_name(name)
        # Update the title
        list_box_row_child = row.get_child()
        # The second element in the default Gtk.Box is the Gtk.Label
        page_title = list_box_row_child.get_last_child().get_label()
        icon_name = row.icon_name
        self.content_title_label.set_label(page_title)
        self.content_title_icon.set_from_icon_name(icon_name)

        if self.split_view.get_collapsed():
            self.split_view.set_show_sidebar(False)
            
        self._update_navigation_buttons()


    
    def load_pages(self):
        # Create and add pages to the ViewStack
        pages = [
            {"name": "welcome", "title": _("Welcome"), "icon": "go-home-symbolic", "class": WelcomePage},
            {"name": "layout", "title": _("Layout"), "icon": "view-paged-symbolic", "class": LayoutPage},
            {"name": "theme", "title": _("Theme"), "icon": "applications-graphics-symbolic", "class": ThemePage},
            {"name": "wallpaper", "title": _("Wallpaper"), "icon": "image-x-generic-symbolic", "class": WallpaperPage},
            {"name": "display", "title": _("Display"), "icon": "video-display-symbolic", "class": DisplayPage},
            {"name": "extension", "title": _("Extensions"), "icon": "org.gnome.Shell.Extensions-symbolic", "class": ExtensionPage},
            {"name": "applications", "title": _("Applications"), "icon": "view-app-grid-symbolic", "class": ApplicationsPage},
            {"name": "time", "title": _("Time"), "icon": "org.gnome.Settings-time-symbolic", "class": TimePage},
            {"name": "outro", "title": _("Finish"), "icon": "application-exit-symbolic", "class": OutroPage},
        ]

        for page_info in pages:
            page = page_info["class"]()
            if page_info["name"] == "welcome":
                page.connect("navigate-to", self._on_navigate_request)
            self.view_stack.add_named(page, page_info["name"])

            row = Gtk.ListBoxRow(name=page_info["name"])
            row.icon_name = page_info["icon"]
            
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            
            icon = Gtk.Image.new_from_icon_name(page_info["icon"])
            icon.set_pixel_size(16)
            label = Gtk.Label.new(page_info["title"])
            label.set_xalign(0)

            box.append(icon)
            box.append(label)

            row.set_child(box)
            self.pages_listbox.append(row)
        
        self.pages_listbox.select_row(self.pages_listbox.get_row_at_index(0)) 