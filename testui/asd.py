import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class ExampleWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Flowbox Example")
        self.set_default_size(800, 600)

        # Create a ScrolledWindow
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_child(scrolled)

        # Create a Flowbox
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(30)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.set_child(flowbox)

        # Add some images to the Flowbox
        for i in range(50):
            image = Gtk.Image.new_from_file("image.jpg")
            image.set_size_request(200, 200) # Set the size of the images
            flowbox.insert(image,-1)

win = ExampleWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
