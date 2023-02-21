import gi
import os, threading
import subprocess
import time

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf, GLib


from WallpaperManager import WallpaperManager
from LayoutManager import LayoutManager
from ScaleManager import ScaleManager
from utils import get_current_theme,get_layout_name

wallpaper_manager = WallpaperManager()
LayoutManager = LayoutManager()
scaleManager = ScaleManager()


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

        # NIGHT LIGHT BUTTONS
        #self.ui_button_night_light_on = self.fun_get_ui("ui_button_night_light_on")
        #self.ui_button_night_light_on.connect("clicked",self.fun_toggle_night_light,True)
        #self.ui_button_night_light_off = self.fun_get_ui("ui_button_night_light_off")
        #self.ui_button_night_light_off.connect("clicked",self.fun_toggle_night_light,False)

        

        thread = threading.Thread(
            target=self.init_wallpapers, args=(wallpaper_manager.get_wallpapers(),)
        )
        thread.daemon = True
        thread.start()

        self.fun_check_bottom_img_states()

        # INIT FUNCTIONS
        self.init_layout()
        self.init_scale()
        # self.init_night_light()
        self.init_themes()

        self.ui_flowbox_extensions = self.fun_get_ui("ui_flowbox_extensions")
        self.ui_flowbox_extensions.insert(self.fun_box(),-1)
      
        

        

#    def init_night_light(self):
#        self.get_night_light_state_cmd = "gsettings get org.gnome.settings-daemon.plugins.color night-light-enabled"
#        self.night_light_status = subprocess.getoutput(self.get_night_light_state_cmd) == "true"
#
#        if self.night_light_status:
#            self.ui_button_night_light_on.set_sensitive(False)
#            self.ui_button_night_light_off.set_sensitive(True)
#        else:
#            self.ui_button_night_light_on.set_sensitive(True)
#            self.ui_button_night_light_off.set_sensitive(False)

    

    def fun_box(self):
        horizontal = Gtk.Orientation.HORIZONTAL
        container = Gtk.Box.new(horizontal,13)
        container.set_size_request(180,250)
        container.get_style_context().add_class("bordered-box")
        container.set_valign(Gtk.Align(1))
        container.set_halign(Gtk.Align(1))


        header = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,5)
        container.append(header)
        for i in range(10):

            logo = Gtk.Image.new_from_file("../assets/ext1_logo.png")

            header.append(logo)
        
        return container
        

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
        print(self.layout_name)
        for btn in self.layout_buttons:
            self.layout_buttons[btn].connect("clicked", self.fun_change_layout, btn)
        self.fun_check_layout_state()

    # INIT SCALE
    def init_scale(self):
        self.ui_scale_display = self.fun_get_ui("ui_scale_display")
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

#    def fun_toggle_night_light(self,action,param):
#        self.night_light_status = param
#        set_night_light_state_cmd = "gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled"
#        cmd = set_night_light_state_cmd
#        if param:
#            self.ui_button_night_light_on.set_sensitive(False)
#            self.ui_button_night_light_off.set_sensitive(True)
#            cmd += " true"
#        else:
#            self.ui_button_night_light_on.set_sensitive(True)
#            self.ui_button_night_light_off.set_sensitive(False)
#            cmd +=  " false"
#        subprocess.getoutput(cmd)



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
        LayoutManager.set_layout(layout_name=self.layout_name)
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

