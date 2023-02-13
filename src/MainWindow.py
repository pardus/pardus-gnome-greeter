import gi
import os,threading
import subprocess
import time
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk,Gdk,Gio,GObject,GdkPixbuf,GLib
from WallpaperManager import WallpaperManager
from LayoutChanger import LayoutChanger


wallpaper_manager = WallpaperManager()
layoutChanger = LayoutChanger()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):

        # INITIALIZE
        super().__init__(*args, **kwargs)

        # IMPORT CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.dirname(os.path.abspath(__file__))+"/../css/style.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # GETTING UI FROM UI FILE
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../ui/ui.ui")

        # MAIN WINDOW OF APPLICATION
        self.main_window = self.builder.get_object("window")
        
        self.init_ui()
        self.init_layout()
        self.init_themes()
     
        



    def init_ui(self):

################################# MAIN DEFINITIONS ################

        # CURRENT ACTIVE STACK PAGE INDEX
        self.current_page = 0

        self.lb_navigation = self.get_ui("lb_navigation")
        self.lb_navigation.set_show_separators(True)
        self.lb_navigation.connect("row_activated",self.change_page)

        self.stack_pages = self.get_ui("gs_pages")
        # RIGHT SIDE OF APPLICATION
        self.bx_content = self.get_ui("bx_content")
        self.bx_content.prepend(self.stack_pages)

        # LISTBOXROWS
        self.left_rows=[
            self.get_ui("lbr_welcome"),
            self.get_ui("lbr_layout"),
            self.get_ui("lbr_wallpaper"),
            self.get_ui("lbr_theme"),
            self.get_ui("lbr_display"),
            self.get_ui("lbr_shortcut")
        ]

        # STACK PAGES
        self.pages = [
            self.get_ui("gb_welcome"),
            self.get_ui("gb_layout"),            
            self.get_ui("gb_wallpaper"),        
            self.get_ui("gb_theme"),        
            self.get_ui("gb_display"),        
            self.get_ui("gb_shortcut"),            
        ]

        # BOTTOM NAVIGATION INDICATORS
        self.nav_images = {
            self.get_ui("gs_nav_img_0"):{
                "on": self.get_ui("gi_nav_img_on_0"),
                "off": self.get_ui("gi_nav_img_off_0"),
            },
            self.get_ui("gs_nav_img_1"):{
                "on": self.get_ui("gi_nav_img_on_1"),
                "off": self.get_ui("gi_nav_img_off_1"),
            },
            self.get_ui("gs_nav_img_2"):{
                "on": self.get_ui("gi_nav_img_on_2"),
                "off": self.get_ui("gi_nav_img_off_2"),
            },
            self.get_ui("gs_nav_img_3"):{
                "on": self.get_ui("gi_nav_img_on_3"),
                "off": self.get_ui("gi_nav_img_off_3"),
            },
            self.get_ui("gs_nav_img_4"):{
                "on": self.get_ui("gi_nav_img_on_4"),
                "off": self.get_ui("gi_nav_img_off_4"),
            },
            self.get_ui("gs_nav_img_5"):{
                "on": self.get_ui("gi_nav_img_on_5"),
                "off": self.get_ui("gi_nav_img_off_5"),
            },
        }
        
        # CHECKING BOTTOM IMAGES WITH CURRENT PAGE INDEX
        self.check_bottom_img_states()

        # BOTTOM PREV NEXT BUTTONS
        self.prev_page_btn = self.get_ui("prev_page")
        self.prev_page_btn.connect("clicked",self.prev_page)
        
        self.next_page_btn = self.get_ui("next_page")
        self.next_page_btn.connect("clicked",self.next_page)




################################# WELCOME UI INITIALITIONS ########

        # SETTING SIZE ON LABEL ON WELCOME PAGE
        self.page1_pardus_label = self.get_ui("page1_pardus23_label")
        self.page1_pardus_label_content = self.page1_pardus_label.get_label()
        self.page1_pardus_label.set_markup("<span size=\"36000\">%s</span>"%self.page1_pardus_label_content)

################################# LAYOUT UI INITIALITIONS ########

        self.layout_buttons = {
            "layout_1":self.get_ui("btn_layout_1"),
            "layout_2":self.get_ui("btn_layout_2"),
            "layout_3":self.get_ui("btn_layout_3"),
            "layout_4":self.get_ui("btn_layout_4"),
        }
        
        print(self.layout_buttons)        


