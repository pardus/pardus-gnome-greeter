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

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/OutroPage.ui')
class OutroPage(Adw.PreferencesPage):
    __gtype_name__ = 'OutroPage'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("OutroPage created.") 