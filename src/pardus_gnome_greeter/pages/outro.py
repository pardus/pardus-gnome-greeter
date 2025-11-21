import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

@Gtk.Template(resource_path='/tr/org/pardus/pardus-gnome-greeter/ui/OutroPage.ui')
class OutroPage(Adw.PreferencesPage):
    __gtype_name__ = 'OutroPage'
    
    explore_button = Gtk.Template.Child("explore_button")
    
    # Link buttons
    btn_website = Gtk.Template.Child("btn_website")
    btn_docs = Gtk.Template.Child("btn_docs")
    btn_community = Gtk.Template.Child("btn_community")
    btn_forum = Gtk.Template.Child("btn_forum")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.explore_button.connect("clicked", self.on_explore_clicked)
        
        # Connect link buttons
        self.btn_website.connect("clicked", self.on_link_clicked, "https://www.pardus.org.tr/")
        self.btn_docs.connect("clicked", self.on_link_clicked, "https://belge.pardus.org.tr/")
        self.btn_community.connect("clicked", self.on_link_clicked, "https://gonullu.pardus.org.tr/")
        self.btn_forum.connect("clicked", self.on_link_clicked, "https://forum.pardus.org.tr/")

    def on_explore_clicked(self, button):
        root = self.get_root()
        if root:
            root.close()
            
    def on_link_clicked(self, button, uri):
        """Open the given URI in default browser"""
        Gtk.show_uri(self.get_native(), uri, 0)
