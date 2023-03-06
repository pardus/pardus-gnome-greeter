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
            os.path.dirname(os.path.abspath(__file__)) + "/../data/style.css"
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
        self.main_window = self.fun_get_ui("ui_window")

        # CURRENT ACTIVE STACK PAGE INDEX
        self.current_page = 0

        # LEFT SIDE NAVIGATION
        self.ui_navigation_listbox = self.fun_get_ui("ui_navigation_listbox")
        self.ui_navigation_listbox.set_show_separators(True)
        self.ui_navigation_listbox.connect("row_activated", self.fun_change_page)

        # STACK PAGES CONTAINER
        self.ui_pages_stack = self.fun_get_ui("ui_pages_stack")

        # RIGHT SIDE OF APPLICATION
        self.ui_content_box = self.fun_get_ui("ui_content_box")
        self.ui_content_box.prepend(self.ui_pages_stack)
        
        # LISTBOXROWS
        self.ui_sidemenu_listbox = [
            self.fun_get_ui("ui_welcome_listboxrow"),
            self.fun_get_ui("ui_layout_listboxrow"),
            self.fun_get_ui("ui_wallpaper_listboxrow"),
            self.fun_get_ui("ui_theme_listboxrow"),
            self.fun_get_ui("ui_display_listboxrow"),
            self.fun_get_ui("ui_extensions_listboxrow"),
            self.fun_get_ui("ui_outro_listboxrow"),

        ]

        # STACK PAGES
        self.ui_pages = [
            self.fun_get_ui("ui_welcome_box"),
            self.fun_get_ui("ui_layout_box"),
            self.fun_get_ui("ui_wallpaper_box"),
            self.fun_get_ui("ui_theme_box"),
            self.fun_get_ui("ui_display_box"),
            self.fun_get_ui("ui_extensions_box"),
            self.fun_get_ui("ui_outro_box"),

        ]

        # BOTTOM NAVIGATION INDICATORS
        self.ui_indicators_image = {
            self.fun_get_ui("ui_indicator_stack_0"): {
                "on": self.fun_get_ui("ui_indicator_on_image_0"),
                "off": self.fun_get_ui("ui_indicator_off_image_0"),
            },
            self.fun_get_ui("ui_indicator_stack_1"): {
                "on": self.fun_get_ui("ui_indicator_on_image_1"),
                "off": self.fun_get_ui("ui_indicator_off_image_1"),
            },
            self.fun_get_ui("ui_indicator_stack_2"): {
                "on": self.fun_get_ui("ui_indicator_on_image_2"),
                "off": self.fun_get_ui("ui_indicator_off_image_2"),
            },
            self.fun_get_ui("ui_indicator_stack_3"): {
                "on": self.fun_get_ui("ui_indicator_on_image_3"),
                "off": self.fun_get_ui("ui_indicator_off_image_3"),
            },
            self.fun_get_ui("ui_indicator_stack_4"): {
                "on": self.fun_get_ui("ui_indicator_on_image_4"),
                "off": self.fun_get_ui("ui_indicator_off_image_4"),
            },
            self.fun_get_ui("ui_indicator_stack_5"): {
                "on": self.fun_get_ui("ui_indicator_on_image_5"),
                "off": self.fun_get_ui("ui_indicator_off_image_5"),
            },
            self.fun_get_ui("ui_indicator_stack_6"): {
                "on": self.fun_get_ui("ui_indicator_on_image_6"),
                "off": self.fun_get_ui("ui_indicator_off_image_6"),
            },
        }


        # PREVIOUS PAGE BUTTON

        self.ui_previous_page_button = self.fun_get_ui("ui_previous_page_button")
        self.ui_previous_page_button.connect("clicked", self.on_prev_page_button_clicked)

        # NEXT PAGE BUTTON
        self.ui_next_page_button= self.fun_get_ui("ui_next_page_button")
        self.ui_next_page_button.connect("clicked", self.on_next_page_button_clicked)


        # FLOWBOX WITH FLOWED ITEMS
        self.ui_wallpapers_flowbox = self.fun_get_ui("ui_wallpapers_flowbox")
        self.ui_wallpapers_flowbox.connect("child-activated", self.fun_change_wallpaper) 


        # BUTTONS ON THEME PAGE
        # DARK THEME BUTTON ON THEME PAGE    
        self.ui_dark_theme_button = self.fun_get_ui("ui_dark_theme_button")
        self.ui_dark_theme_button.connect("clicked", self.fun_change_theme, "dark")

        # LIGHT THEME BUTTON ON THEME PAGE
        self.ui_light_theme_button = self.fun_get_ui("ui_light_theme_button")
        self.ui_light_theme_button.connect("clicked", self.fun_change_theme, "light")
        
        # ABOUT DIALOG AND BUTTON
        self.ui_about_dialog_button = self.fun_get_ui("ui_about_dialog_button")
        self.ui_about_dialog_button.connect("clicked",self.init_about_dialog)
        
        thread = threading.Thread(
            target=self.init_wallpapers, args=(wallpaper_manager.get_wallpapers(),)
        )
        thread.daemon = True
        thread.start()

        self.fun_check_bottom_img_states()

        

        self.enabled_extensions = extensionManager.get_extensions("enabled")
        self.ui_extensions_flowbox = self.fun_get_ui("ui_extensions_flowbox")

        with open("../data/extensions.json") as file_content:
            self.extension_datas = json.loads(file_content.read())

        

        for item in self.extension_datas:
            extension = self.fun_create_extension_box(item)
            self.ui_extensions_flowbox.insert(extension,-1)
        

        self.toggle_buttons = []


       
        # INIT FUNCTIONS
        self.init_layout()
        self.init_scale()
        self.init_themes()



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
        

    # INIT WALLPAPERS
    def init_wallpapers(self, wallpapers:str):
        for wallpaper in wallpapers:
            wallpaper_img = Gtk.Image.new_from_file(wallpaper)
            wallpaper_img.set_size_request(280, 280)
            self.ui_wallpapers_flowbox.insert(wallpaper_img,-1)
            #GLib.idle_add(self.ui_wallpapers_flowbox.insert, wallpaper_img, -1)

    # INIT LAYOUTS
    def init_layout(self):
        self.layout_buttons = {
            "layout_1": self.fun_get_ui("ui_layout_1_button"),
            "layout_2": self.fun_get_ui("ui_layout_2_button"),
            "layout_3": self.fun_get_ui("ui_layout_3_button"),
            "layout_4": self.fun_get_ui("ui_layout_4_button"),
        }
        self.layout_name = get_layout_name()
        for btn in self.layout_buttons:
            self.layout_buttons[btn].connect("clicked", self.fun_change_layout, btn)
        self.fun_check_layout_state()

    # INIT SCALE
    def init_scale(self):
        self.ui_display_scale = self.fun_get_ui("ui_display_scale")
        self.ui_recommended_scale_label = self.fun_get_ui("ui_recommended_scale_label")
        self.recommended_scale = get_recommended_scale()
        self.ui_recommended_scale_label.set_markup(
            "<b>Recommended scale option is %s%%</b>"%self.recommended_scale
            ) 

        self.current_scale = (float(scaleManager.get_scale()) / 0.25) - 4

        self.ui_display_scale.set_value(self.current_scale)
        self.ui_display_scale.connect("value-changed", self.fun_change_display_scale)
        self.ui_display_scale.add_mark(0, Gtk.PositionType.TOP, "100%")
        self.ui_display_scale.add_mark(1, Gtk.PositionType.TOP, "125%")
        self.ui_display_scale.add_mark(2, Gtk.PositionType.TOP, "150%")
        self.ui_display_scale.add_mark(3, Gtk.PositionType.TOP, "175%")
        self.ui_display_scale.add_mark(4, Gtk.PositionType.TOP, "200%")

    def init_about_dialog(self,action):
        self.ui_about_dialog = self.fun_get_ui("ui_about_dialog")
        self.ui_about_dialog.show()

    # INIT THEMES
    def init_themes(self):
        if get_current_theme() == "'prefer-dark'":
            self.ui_dark_theme_button.get_style_context().add_class("selected-theme")
            self.ui_light_theme_button.get_style_context().remove_class("selected-theme")
        else:
            self.ui_dark_theme_button.get_style_context().remove_class("selected-theme")
            self.ui_light_theme_button.get_style_context().add_class("selected-theme")


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
            self.ui_dark_theme_button.get_style_context().add_class("selected-theme")
            self.ui_light_theme_button.get_style_context().remove_class("selected-theme")

        else:
            self.ui_dark_theme_button.get_style_context().remove_class("selected-theme")
            self.ui_light_theme_button.get_style_context().add_class("selected-theme")

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
        self.ui_navigation_listbox.select_row(self.ui_sidemenu_listbox[self.current_page])
        self.ui_pages_stack.set_visible_child(self.ui_pages[self.current_page])
        self.fun_check_bottom_img_states()

    # CHECKING BOTTOM NAVIGATION INDICATORS
    def fun_check_bottom_img_states(self):
        for index, image in enumerate(self.ui_indicators_image):
            if index <= self.current_page:
                image.set_visible_child(self.ui_indicators_image[image]["on"])
            else:
                image.set_visible_child(self.ui_indicators_image[image]["off"])

    def fun_extension_toggle(self,switch,param,extension_id):
        if switch.get_active():
            status = "enable"
        else:
            status = "disable"
        extensionManager.extension_operations(status, extension_id)

    # PREVIOUS STACKED PAGE
    def on_prev_page_button_clicked(self, name): 
        if self.current_page > 0:
            self.current_page -= 1
            self.ui_pages_stack.set_visible_child(self.ui_pages[self.current_page])
            self.ui_navigation_listbox.select_row(self.ui_sidemenu_listbox[self.current_page])
            self.fun_check_bottom_img_states()

    # NEXT STACKED PAGE
    def on_next_page_button_clicked(self, name):
        if self.current_page < len(self.ui_indicators_image) - 1:
            self.current_page += 1
            self.ui_pages_stack.set_visible_child(self.ui_pages[self.current_page])
            self.ui_navigation_listbox.select_row(self.ui_sidemenu_listbox[self.current_page])
            self.fun_check_bottom_img_states()

