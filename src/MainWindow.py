import gi
import os, threading
import subprocess
import time
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf, GLib,Pango


from WallpaperManager import WallpaperManager
from LayoutManager import LayoutManager
from ScaleManager import ScaleManager
from ExtensionManager import ExtensionManager
from utils import get_current_theme, get_layout_name, get_recommended_scale

wallpaper_manager = WallpaperManager()
LayoutManager = LayoutManager()
scaleManager = ScaleManager()
extensionManager = ExtensionManager()

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # IMPORT CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(
            os.path.dirname(os.path.abspath(__file__)) + "/../css/style.css"
        )

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.init_ui()

    def init_ui(self):
        # GTK SETTINGS
        self.ellipsize = Pango.EllipsizeMode(2)
        self.horizontal = Gtk.Orientation.HORIZONTAL
        self.vertical = Gtk.Orientation.VERTICAL
        self.align_start = Gtk.Align(1)
        self.align_fill = Gtk.Align(0)
        self.align_center = Gtk.Align(3)

        # GETTING UI FROM UI FILE
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(
            os.path.dirname(os.path.abspath(__file__)) + "/../ui/ui.ui"
        )
        
        # MAIN WINDOW OF APPLICATION
        self.main_window = self.fun_get_ui("window")

        # CURRENT ACTIVE STACK PAGE INDEX
        self.current_page = 0

        # LEFT SIDE NAVIGATION
        self.ui_listbox_navigation = self.fun_get_ui("ui_listbox_navigation")
        self.ui_listbox_navigation.set_show_separators(True)
        self.ui_listbox_navigation.connect("row_activated", self.fun_change_page)

        # STACK PAGES CONTAINER
        self.ui_stack_pages = self.fun_get_ui("ui_stack_pages")

        # RIGHT SIDE OF APPLICATION
        self.ui_box_content = self.fun_get_ui("ui_box_content")
        self.ui_box_content.prepend(self.ui_stack_pages)
        
        # LISTBOXROWS
        self.ui_listbox_sidemenu = [
            self.fun_get_ui("ui_listboxrow_welcome"),
            self.fun_get_ui("ui_listboxrow_layout"),
            self.fun_get_ui("ui_listboxrow_wallpaper"),
            self.fun_get_ui("ui_listboxrow_theme"),
            self.fun_get_ui("ui_listboxrow_display"),
            self.fun_get_ui("ui_listboxrow_extensions"),
            self.fun_get_ui("ui_listboxrow_shortcut"),
        ]

        # STACK PAGES
        self.ui_pages = [
            self.fun_get_ui("ui_box_welcome"),
            self.fun_get_ui("ui_box_layout"),
            self.fun_get_ui("ui_box_wallpaper"),
            self.fun_get_ui("ui_box_theme"),
            self.fun_get_ui("ui_box_display"),
            self.fun_get_ui("ui_box_extensions"),
            self.fun_get_ui("ui_box_shortcut"),
        ]

        # BOTTOM NAVIGATION INDICATORS
        self.ui_image_indicators = {
            self.fun_get_ui("ui_stack_indicator_0"): {
                "on": self.fun_get_ui("ui_image_indicator_on_0"),
                "off": self.fun_get_ui("ui_image_indicator_off_0"),
            },
            self.fun_get_ui("ui_stack_indicator_1"): {
                "on": self.fun_get_ui("ui_image_indicator_on_1"),
                "off": self.fun_get_ui("ui_image_indicator_off_1"),
            },
            self.fun_get_ui("ui_stack_indicator_2"): {
                "on": self.fun_get_ui("ui_image_indicator_on_2"),
                "off": self.fun_get_ui("ui_image_indicator_off_2"),
            },
            self.fun_get_ui("ui_stack_indicator_3"): {
                "on": self.fun_get_ui("ui_image_indicator_on_3"),
                "off": self.fun_get_ui("ui_image_indicator_off_3"),
            },
            self.fun_get_ui("ui_stack_indicator_4"): {
                "on": self.fun_get_ui("ui_image_indicator_on_4"),
                "off": self.fun_get_ui("ui_image_indicator_off_4"),
            },
            self.fun_get_ui("ui_stack_indicator_5"): {
                "on": self.fun_get_ui("ui_image_indicator_on_5"),
                "off": self.fun_get_ui("ui_image_indicator_off_5"),
            },
            self.fun_get_ui("ui_stack_indicator_6"): {
                "on": self.fun_get_ui("ui_image_indicator_on_6"),
                "off": self.fun_get_ui("ui_image_indicator_off_6"),
            },
        }


        # PREVIOUS PAGE BUTTON

        self.ui_button_previous_page = self.fun_get_ui("ui_button_previous_page")
        self.ui_button_previous_page.connect("clicked", self.on_prev_page_button_clicked)

        # NEXT PAGE BUTTON
        self.ui_button_on_next_page= self.fun_get_ui("ui_button_next_page")
        self.ui_button_on_next_page.connect("clicked", self.on_next_page_button_clicked)


        # WELCOME PAGE SETTING SIZE OF LABEL
        self.ui_label_pardus23_label = self.fun_get_ui("ui_label_pardus23_label")
        self.ui_label_pardus23_label_content = self.ui_label_pardus23_label.get_label()
        self.ui_label_pardus23_label.set_markup(
            '<span size="36000">%s</span>' % self.ui_label_pardus23_label_content
        )

        # FLOWBOX WITH FLOWED ITEMS
        self.ui_flowbox_wallpapers = self.fun_get_ui("ui_flowbox_wallpapers")
        self.ui_flowbox_wallpapers.connect("child-activated", self.fun_change_wallpaper) 


        # BUTTONS ON THEME PAGE
        # DARK THEME BUTTON ON THEME PAGE    
        self.ui_button_dark_theme = self.fun_get_ui("ui_button_dark_theme")
        self.ui_button_dark_theme.connect("clicked", self.fun_change_theme, "dark")

        # LIGHT THEME BUTTON ON THEME PAGE
        self.ui_button_light_theme = self.fun_get_ui("ui_button_light_theme")
        self.ui_button_light_theme.connect("clicked", self.fun_change_theme, "light")
        
        # ABOUT DIALOG AND BUTTON
        self.ui_button_about_dialog = self.fun_get_ui("ui_button_about_dialog")
        self.ui_button_about_dialog.connect("clicked",self.init_about_dialog)
    

        thread = threading.Thread(
            target=self.init_wallpapers, args=(wallpaper_manager.get_wallpapers(),)
        )
        thread.daemon = True
        thread.start()

        self.fun_check_bottom_img_states()

        

        self.enabled_extensions = extensionManager.get_extensions("enabled")
        self.ui_flowbox_extensions = self.fun_get_ui("ui_flowbox_extensions")

        with open("../data/extensions.json") as file_content:
            self.extension_datas = json.loads(file_content.read())

        with open("../data/shortcuts.json") as file_content:
            self.shortcut_datas = json.loads(file_content.read())
        

        for item in self.extension_datas:
            extension = self.fun_create_extension_box(item)
            self.ui_flowbox_extensions.insert(extension,-1)
        
        self.shortcuts = self.fun_get_ui("shortcuts")

        self.toggle_buttons = []
        self.shortcut_pages = []


        #self.toggles = [
        #    self.fun_get_ui("toggle1"),
        #    self.fun_get_ui("toggle2"),
        #    self.fun_get_ui("toggle3"),
        #    self.fun_get_ui("toggle4"),
        #]
