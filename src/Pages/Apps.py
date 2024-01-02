import os
import gi
import subprocess

gi.require_version("Gtk", "4.0")
from libpardus import Ptk
from gi.repository import Gtk, GdkPixbuf
from Server import Server
from Stream import Stream
import locale
from locale import gettext as _

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"
locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)


class Apps:
    def __init__(self):
        # +-------------------------------------------------------+
        # |                  Pardus Software Center               |
        # +--------------------------+----------------------------+
        # |                          |                            |
        # |         [Icon 1]         |         [Icon 2]           |
        # |        App Name 1        |        App Name 2          |
        # |                          |                            |
        # |                          |                            |
        # |         [Icon 3]         |         [Icon 4]           |
        # |        App Name 3        |        App Name 4          |
        # |                          |                            |
        # +--------------------------+----------------------------+

        self.apps_url = "https://apps.pardus.org.tr/api/greeter"
        self.non_tls_tried = False
        self.lang = os.getenv("LANG")[0:2]
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        ui_software_center_image = Ptk.Image(
            file=cur_dir + "/../../data/assets/pardus-software.svg",
            pixel_size=100,
            margin_top=50,
        )

        ui_software_center_markup = (
            f"<span font-size='20pt'><b>{_('Pardus Software Center')}</b></span>"
        )

        ui_software_center_label = Ptk.Label(
            markup=ui_software_center_markup, halign="center"
        )

        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        self.iconview = Gtk.IconView.new()

        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.set_item_orientation(Gtk.Orientation.HORIZONTAL)
        self.iconview.connect("item-activated", self.open_app)
        self.iconview.set_hexpand(True)
        self.iconview.set_vexpand(True)
        self.iconview.set_activate_on_single_click(True)
        self.iconview.set_item_width(155)

        self.ui_display_box = Ptk.Box(
            orientation="vertical",
            hexpand=True,
            vexpand=True,
            xalign="start",
            yalign="start",
            spacing=21,
            margin_start=13,
            margin_end=13,
            children=[
                ui_software_center_image,
                ui_software_center_label,
            ],
        )
        self.stream = Stream()
        self.stream.StreamGet = self.StreamGet

        self.server_response = None
        self.server = Server()
        self.server.ServerGet = self.ServerGet
        self.server.get(self.apps_url, "test")

    def open_app(self, widget, path):
        selected_item = widget.get_selected_items()
        treeiter = self.liststore.get_iter(selected_item[0])
        appname = self.liststore.get(treeiter, 2)[0]
        widget.unselect_all()
        subprocess.Popen(["pardus-software", "-d", appname])

    def StreamGet(self, pixbuf, data):
        lang = f"pretty_{self.lang}"

        label = data[lang]
        name = data["name"]
        self.liststore.append([pixbuf, label, name])

    def ServerGet(self, response):
        if "error" not in response.keys():
            datas = response["greeter"]["suggestions"]
            if len(datas) > 0:
                for data in datas:
                    if self.non_tls_tried:
                        data["icon"] = data["icon"].replace("https", "http")
                    self.stream.fetch(data)
            self.ui_display_box.append(self.iconview)
        else:
            if "tlserror" in response.keys() and not self.non_tls_tried:
                self.non_tls_tried = True
                self.apps_url = self.apps_url.replace("https", "http")
                print("trying {}".format(self.apps_url))
                self.server.get(self.apps_url, "test")
            else:
                error_message = response["message"]
                error_label = Ptk.Label(label=error_message, hexpand=True, halign="center")
                self.ui_display_box.append(error_label)

    def fun_create(self):
        return self.ui_display_box
