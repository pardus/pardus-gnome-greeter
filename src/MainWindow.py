import gi
import os
import sys
import json
import locale
import threading

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from libpardus import Ptk
from Keybindings import Keybindings
from gi.repository import Adw, Gtk, GLib
from locale import gettext as _
from Pages import Welcome, Layout, Wallpaper, Theme, Display, Extension, Outro, Apps


VERSION = "0.0.1"
APPNAME = "Pardus Gnome Greeter"
DEV = "Osman Coskun"
WEBSITE = "https://github.com/pardus/pardus-gnome-greeter"
ICON = "tr.org.pardus.pardus-gnome-greeter.desktop"

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"
locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)


class MainWindow(Ptk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = Ptk.ApplicationWindow(
            title=_("Pardus Gnome Greeter"), width=1000, height=600
        )
        Ptk.utils.load_css("../data/style.css")
        with open("../data/shortcuts.json") as shortcut_json_file:
            self.shortcuts = json.loads(shortcut_json_file.read())

        with open("../data/custom_shortcuts.json") as custom_shortcuts_json_file:
            self.custom_shortcuts = json.loads(custom_shortcuts_json_file.read())
        self.schema = "org.pardus.pardus-gnome-greeter"
        self.first_run = bool(Ptk.utils.gsettings_get(self.schema,"first-run"))
        if self.first_run:
            self.fun_set_shortcuts()
            self.fun_set_custom_shortcuts()
            Ptk.utils.gsettings_set(self.schema,"first-run",GLib.Variant.new_boolean(False))


        self.Apps = Apps.Apps()
        self.result = None
        self.ui_leaflet_main_window = Adw.Leaflet()
        self.current_page = 0

        self.page_datas = [
            {
                "id": "ui_welcome_listboxrow",
                "page": Welcome.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Welcome"),
                "icon": "go-home-symbolic",
            },
            {
                "id": "ui_layout_listboxrow",
                "page": Layout.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Layout"),
                "icon": "edit-copy",
            },
            {
                "id": "ui_wallpaper_listboxrow",
                "page": Wallpaper.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Wallpaper"),
                "icon": "emblem-photos-symbolic",
            },
            {
                "id": "ui_theme_listboxrow",
                "page": Theme.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Theme"),
                "icon": "org.gnome.Settings-appearance-symbolic",
            },
            {
                "id": "ui_display_listboxrow",
                "page": Display.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Display"),
                "icon": "video-display-symbolic",
            },
            {
                "id": "ui_extensions_listboxrow",
                "page": Extension.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Extension"),
                "icon": "org.gnome.Shell.Extensions-symbolic",
            },
            {
                "id": "ui_applications_listboxrow",
                "page": self.Apps.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Applications"),
                "icon": "view-grid-symbolic",
            },
            {
                "id": "ui_outro_listboxrow",
                "page": Outro.fun_create(),
                "listboxrow": None,
                "togglebutton": None,
                "text": _("Outro"),
                "icon": "info-symbolic",
            },
        ]

        self.ui_pages_stack = Ptk.Stack(hexpand=True, vexpand=True)
        self.ui_pages_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )
        self.ui_prev_button = Ptk.Button(name="prev", hexpand=True, label=_("Previous"))
        self.ui_prev_button.connect(
            "clicked", self.fun_change_page_with_next_prev_buttons
        )
        self.ui_next_button = Ptk.Button(name="next", hexpand=True, label=_("Next"))
        self.ui_next_button.connect(
            "clicked", self.fun_change_page_with_next_prev_buttons
        )
        self.ui_navigation_buttons_box = Ptk.Box(
            spacing=23,
            hexpand=True,
            children=[self.ui_prev_button, self.ui_next_button],
        )
        self.ui_pages_box = Ptk.Box(
            hexpand=True,
            orientation="vertical",
            children=[self.ui_pages_stack, self.ui_navigation_buttons_box],
        )

        self.ui_listbox_pages = Ptk.ListBox(
            show_seperators=True, css=["navigation-sidebar"]
        )
        self.ui_markup = (
            f"<span size='x-large'><b>{_('Pardus Gnome Greeter')}</b></span>"
        )
        self.ui_application_title = Ptk.Label(markup=self.ui_markup, valign="center")
        self.ui_header_toggles_box = Ptk.Box(css=["linked"])

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
        self.separator = Ptk.Separator("vertical")
        self.ui_leaflet_main_window.append(self.ui_listbox_pages)
        self.ui_leaflet_main_window.append(self.separator)
        self.ui_leaflet_main_window.append(self.ui_pages_box)

        self.ui_leaflet_main_window.set_visible_child(self.ui_pages_box)

        self.ui_header_headerbar = Adw.HeaderBar()
        self.ui_header_headerbar.set_centering_policy(Adw.CenteringPolicy.LOOSE)
        self.ui_header_headerbar.set_hexpand(True)
        self.ui_header_headerbar.set_overflow(Gtk.Overflow.VISIBLE)
        self.ui_header_headerbar.set_accessible_role(Gtk.AccessibleRole.GROUP)

        self.ui_about_button = Ptk.Button(icon="open-menu-symbolic")
        self.ui_about_button.connect("clicked", self.fun_show_about)

        self.ui_header_headerbar.pack_start(self.ui_about_button)
        self.ui_header_headerbar.set_title_widget(self.ui_header_toggles_box)

        self.ui_listbox_pages.connect("map", self.widget_show)
        self.ui_listbox_pages.connect("unmap", self.widget_hide)
        self.ui_listbox_pages.connect("row_activated", self.fun_change_page)

        self.fun_check_navigation_buttons()
        self.change_page()
        self.window.set_titlebar(self.ui_header_headerbar)
        self.window.set_child(self.ui_leaflet_main_window)

    def fun_set_custom_shortcuts(self):
        for custom_short in self.custom_shortcuts:
            id, name, binding, command = custom_short.values()
            Keybindings.set_custom_keybinding(self,id, name, binding, command)

    def fun_set_shortcuts(self):
        for shortcut in self.shortcuts:
            schema, key, binding = shortcut.values()
            Keybindings.set_keybinding(self,schema, key, binding)

    def fun_create_navigation_listbox(self, data):
        icon = Ptk.Image(icon=data["icon"])
        label = Ptk.Label(label=data["text"])
        listboxrow_box = Ptk.Box(spacing=13, children=[icon, label], valign="center")
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
        box = Ptk.Box(orientation="vertical", children=[avatar])
        toggle_button.set_child(box)
        return toggle_button

    def widget_show(self, widget):
        self.ui_header_toggles_box.hide()
        self.ui_header_headerbar.set_title_widget(self.ui_application_title)

    def widget_hide(self, widget):
        self.ui_header_toggles_box.show()
        self.ui_header_headerbar.set_title_widget(self.ui_header_toggles_box)

    def fun_change_page_with_next_prev_buttons(self, widget):
        name = widget.get_name()
        label = widget.get_label()
        if label == _("Close"):
            self.window.get_application().quit()
        if name == "prev":
            self.current_page -= 1
        else:
            self.current_page += 1

        self.fun_check_navigation_buttons()
        self.change_page()

    def fun_change_page(self, action, name):
        self.current_page = name.get_index()
        self.change_page()

    def fun_check_navigation_buttons(self):
        if self.current_page == 0:
            self.ui_prev_button.set_sensitive(False)
        else:
            self.ui_prev_button.set_sensitive(True)
        if self.current_page == len(self.page_datas) - 1:
            self.ui_next_button.set_label(_("Close"))

    def fun_change_page_with_toggle_button(self, toggle_button):
        state = toggle_button.get_active()
        self.current_page = int(toggle_button.get_name())

        if state:
            self.fun_check_navigation_buttons()
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
        dialog = Ptk.AboutWindow(
            application_name=APPNAME,
            version=VERSION,
            developer_name=APPNAME,
            license_type="GPL-3",
            comments=_("Configure Pardus with few clicks"),
            website=WEBSITE,
            issue_url=WEBSITE,
            credit_section=[_("Contributors"), [DEV]],
            translator_credits=DEV,
            copyright="© 2023 Ulakbim / Pardus",
            developers=[DEV],
            application_icon=ICON,
            transient_for=self.window,
            modal=True,
        )
        dialog.show()

    def fun_quit_application(self):
        self.quit()
