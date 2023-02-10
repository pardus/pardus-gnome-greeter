import gi
import os,threading
import subprocess
import time
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk,Gdk,Gio,GObject,GdkPixbuf,GLib
from WallpaperManager import WallpaperManager

wallpaper_manager = WallpaperManager()
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):

        # INITIALIZE
        super().__init__(*args, **kwargs)

        # IMPORT CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.dirname(os.path.abspath(__file__))+"/../test/test.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # GETTING UI FROM UI FILE
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/ui.ui")

        # MAIN WINDOW OF APPLICATION
        self.main_window = self.builder.get_object("window")
        self.init_ui()
        
        self.wallpapers = wallpaper_manager.get_wallpapers()
        thread = threading.Thread(target=self.init_wallpapers,args=(wallpaper_manager.get_wallpapers(),))
        thread.daemon = True
        thread.start()
     
        



    def init_ui(self):
           # CURRENT PAGE INDEX
        self.current_page = 0
          # LISTBOX NAVIGATION
        self.lb_navigation = self.get_ui("lb_navigation")
        self.lb_navigation.set_show_separators(True)
        self.lb_navigation.connect("row_activated",self.change_page)
        

        

        # stack_pagesED PAGES
        self.stack_pages = self.get_ui("gs_pages")
             

        # RIGHT SIDE OF APPLICATION
        self.bx_content = self.get_ui("bx_content")
        self.bx_content.prepend(self.stack_pages)

        self.flow_wallpapers = self.get_ui("flow_wallpapers")
        self.flow_wallpapers.connect("child-activated",self.change_wallpaper)
        #self.flow_wallpapers.connect("item-activated",self.change_wallpaper)

        


        self.scrolled_window = self.get_ui("gsw_wallpaper")
        
   
        self.left_rows=[
            self.get_ui("lbr_welcome"),
            self.get_ui("lbr_wallpaper"),
            self.get_ui("lbr_theme"),
            self.get_ui("lbr_display"),
            self.get_ui("lbr_shortcut")
        ]

        self.pages = [
            self.get_ui("gb_welcome"),            
            self.get_ui("gb_wallpaper"),        
            self.get_ui("gb_theme"),        
            self.get_ui("gb_display"),        
            self.get_ui("gb_shortcut"),            
        ]

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
        }
       

        self.page1_pardus_label = self.get_ui("page1_pardus23_label")
        self.page1_pardus_label_content = self.page1_pardus_label.get_label()
        self.page1_pardus_label.set_markup("<span size=\"36000\">%s</span>"%self.page1_pardus_label_content)


            
        # BOTTOM PREV NEXT BUTTONS
        self.prev_page_btn = self.get_ui("prev_page")
        self.prev_page_btn.connect("clicked",self.prev_page)
        
        self.next_page_btn = self.get_ui("next_page")
        self.next_page_btn.connect("clicked",self.next_page)
        self.check_bottom_img_states()
        
 

    def get_ui(self,ui_name:str):
        return self.builder.get_object(ui_name)

    def init_wallpapers(self,wallpapers):
        

        for wallpaper in wallpapers:
            wallpaper_img = Gtk.Image.new_from_file(wallpaper)
            wallpaper_img.set_size_request(280,280)
            GLib.idle_add(self.flow_wallpapers.insert, wallpaper_img, -1)
            

    def change_wallpaper(self,flowbox,flowbox_child):
        img_index = flowbox_child.get_index()
        wallpaper_manager.change_wallpaper(self.wallpapers[img_index])

    def change_page(self,action,name):
        self.row_index = name.get_index()
        self.current_page = self.row_index
        self.lb_navigation.select_row(self.left_rows[self.current_page])
        self.stack_pages.set_visible_child(self.pages[self.current_page])
        self.check_bottom_img_states()

    def prev_page(self,name):
        if(self.current_page > 0):
            self.current_page -= 1
            self.stack_pages.set_visible_child(self.pages[self.current_page])
            self.lb_navigation.select_row(self.left_rows[self.current_page])
            self.check_bottom_img_states()
            
    def next_page(self,name):
        if self.current_page < 4:
            self.current_page += 1
            self.stack_pages.set_visible_child(self.pages[self.current_page])
            self.lb_navigation.select_row(self.left_rows[self.current_page])
            self.check_bottom_img_states()

    
    def check_bottom_img_states(self):
        for index,image in enumerate(self.nav_images):
            if index <= self.current_page:
                image.set_visible_child(self.nav_images[image]["on"])
            else:
                image.set_visible_child(self.nav_images[image]["off"])
                
