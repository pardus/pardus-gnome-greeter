import gi
import sys
import threading

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

sys.path.append("../")
from data.lib.pardus import Ptk
from gi.repository import Adw, Gtk
from Pages import Welcome, Layout, Wallpaper, Theme, Display, Extension, Outro

VERSION = "0.0.1"
APPNAME = "Pardus Gnome Greeter"
DEV = "Osman Coskun"
WEBSITE = "https://github.com/pardus/pardus-gnome-greeter"
ICON = "tr.org.pardus.pardus-gnome-greeter.desktop"


class MainWindow(Ptk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = Ptk.ApplicationWindow(
            title="Pardus Gnome Greeter", width=1100, height=600
        )
        Ptk.utils.load_css("../data/style.css")

        self.ui_leaflet_main_window = Adw.Leaflet()
        self.current_page = 0
        self.page_datas = [
            {
                "id": "ui_welcome_listboxrow",
                "page": Welcome.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": "Welcome",
                "icon": "go-home-symbolic",
            },
            {
                "id": "ui_layout_listboxrow",
                "page": Layout.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": "Layout",
                "icon": "focus-windows-symbolic",
            },
            {
                "id": "ui_wallpaper_listboxrow",
                "page": Wallpaper.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": "Wallpaper",
                "icon": "preferences-desktop-wallpaper-symbolic",
            },
            {
                "id": "ui_theme_listboxrow",
                "page": Theme.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": "Theme",
                "icon": "palette-symbolic",
            },
            {
                "id": "ui_display_listboxrow",
                "page": Display.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": "Display",
                "icon": "display-symbolic",
            },
            {
                "id": "ui_extensions_listboxrow",
                "page": Extension.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": "Extension",
                "icon": "extensions-symbolic",
            },
            {
                "id": "ui_outro_listboxrow",
                "page": Outro.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": "Outro",
                "icon": "gtk-about-symbolic",
            },
        ]

        self.ui_pages_stack = Ptk.Stack(
            hexpand=True, vexpand=True, width=900, height=700
        )

        self.ui_listbox_pages = Ptk.ListBox(show_seperators=True)
        self.ui_application_title = Ptk.Label(
            markup="<span size='x-large'><b>Pardus Gnome Greeter</b></span>",
            valign="center",
        )
        self.ui_header_toggles_box = Ptk.Box()

        for index, data in enumerate(self.page_datas):
            if data["page"] != None:
                self.ui_pages_stack.add_child(data["page"])

            listboxrow = self.fun_create_navigation_listbox(data=data)
            data["listboxrow"] = listboxrow
            self.ui_listbox_pages.append(data["listboxrow"])

            togglebutton = self.fun_create_navigation_togglebutton(
                data=data, index=index
            )
            data["togglebutton"] = togglebutton

            self.ui_header_toggles_box.append(togglebutton)

        self.ui_leaflet_main_window.append(self.ui_listbox_pages)
        self.ui_leaflet_main_window.append(self.ui_pages_stack)

        self.ui_leaflet_main_window.set_visible_child(self.ui_pages_stack)

        self.ui_header_headerbar = Adw.HeaderBar()

        self.ui_about_button = Ptk.Button(css=["rounded"], icon="open-menu-symbolic")
        self.ui_about_button.connect("clicked", self.fun_show_about)

        self.ui_header_headerbar.pack_start(self.ui_about_button)
        self.ui_header_headerbar.set_title_widget(self.ui_header_toggles_box)

        self.ui_listbox_pages.connect("map", self.widget_show)
        self.ui_listbox_pages.connect("unmap", self.widget_hide)
        self.ui_listbox_pages.connect("row_activated", self.fun_change_page)

        self.window.set_titlebar(self.ui_header_headerbar)
        self.window.set_child(self.ui_leaflet_main_window)

    def fun_create_navigation_listbox(self, data):
        icon = Ptk.Image(icon=data["icon"])
        label = Ptk.Label(label=data["text"])
        listboxrow_box = Ptk.Box(spacing=13, children=[icon, label])
        listboxrow = Ptk.ListBoxRow(
            css=["listboxrow"], name=data["id"], child=listboxrow_box
        )
        return listboxrow

    def fun_create_navigation_togglebutton(self, data, index):
        avatar = Ptk.Image(icon=data["icon"], pixel_size=21)

        toggle_button = Ptk.ToggleButton(
            name=str(index), group=self.ui_header_toggles_box.get_first_child()
        )
        if index == 0:
            toggle_button.set_active(True)
        toggle_button.connect("toggled", self.fun_change_page_with_toggle_button)

        if index == 0:
            toggle_button.set_css_classes(["firstbuttonbox"])
        elif index == len(self.page_datas) - 1:
            toggle_button.set_css_classes(["lastbuttonbox"])
        else:
            toggle_button.set_css_classes(["buttonbox"])

        box = Ptk.Box(orientation="vertical", children=[avatar])
        toggle_button.set_child(box)
        return toggle_button

    def widget_show(self, widget):
        self.ui_header_toggles_box.hide()
        self.ui_header_headerbar.set_title_widget(self.ui_application_title)

    def widget_hide(self, widget):
        self.ui_header_toggles_box.show()
        self.ui_header_headerbar.set_title_widget(self.ui_header_toggles_box)

    def fun_change_page(self, action, name):
        self.current_page = name.get_index()
        self.change_page()

    def fun_change_page_with_toggle_button(self, toggle_button):
        state = toggle_button.get_active()
        self.current_page = int(toggle_button.get_name())
        if state:
            self.change_page()

    def change_page(self):
        self.ui_listbox_pages.select_row(
            self.page_datas[self.current_page]["listboxrow"]
        )
        self.page_datas[self.current_page]["togglebutton"].set_active(True)
        self.ui_pages_stack.set_visible_child(
            self.page_datas[self.current_page]["page"]
        )

    def fun_show_about(self, button):
        dialog = Adw.AboutWindow()
        dialog.set_application_name = APPNAME
        dialog.set_version(VERSION)
        dialog.set_developer_name(APPNAME)
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        dialog.set_comments("Configure Pardus with few clicks")
        dialog.set_website(WEBSITE)
        dialog.set_issue_url(WEBSITE)
        dialog.add_credit_section("Contributors", [DEV])
        dialog.set_translator_credits(DEV)
        dialog.set_copyright("© 2023 Ulakbim / Pardus")
        dialog.set_developers([DEV])
        dialog.set_application_icon(ICON)
        dialog.show()
