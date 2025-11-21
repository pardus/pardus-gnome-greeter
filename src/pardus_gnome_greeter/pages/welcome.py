import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/WelcomePage.ui')
class WelcomePage(Adw.PreferencesPage):
    __gtype_name__ = 'WelcomePage'
    
    welcome_banner = Gtk.Template.Child("welcome_banner")
    welcome_title = Gtk.Template.Child("welcome_title")
    welcome_message = Gtk.Template.Child("welcome_message")
    start_button = Gtk.Template.Child("start_button")

    __gsignals__ = {
        'navigate-to': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.welcome_banner.set_resource("/tr/org/pardus/pardus-gnome-greeter/assets/banner.png")
        self.welcome_title.set_label(_("Welcome to Pardus GNOME!"))
        self.welcome_message.set_label(_("You can easily configure your system with the Greeter application."))
        self.start_button.connect("clicked", self.on_start_button_clicked)

    def on_start_button_clicked(self, button):
        self.emit('navigate-to', 'layout') 