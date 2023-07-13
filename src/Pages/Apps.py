import os
import gi
import urllib
import requests
import random
import subprocess

gi.require_version("Gtk", "4.0")
from libpardus import Ptk
from utils import get_current_theme
from gi.repository import GLib, Gtk, Gio, GdkPixbuf
from utils import get_recommended_scale
from Server import Server
from Stream import Stream

url = "https://apps.pardus.org.tr/api/greeter"


class Apps:
    def __init__(self):
        cur_dir = os.path.dirname(__file__)
        ui_software_center_image = Ptk.Image(
            file=cur_dir + "/../../data/assets/pardus-software.svg",
            pixel_size=100,
            margin_top=50,
        )
        ui_software_center_markup = (
            "<span font-size='20pt'><b>Pardus Software Center</b></span>"
        )
        ui_software_center_label = Ptk.Label(
            markup=ui_software_center_markup, halign="center"
        )
        remove_this_label = Ptk.Label(
            markup="<span font-size='12pt'>Kullanmayan bin pisman</span>",
            halign="center",
        )
        self.flowbox = Ptk.FlowBox(
            min_children_per_line=2, row_spacing=23, column_spacing=23, halign="center"
        )
        self.ui_display_box = Ptk.Box(
            orientation="vertical",
            hexpand=True,
            vexpand=True,
            xalign="start",
            yalign="start",
            spacing=23,
            margin_start=13,
            margin_end=13,
            children=[
                ui_software_center_image,
                ui_software_center_label,
                remove_this_label,
                self.flowbox,
            ],
        )
        self.stream = Stream()
        self.stream.StreamGet = self.StreamGet

        self.server_response = None
        self.server = Server()
        self.server.ServerGet = self.ServerGet
        self.server.get(url, "test")

    def open_app(self, widget):
        subprocess.Popen(["pardus-software", "-d", widget.get_name()])

    def StreamGet(self, pixbuf, data):
        image = Ptk.Image.new_from_pixbuf(pixbuf)
        image.set_size_request(50, 50)
        label = Ptk.Label(
            vexpand=True, label=data["pretty_en"], valign="center", halign="center"
        )
        box = Ptk.Box(
            width=150,
            spacing=13,
            children=[image, label],
        )
        button = Ptk.Button(name=data["name"])
        button.connect("clicked", self.open_app)
        button.set_child(box)

        self.flowbox.insert(button, -1)

    def ServerGet(self, response):
        datas = response["greeter"]["suggestions"]
        if len(datas) > 0:
            for data in datas:
                label = Ptk.Label(label=data["pretty_en"])
                self.stream.fetch(data)

    def fun_create(self):
        return self.ui_display_box