#
        #for toggle in self.toggles:
        #    toggle.connect("toggled",self.test_toggle)
        
        # INIT FUNCTIONS
        self.init_layout()
        self.init_scale()
        self.init_themes()
        self.init_shortcut()

    def test_toggle(self,widget):
        if widget.get_active():
            for index,active_toggle in enumerate(self.toggle_buttons):
                if active_toggle.get_active() == True:
                    self.ui_shortcut_stack.set_visible_child(self.shortcut_pages[index])

    def init_shortcut(self):
        # SHORTCUT OUTER BOX
        self.ui_box_shortcut = self.fun_get_ui("ui_box_shortcut")
        self.ui_box_shortcut.set_hexpand(True)
        self.ui_box_shortcut.set_vexpand(True)

        # SHORTCUT TOGGLE NAVIGATION BOX
        self.ui_toggle_nav_box = Gtk.Box()
        self.ui_toggle_nav_box.set_hexpand(True)
        self.ui_toggle_nav_box.set_homogeneous(True)

        self.toggle_group = None
        
        self.ui_shortcut_stack = Gtk.Stack()
        self.ui_shortcut_stack.set_hexpand(True)
        self.ui_shortcut_stack.set_vexpand(True)



        # ADDING TOGGLE BUTTONS TO SHORTCUT
        for index,toggle in enumerate(self.shortcut_datas):
            toggle_button = self.fun_create_shortcut_nav_button(toggle,index)
            shortcut_page = self.fun_create_shortcut_page(self.shortcut_datas[toggle], toggle)

            self.ui_shortcut_stack.add_child(shortcut_page)

            self.shortcut_pages.append(shortcut_page)
            self.toggle_buttons.append(toggle_button)
            self.ui_toggle_nav_box.append(toggle_button)
        
        self.ui_box_shortcut.append(self.ui_toggle_nav_box)
        self.ui_box_shortcut.append(self.ui_shortcut_stack)

    def fun_create_shortcut_page(self,content,id):

        page = Gtk.Box.new(self.vertical,5)


        page.set_hexpand(True)
        page.set_vexpand(True)
        page.set_halign(self.align_center)
        page.set_valign(self.align_start)
        
        
        for item in content:
            shortcut_box = Gtk.Box.new(self.vertical,5)
            shortcut_box.get_style_context().add_class("bordered-box")
            shortcut_box.set_halign(self.align_center)
            label_content = item['shortcut']
            label = Gtk.Label(label=label_content)
            shortcut_box.append(label)

            shortcut_buttons_box = Gtk.Box.new(self.horizontal,13)
            shortcut_buttons_box.get_style_context().add_class("bordered-box")
            shortcut_buttons_box.set_halign(self.align_center)
            shortcut_buttons_box.set_valign(self.align_fill)

            shortcut_box.append(shortcut_buttons_box)
            for shortcut_key in item['keys']:
                shortcut_buttons_box.append(Gtk.Button(label=shortcut_key))
            page.append(shortcut_box)
        return page

    def fun_create_shortcut_nav_button(self,label,index):
        toggle_button = Gtk.ToggleButton(label=label)
        toggle_button.set_css_classes(["togglebutton"])
        toggle_button.set_name(label)
        toggle_button.connect("toggled",self.test_toggle)

        if index == 0:
            toggle_button.set_group(None)
            self.toggle_group = toggle_button
        else:
            toggle_button.set_group(self.toggle_group)
        
        return toggle_button

    


    def fun_create_extension_box(self,extension_props):
        
        # RETURNING EXTENSION BOX
        # _______(Container)______________________________
        #|                                               |
        #|     _____(Header)_________________________    |
        #|    |   logo | extension name    | switch |    | 
        #|    ---------------------------------------    |
        #|                                               |
        #|     _____(description)___________________| 
        #|    | extension long description          |    |
        #|    |_____________________________________|    |
        #|    |                                     |    |
        #|    |    ___(Image)_________________      |    |
        #|    |   |                          |      |    |
        #|    |   |                          |      |    |
        #|    |   |                          |      |    |
        #|    |   |                          |      |    |
        #|    |   |__________________________|      |    |
        #|    |_____________________________________|    |
        #|                                               |
        #|_______________________________________________|

        

        # MAIN CONTAINER
        ui_box_container = Gtk.Box.new(self.vertical,13)
        ui_box_container.set_size_request(200,200)
        ui_box_container.get_style_context().add_class("bordered-box")
        ui_box_container.set_valign(self.align_start)
        ui_box_container.set_halign(self.align_start)
        

        # HEADER THAT GOT LOGO EXTENSION NAME AND SWITCH
        ui_box_header = Gtk.Box.new(self.horizontal,5)
        ui_box_header.set_valign(self.align_start)
        ui_box_header.set_halign(self.align_fill)
        ui_box_header.get_style_context().add_class("bordered-box")

        # EXTENSION LOGO
        ui_image_logo = Gtk.Image.new_from_file(extension_props["logo"])
        ui_image_logo.set_halign(self.align_start)

        # EXTENSION IMAGE
        ui_image_extension_image = Gtk.Image.new_from_file(extension_props["image"])
        ui_image_extension_image.set_size_request(130,160)

        # EXTENSION NAME
        ui_label_name = Gtk.Label(label=extension_props["name"])
        ui_label_name.set_hexpand(True)
        ui_label_name.set_halign(self.align_start)

        # SWITCH TO CONTROL STATE OF EXTENSION

        
        
        ui_switch_toggle = Gtk.Switch()
        ui_switch_toggle.connect("notify::active",self.fun_extension_toggle,extension_props["id"])
        ui_switch_toggle.set_sensitive(True)
        if extension_props["id"] in self.enabled_extensions:
            ui_switch_toggle.set_active(True)
        else:
            ui_switch_toggle.set_active(False)
        
        # ADDING ELEMENTS TO HEADER
        ui_box_header.append(ui_image_logo)
        ui_box_header.append(ui_label_name)
        ui_box_header.append(ui_switch_toggle)

        # EXTENSION DESCRIPTION
        ui_label_description = Gtk.Label(label=extension_props["description"])
        ui_label_description.set_halign(self.align_start)
        ui_label_description.set_valign(self.align_start)
        ui_label_description.set_ellipsize(self.ellipsize)
        ui_label_description.set_lines(5)

        # ADDING HEADER AND OTHER ELEMENTS TO CONTAINER
        ui_box_container.append(ui_box_header)
        ui_box_container.append(ui_label_description)
        ui_box_container.append(ui_image_extension_image)

        # RETURN CONTAINER
        return ui_box_container
        
    def fun_extension_toggle(self,switch,param,extension_id):
        if switch.get_active():
            status = "enable"
        else:
            status = "disable"
        extensionManager.extension_operations(status, extension_id)
    # INIT WALLPAPERS
    def init_wallpapers(self, wallpapers:str):
        for wallpaper in wallpapers:
            wallpaper_img = Gtk.Image.new_from_file(wallpaper)
            wallpaper_img.set_size_request(280, 280)
            self.ui_flowbox_wallpapers.insert(wallpaper_img,-1)
            #GLib.idle_add(self.ui_flowbox_wallpapers.insert, wallpaper_img, -1)

    # INIT LAYOUTS
    def init_layout(self):
        self.layout_buttons = {
            "layout_1": self.fun_get_ui("ui_button_layout_1"),
            "layout_2": self.fun_get_ui("ui_button_layout_2"),
            "layout_3": self.fun_get_ui("ui_button_layout_3"),
            "layout_4": self.fun_get_ui("ui_button_layout_4"),
        }
        self.layout_name = get_layout_name()
        for btn in self.layout_buttons:
            self.layout_buttons[btn].connect("clicked", self.fun_change_layout, btn)
        self.fun_check_layout_state()

    # INIT SCALE
    def init_scale(self):
        self.ui_scale_display = self.fun_get_ui("ui_scale_display")
        self.ui_label_recommended_scale = self.fun_get_ui("ui_label_recommended_scale")
        self.recommended_scale = get_recommended_scale()
        self.ui_label_recommended_scale.set_markup(
            "<b>Recommended scale option is %s%%</b>"%self.recommended_scale
            ) 

        self.current_scale = (float(scaleManager.get_scale()) / 0.25) - 4

        self.ui_scale_display.set_value(self.current_scale)
        self.ui_scale_display.connect("value-changed", self.fun_change_display_scale)
        self.ui_scale_display.add_mark(0, Gtk.PositionType.TOP, "100%")
        self.ui_scale_display.add_mark(1, Gtk.PositionType.TOP, "125%")
        self.ui_scale_display.add_mark(2, Gtk.PositionType.TOP, "150%")
        self.ui_scale_display.add_mark(3, Gtk.PositionType.TOP, "175%")
        self.ui_scale_display.add_mark(4, Gtk.PositionType.TOP, "200%")

    def init_about_dialog(self,action):
        self.ui_about_dialog = self.fun_get_ui("ui_about_dialog")
        self.ui_about_dialog.show()

    # INIT THEMES
    def init_themes(self):
        if get_current_theme() == "'prefer-dark'":
            self.ui_button_dark_theme.get_style_context().add_class("selected-theme")
            self.ui_button_light_theme.get_style_context().remove_class("selected-theme")
        else:
            self.ui_button_dark_theme.get_style_context().remove_class("selected-theme")
            self.ui_button_light_theme.get_style_context().add_class("selected-theme")


    # GETTING GTK OBJECTS WITH ID
    def fun_get_ui(self, ui_name: str):
        return self.gtk_builder.get_object(ui_name)

    
    # CHANGE SCALING OF DISPLAY
    def fun_change_display_scale(self, action):
        value = action.get_value()
        scale = float(1 + (0.25 * value))
        scaleManager.set_scale(scale)

    # CHANGE LAYOUT AND CHECK FOR LAYOUT STATE
    def fun_change_layout(self, action, layout_name):
        self.layout_name = layout_name
        LayoutManager.set_layout(self.layout_name)
        self.fun_check_layout_state()

    # CHECK LAYOUT STATE.
    def fun_check_layout_state(self):
        for btn in self.layout_buttons:
            if btn == self.layout_name:
                self.layout_buttons[btn].get_style_context().add_class("selected-layout")
            else:
                self.layout_buttons[btn].get_style_context().remove_class("selected-layout")


    # CHANGE THEME
    def fun_change_theme(self, action, theme):
        cmd = "dconf write /org/gnome/desktop/interface/color-scheme \"'prefer-%s'\""%theme
        if theme == "dark":
            self.ui_button_dark_theme.get_style_context().add_class("selected-theme")
            self.ui_button_light_theme.get_style_context().remove_class("selected-theme")

        else:
            self.ui_button_dark_theme.get_style_context().remove_class("selected-theme")
            self.ui_button_light_theme.get_style_context().add_class("selected-theme")

        return GLib.spawn_command_line_sync(cmd)

    # CHANGE WALLPAPERS
    def fun_change_wallpaper(self, flowbox, flowbox_child):
        wallpapers = wallpaper_manager.get_wallpapers()
        img_index = flowbox_child.get_index()
        wallpaper_manager.change_wallpaper(wallpapers[img_index])

    # CHANGE STACKED PAGES
    def fun_change_page(self, action, name):
        self.row_index = name.get_index()
        self.current_page = self.row_index
        self.ui_listbox_navigation.select_row(self.ui_listbox_sidemenu[self.current_page])
        self.ui_stack_pages.set_visible_child(self.ui_pages[self.current_page])
        self.fun_check_bottom_img_states()

    # CHECKING BOTTOM NAVIGATION INDICATORS
    def fun_check_bottom_img_states(self):
        for index, image in enumerate(self.ui_image_indicators):
            if index <= self.current_page:
                image.set_visible_child(self.ui_image_indicators[image]["on"])
            else:
                image.set_visible_child(self.ui_image_indicators[image]["off"])


    # PREVIOUS STACKED PAGE
    def on_prev_page_button_clicked(self, name): 
        if self.current_page > 0:
            self.current_page -= 1
            self.ui_stack_pages.set_visible_child(self.ui_pages[self.current_page])
            self.ui_listbox_navigation.select_row(self.ui_listbox_sidemenu[self.current_page])
            self.fun_check_bottom_img_states()

    # NEXT STACKED PAGE
    def on_next_page_button_clicked(self, name):
        if self.current_page < len(self.ui_image_indicators) - 1:
            self.current_page += 1
            self.ui_stack_pages.set_visible_child(self.ui_pages[self.current_page])
            self.ui_listbox_navigation.select_row(self.ui_listbox_sidemenu[self.current_page])
            self.fun_check_bottom_img_states()

