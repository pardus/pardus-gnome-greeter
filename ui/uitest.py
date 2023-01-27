import gi
import os
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GLib

builder = Gtk.Builder()
builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/test.ui")


window = builder.get_object("window")
window.show()

loop = GLib.MainLoop()
loop.run()