################################# WALLPAPER UI INITIALITIONS ######

        # FLOWBOX WITH FLOWED ITEMS
        self.flow_wallpapers = self.get_ui("flow_wallpapers")
        self.flow_wallpapers.connect("child-activated",self.change_wallpaper)

        # THREADING ADDING IMAGES TO FLOWBOX
        thread = threading.Thread(target=self.init_wallpapers,args=(wallpaper_manager.get_wallpapers(),))
        thread.daemon = True
        thread.start()

################################# THEME UI INITIALITIONS ###########

        # CURRENT THEME
        self.current_theme = subprocess.getoutput("dconf read /org/gnome/desktop/interface/color-scheme")

        # BUTTONS ON THEME PAGE
        self.btn_dark_theme = self.get_ui("btn_dark_theme")
        self.btn_dark_theme.connect("clicked",self.change_theme,"dark")

        self.btn_light_theme = self.get_ui("btn_light_theme")
        self.btn_light_theme.connect("clicked",self.change_theme,"light")


################################# DISPLAY UI INITIALITIONS #########

################################# SHORTCUTS UI INITIALITIONS #######

        


#------------------------------------- FUNCTIONS ------------------#

    # GETTING GTK OBJECTS WITH ID
    def get_ui(self,ui_name:str):
        return self.builder.get_object(ui_name)


    # INIT WALLPAPERS
    def init_wallpapers(self,wallpapers):
        for wallpaper in wallpapers:
            wallpaper_img = Gtk.Image.new_from_file(wallpaper)
            wallpaper_img.set_size_request(280,280)
            GLib.idle_add(self.flow_wallpapers.insert, wallpaper_img, -1)


    # INIT LAYOUTS

    def init_layout(self):
        for btn in self.layout_buttons:
            print("buttons",btn)
            self.layout_buttons[btn].connect("clicked",layoutChanger.set_layout,btn)


    # INIT THEMES
    def init_themes(self):
        if(self.current_theme=="'prefer-dark'"):
            self.add_css_class(self.btn_dark_theme,"selected-theme")
            self.remove_css_class(self.btn_light_theme,"selected-theme")
        else:
            self.add_css_class(self.btn_light_theme,"selected-theme")
            self.remove_css_class(self.btn_dark_theme,"selected-theme")

    # ADDING CSS TO A GTK WIDGET
    def add_css_class(self,widget,css_class):
        widget.get_style_context().add_class(css_class)

    # REMOVE CSS FROM GTK WIDGET
    def remove_css_class(self,widget,css_class):
        widget.get_style_context().remove_class(css_class)

    # CHANGE THEME
    def change_theme(self,action,theme):
        cmd = "dconf write /org/gnome/desktop/interface/color-scheme \"'prefer-%s'\""%theme
        if(theme=="dark"):
            self.add_css_class(self.btn_dark_theme,"selected-theme")
            self.remove_css_class(self.btn_light_theme,"selected-theme")
        else:
            self.add_css_class(self.btn_light_theme,"selected-theme")
            self.remove_css_class(self.btn_dark_theme,"selected-theme")
        return GLib.spawn_command_line_sync(cmd)


    # CHANGE WALLPAPERS
    def change_wallpaper(self,flowbox,flowbox_child):
        wallpapers = wallpaper_manager.get_wallpapers()
        img_index = flowbox_child.get_index()
        wallpaper_manager.change_wallpaper(wallpapers[img_index])


    # CHANGE STACKED PAGES
    def change_page(self,action,name):
        self.row_index = name.get_index()
        self.current_page = self.row_index
        self.lb_navigation.select_row(self.left_rows[self.current_page])
        self.stack_pages.set_visible_child(self.pages[self.current_page])
        self.check_bottom_img_states()

    # PREVIOUS STACKED PAGE
    def prev_page(self,name):
        if(self.current_page > 0):
            self.current_page -= 1
            self.stack_pages.set_visible_child(self.pages[self.current_page])
            self.lb_navigation.select_row(self.left_rows[self.current_page])
            self.check_bottom_img_states()
    
    # NEXT STACKED PAGE
    def next_page(self,name):
        if self.current_page < 4:
            self.current_page += 1
            self.stack_pages.set_visible_child(self.pages[self.current_page])
            self.lb_navigation.select_row(self.left_rows[self.current_page])
            self.check_bottom_img_states()

    # CHECKING BOTTOM NAVIGATION INDICATORS
    def check_bottom_img_states(self):
        for index,image in enumerate(self.nav_images):
            if index <= self.current_page:
                image.set_visible_child(self.nav_images[image]["on"])
            else:
                image.set_visible_child(self.nav_images[image]["off"])
                
