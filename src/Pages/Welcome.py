import gi
import sys

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from data.lib.pardus import Ptk


def fun_create(label=""):
    # WELCOME PAGE BOX
    #  ________________________________________
    # |                                        |
    # |                                        |
    # |            (Logo Image)                |
    # |                                        |
    # |                                        |
    # |            (OS Name Label)             |
    # |                                        |
    # |                                        |
    # |          (Welcome Label)               |
    # |                                        |
    # |          (Description Label)           |
    # |                                        |
    # |                                        |
    # |                                        |
    # |                                        |
    # |________________________________________|

    ui_logo_image = Ptk.Image(file="../data/assets/logo.svg", pixel_size=250)
    ui_os_name_label = Ptk.Label(
        markup="<span size='50pt'><b>Pardus 23</b></span>", halign="center"
    )
    os_welcome = Ptk.Label(markup="<span size='25pt'>Welcome</span>", halign="center")
    os_description = Ptk.Label(label="This Application Help To Configure Pardus")
    box = Ptk.Box(
        name=label,
        orientation="vertical",
        hexpand=True,
        vexpand=True,
        halign="center",
        valign="center",
        spacing=25,
        children=[ui_logo_image, ui_os_name_label, os_welcome, os_description],
    )
    return box
