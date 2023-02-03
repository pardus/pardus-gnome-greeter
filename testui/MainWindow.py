import gi
import os
import subprocess
import time
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk,Gdk,Gio,GObject


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.dirname(os.path.abspath(__file__))+"/../test/test.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/ui.ui")
        self.main_window = self.builder.get_object("window")

        self.listbox = self.get_ui("listbox")
        self.listbox.set_show_separators(True)
        self.listbox.connect("row_activated",self.on_click)
        self.welcome1 = self.get_ui("row1")
        
        # RIGHT SIDE OF THE WINDOW
        self.right_window = self.get_ui("right_window")
        
        # CURRENT PAGE INDEX
        self.current_page = 0
        

        # STACKED PAGES FOR NEXT NEXT INSTALL LOGIC
        self.stack = self.get_ui("pages")

        

        # PAGE ARRAY
        self.pages = [
            self.get_ui("page1"),
            self.get_ui("page2"),
            self.get_ui("page3"),
            self.get_ui("page4"),
            self.get_ui("page5"),
        ]

        # BOTTOM NAVIGATION BUTTONS
        self.nav_buttons = {
            self.get_ui("nav_btn_1"):{
                "on":self.get_ui("nav_img_on_1"),
                "off":self.get_ui("nav_img_off_1"),
            },
            self.get_ui("nav_btn_2"):{
                "on":self.get_ui("nav_img_on_2"),
                "off":self.get_ui("nav_img_off_2"),
            },
            self.get_ui("nav_btn_3"):{
                "on":self.get_ui("nav_img_on_3"),
                "off":self.get_ui("nav_img_off_3"),
            },
            self.get_ui("nav_btn_4"):{
                "on":self.get_ui("nav_img_on_4"),
                "off":self.get_ui("nav_img_off_4"),
            },
            self.get_ui("nav_btn_5"):{
                "on":self.get_ui("nav_img_on_5"),
                "off":self.get_ui("nav_img_off_5"),
            },
        }



        # LEFT NAVIGATIONS
        self.left_rows=[
            self.get_ui("row1"),
            self.get_ui("row2"),
            self.get_ui("row3"),
            self.get_ui("row4"),
            self.get_ui("row5"),
        ]
        # BOTTOM PREV NEXT BUTTONS
        self.prev_page_btn = self.get_ui("prev_page")
        self.prev_page_btn.connect("clicked",self.prev_page)
        
        self.next_page_btn = self.get_ui("next_page")
        self.next_page_btn.connect("clicked",self.next_page)
        self.right_window.prepend(self.stack)

        self.check_states()

    def check_states(self):
        self.left_rows[self.current_page].activate()
        for nav_index,nav in enumerate(self.nav_buttons):
            print(self.nav_buttons[nav])
            if(nav_index <= self.current_page):
                on_img = self.nav_buttons[nav]["on"]
                nav.set_visible_child(on_img)
            else:
                off_img = self.nav_buttons[nav]["off"]
                nav.set_visible_child(off_img)

    def prev_page(self,name):
        if(self.current_page > 0):
            self.current_page -= 1
            self.stack.set_visible_child(self.pages[self.current_page])
            self.check_states()
        else:
            print("daha geri gidemezsin",self.current_page)
    def next_page(self,name):
        if(self.current_page < 4):
            self.current_page += 1
            self.stack.set_visible_child(self.pages[self.current_page])
            self.check_states()

        else:
            print("daha ileri gidemezsin",self.current_page)


    def change_page(self):   
        self.stack.set_visible_child(self.pages[self.current_page])

    def get_ui(self,ui_name:str):
        return self.builder.get_object(ui_name)

    def on_click(self,action,name):
        self.row_index = name.get_index()
        self.listbox.select_row(self.left_rows[self.row_index])
        self.current_page = self.row_index
        self.change_page()
        self.check_states()
  