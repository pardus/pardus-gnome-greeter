import gi
import os
import subprocess

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk,Gdk

from LayoutChanger import LayoutChanger

layoutChanger = LayoutChanger()

class MainWindow():
    def __init__(self,application):

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_path(os.path.dirname(os.path.abspath(__file__))+"/../css/style.css")
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # GLADE
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../ui/ui2.glade")
        self.builder.connect_signals(self)

        layout_name = self.get_layout_name().split("'")[1]

        # BUTTONS
        buttons = {
            "set_1":self.builder.get_object("set_1"),
            "set_2":self.builder.get_object("set_2"),
            "set_3":self.builder.get_object("set_3"),
            "set_4":self.builder.get_object("set_4"),
        }

        for button in buttons:
            buttons[button].connect("clicked",self.apply_layout,buttons,button)
            if button == layout_name:
                buttons[button].get_style_context().add_class("btn-active")


        # WINDOW
        self.window = self.builder.get_object("window")
        self.window.set_application(application)
        self.window.connect("destroy",self.quit_window)
        self.window.show_all()

    def apply_layout(self,action,button_group,button):
        layoutChanger.set_layout(button)
        for btn in button_group:
            if btn==button:
                button_group[btn].get_style_context().add_class("btn-active")
            else:
                button_group[btn].get_style_context().remove_class("btn-active")   
        
    def get_layout_name(self):
        cmd = "gsettings get org.pardus.pardus-gnome-greeter layout-name"
        return subprocess.getoutput(cmd)
    
    def quit_window(self,action):
        self.window.get_application().quit()