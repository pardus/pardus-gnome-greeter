import gi
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from LayoutChanger import LayoutChanger
layoutChanger = LayoutChanger()

class MainWindow():
    def __init__(self,application):

        # GLADE
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../ui/ui.glade")
        self.builder.connect_signals(self)

        # RADIO BUTTONS
        radio_buttons = {
            "set_1":self.builder.get_object("set_1"),
            "set_2":self.builder.get_object("set_2"),
            "set_3":self.builder.get_object("set_3"),
            "set_4":self.builder.get_object("set_4"),
        }

        for radio in radio_buttons:
            radio_buttons[radio].connect("toggled",self.apply_layout,radio)

        # WINDOW
        self.window = self.builder.get_object("window")
        self.window.set_application(application)
        self.window.connect("destroy",self.quit_window)
        self.window.show_all()

    def apply_layout(self,action,name):
        layoutChanger.set_layout(name)

    def quit_window(self,action):
        self.window.get_application().quit()
    