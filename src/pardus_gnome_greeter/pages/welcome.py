import locale
import gi
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/WelcomePage.ui')
class WelcomePage(Adw.PreferencesPage):
    __gtype_name__ = 'WelcomePage'
    
    welcome_message = Gtk.Template.Child("welcome_message")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_translations()
    
    def _setup_translations(self):
        """Çeviri metinlerini ayarla"""
        self.welcome_message.set_label(_("Welcome to Pardus GNOME Greeter! This application will help you configure your Pardus GNOME experience.")) 