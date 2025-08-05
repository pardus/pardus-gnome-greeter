import locale
import gi
import subprocess
from locale import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

# Gettext setup
domain = 'pardus-gnome-greeter'
locale.bindtextdomain(domain, '/usr/share/locale')
locale.textdomain(domain)

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/ApplicationsPage.ui')
class ApplicationsPage(Adw.PreferencesPage):
    __gtype_name__ = 'ApplicationsPage'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("ApplicationsPage created.")
    
    @Gtk.Template.Callback()
    def on_open_store_clicked(self, button):
        """Open Pardus Software Center"""
        try:
            subprocess.Popen(["pardus-software"])
        except FileNotFoundError:
            print("Pardus Software Center not found")
        except Exception as e:
            print(f"Error opening Pardus Software Center: {e}") 