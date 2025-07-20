import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/ThemePage.ui')
class ThemePage(Adw.PreferencesPage):
    __gtype_name__ = 'ThemePage'

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 