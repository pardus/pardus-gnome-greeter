import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

# This class is empty for now, it will be added logic for layout in the future.
@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/LayoutPage.ui')
class LayoutPage(Adw.PreferencesPage):
    __gtype_name__ = 'LayoutPage'

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 