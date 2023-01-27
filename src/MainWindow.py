import gi
import os
import subprocess

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk,Gdk,Gio

from LayoutChanger import LayoutChanger

layoutChanger = LayoutChanger()


class MainWindow():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.dirname(os.path.abspath(__file__))+"/../css/style.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.main_window = None
        self.initialize_gui()
        

    def initialize_gui(self):
        self.main_window = Gtk.ApplicationWindow()
        self.main_window.set_title("Pardus Gnome Greeter")
        self.layout_name = self.get_layout_name().split("'")[1]
        grid  = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        for i in range(2):
            grid.insert_column(i)
            grid.insert_row(i)   

        label = Gtk.Label()
        label.set_markup("Select Layout")
        grid.attach(label,0,0,2,1)
       
        button_configs = {
            "set_1":{
                "filename":"set1.svg",
                "position":[0,1,1,1]
            },
            "set_2":{
                "filename":"set2.svg",
                "position":[1,1,1,1]
            },
            "set_3":{
                "filename":"set3.svg",
                "position":[0,2,1,1]
            },
            "set_4":{
                "filename":"set4.svg",
                "position":[1,2,1,1]
            }
        }
        self.buttons = []           

        for btn in button_configs:
            new_btn = self.create_button_with_image(self.assets_file(button_configs[btn]["filename"]),btn,self.set_layout)
            self.buttons.append(new_btn)
            grid.attach(new_btn, 
                button_configs[btn]["position"][0],
                button_configs[btn]["position"][1],
                button_configs[btn]["position"][2],
                button_configs[btn]["position"][3])
        self.main_window.set_child(grid)     

    def set_layout(self,action):
        layout_name = action.get_name()
        layoutChanger.set_layout(layout_name)
        for btn in self.buttons:
            if btn.get_name()==layout_name:
               btn.get_style_context().add_class("btn-active")
            else:
               btn.get_style_context().remove_class("btn-active") 
        
    def assets_file(self,file):
        return os.path.dirname(os.path.abspath(__file__)) +"/../assets/" +file

    def create_button_with_image(self,img_path:str,name:str,function):
        btn = Gtk.Button()
        img = Gtk.Image()
        img.set_from_file(img_path)
        img.set_size_request(200,200)
        btn.set_child(img)
        btn.connect("clicked",function)
        if self.layout_name in name:
            btn.get_style_context().add_class("btn-active")
        btn.set_name(name)
        return btn
    def get_layout_name(self):
        cmd = "gsettings get org.pardus.pardus-gnome-greeter layout-name"
        return subprocess.getoutput(cmd)