import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio

from .pages.welcome import WelcomePage
from .pages.layout import LayoutPage
from .pages.theme import ThemePage
from .pages.wallpaper import WallpaperPage
from .pages.display import DisplayPage
from .pages.extension import ExtensionPage
from .pages.applications import ApplicationsPage
from .pages.outro import OutroPage

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/MainWindow.ui')
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    split_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. Create the Sidebar
        self.pages_listbox = Gtk.ListBox()
        self.pages_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.pages_listbox.add_css_class("navigation-sidebar")
        
        sidebar_header = Adw.HeaderBar()
        sidebar_title = Adw.WindowTitle(title="Settings")
        sidebar_header.set_title_widget(sidebar_title)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_child(self.pages_listbox)
        
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.append(sidebar_header)
        sidebar_box.append(scrolled_window)

        # 2. Create the Content Area
        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)
        
        # Menu button
        self.menu_button = Gtk.Button.new_from_icon_name("open-menu-symbolic")
        self.menu_button.connect('clicked', self._on_menu_button_clicked)

        content_header = Adw.HeaderBar()
        content_header.pack_start(self.menu_button)
        self.content_title = Adw.WindowTitle(title="Welcome")
        content_header.set_title_widget(self.content_title)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.append(content_header)
        content_box.append(self.view_stack)

        # 3. Assign the created widgets to the SplitView
        self.split_view.set_sidebar(sidebar_box)
        self.split_view.set_content(content_box)
        
        self.load_pages()
        self.pages_listbox.connect('row-activated', self._on_row_activated)
        self.split_view.connect('notify::collapsed', self._on_split_view_collapsed)

        self.pages_listbox.select_row(self.pages_listbox.get_row_at_index(0))
        self._on_split_view_collapsed(self.split_view, None)


    def _on_menu_button_clicked(self, button):
        self.split_view.set_show_sidebar(not self.split_view.get_show_sidebar())

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
        self.content_title.set_title(page_title)

        if self.split_view.get_collapsed():
            self.split_view.set_show_sidebar(False)

    def load_pages(self):
        # Create and add pages to the ViewStack
        pages = [
            {"name": "welcome", "title": "Welcome", "icon": "go-home-symbolic", "class": WelcomePage},
            {"name": "layout", "title": "Layout", "icon": "view-paged-symbolic", "class": LayoutPage},
            {"name": "theme", "title": "Theme", "icon": "org.gnome.Settings-appearance-symbolic", "class": ThemePage},
            {"name": "wallpaper", "title": "Wallpaper", "icon": "image-x-generic-symbolic", "class": WallpaperPage},
            {"name": "display", "title": "Display", "icon": "video-display-symbolic", "class": DisplayPage},
            {"name": "extension", "title": "Extensions", "icon": "puzzle-piece-symbolic", "class": ExtensionPage},
            {"name": "applications", "title": "Applications", "icon": "view-app-grid-symbolic", "class": ApplicationsPage},
            {"name": "outro", "title": "Finish", "icon": "emoji-celebrate-symbolic", "class": OutroPage},
        ]

        for page_info in pages:
            page = page_info["class"]()
            self.view_stack.add_named(page, page_info["name"])

            row = Gtk.ListBoxRow(name=page_info["name"])
            
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            box.set_margin_top(6)
            box.set_margin_bottom(6)
            
            icon = Gtk.Image.new_from_icon_name(page_info["icon"])
            label = Gtk.Label.new(page_info["title"])
            label.set_xalign(0)

            box.append(icon)
            box.append(label)

            row.set_child(box)
            self.pages_listbox.append(row)
        
        self.pages_listbox.select_row(self.pages_listbox.get_row_at_index(0)) 