
# Load Gtk
import gi
import threading
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk,Gdk,Gio,GObject,GdkPixbuf,GLib


from WallpaperManager import WallpaperManager
wallpaper_manager = WallpaperManager()

def init_wallpapers(wallpapers,flowbox):
    for wallpaper in wallpapers:
        #wallpaper_img = Gtk.Image.new_from_file(wallpaper)
        #wallpaper_img.set_default_size(100,100)
        #flowbox.insert(wallpaper_img,-1)

        bitmap = GdkPixbuf.Pixbuf.new_from_file(wallpaper)
        bitmap = bitmap.scale_simple(200,200,GdkPixbuf.InterpType.BILINEAR)
        wallpaper_img = Gtk.Image.new_from_pixbuf(bitmap)
        wallpaper_img.set_size_request(200,200)
        wallpaper_img.img_path = wallpaper
        GLib.idle_add(flowbox.insert, wallpaper_img, -1)
        #GLib.idle_add(self.flow_wallpapers.insert, wallpaper_img, -1)
    
def on_activate(app):
    # Pencere olusturuyoruz
    win = Gtk.ApplicationWindow(application=app)

    # Penceremizin boyutunu ayarliyoruz
    win.set_default_size(800,600)

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    flowbox = Gtk.FlowBox()
    flowbox.set_valign(Gtk.Align.START)
    flowbox.set_vexpand(True)
    flowbox.set_hexpand(True)
    flowbox.set_max_children_per_line(4)

    wallpapers = wallpaper_manager.get_wallpapers()

    thread = threading.Thread(target=init_wallpapers,args=(wallpapers,flowbox))
    thread.daemon = True
    thread.start()




    win.set_child(scrolled_window)
    scrolled_window.set_child(flowbox)
    win.present()





app = Gtk.Application(application_id='tr.org.pardus.buttons')
app.connect('activate', on_activate)

# Run the application
app.run(None)