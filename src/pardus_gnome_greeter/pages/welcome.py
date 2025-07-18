import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/WelcomePage.ui')
class WelcomePage(Gtk.Box):
    __gtype_name__ = 'WelcomePage'

    # This will be connected to the widget with the "welcome_label" id in the .ui file
    welcome_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # We can change the text of this label from code, but the main text will be in the .ui file.
        print("WelcomePage created.") 