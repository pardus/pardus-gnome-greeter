import os
import gi
import os
import json
import locale
import subprocess

from libpardus import Ptk
from locale import gettext as _

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)


def fun_create():
    # RETURNING OUTRO BOX
    # _______(Box)____________________________________________
    # |                                                       |
    # |   _______(Box)___________________________________     |
    # |  |                                               |    |
    # |  |   (Label: Social Media Accounts)              |    |
    # |  |                                               |    |
    # |  |                                               |    |
    # |  |  ________(Box)_____     ________(Box)_____    |    |
    # |  | |                  |   |                  |   |    |
    # |  | |  (LinkButton)    |   |  (LinkButton)    |   |    |
    # |  | |   [Image]        |   |   [Image]        |   |    |
    # |  | |__________________|   |__________________|   |    |
    # |  |                                               |    |
    # |  |_______________________________________________|    |
    # |                                                       |
    # |                                                       |
    # |   ________(Box)_______   ________(Box)______          |
    # |  |                    | |                   |         |
    # |  |   (Label:          | |  (Button:         |         |
    # |  |   Phone Number)    | |  Open Shortcuts)  |         |
    # |  |                    | |                   |         |
    # |  | [Phone Number]     | |                   |         |
    # |  |                    | |                   |         |
    # |  |____________________| |___________________|         |
    # |                                                       |
    # |   _______(Box)___________________________________     |
    # |  |                                               |    |
    # |  |   (Label: Platforms)                          |    |
    # |  |                                               |    |
    # |  |                                               |    |
    # |  |  ________(Box)_____     ________(Box)_____    |    |
    # |  | |                  |   |                  |   |    |
    # |  | |  (LinkButton)    |   |  (LinkButton)    |   |    |
    # |  | |   [Image]        |   |   [Image]        |   |    |
    # |  | |__________________|   |__________________|   |    |
    # |  |                                               |    |
    # |  |_______________________________________________|    |
    # |                                                       |
    # |_______________________________________________________|

    def ui_shortcut_trigger_button_clicked(button):
        subprocess.Popen(["gtk-launch", "tr.org.pardus.pardus-gnome-shortcuts"])

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    with open(cur_dir + "/../../data/social_media.json") as file:
        social_media_datas = json.loads(file.read())
    with open(cur_dir + "/../../data/links.json") as links:
        link_datas = json.loads(links.read())
    ui_bold_markup = """<span size='27pt'><b>{text}</b></span>"""
    ui_social_media_label_markup = ui_bold_markup.format(
        text=_("Social Media Accounts")
    )
    ui_social_media_label = Ptk.Label(
        markup=ui_social_media_label_markup, halign="center"
    )
    ui_social_media_link_box = Ptk.Box(halign="center", hexpand=True, spacing=13)
    for data in social_media_datas:
        btn = Gtk.LinkButton(uri=data["url"])
        img_file_dir = cur_dir + "/../../data/assets/" + data["img"]
        ui_media_img = Ptk.Image(file=img_file_dir, pixel_size=37)
        btn.set_child(ui_media_img)
        ui_social_media_link_box.append(btn)
    ui_social_media_box = Ptk.Box(
        spacing=23,
        halign="center",
        valign="center",
        orientation="vertical",
        children=[ui_social_media_label, ui_social_media_link_box],
    )

    ui_support_label = Ptk.Label(markup=ui_bold_markup.format(text=_("Support")))
    ui_shortcuts_label = Ptk.Label(markup=ui_bold_markup.format(text=_("Shortcuts")))
    ui_support_labels_box = Ptk.Box(
        spacing=23,
        hexpand=True,
        valign="center",
        halign="center",
        children=[ui_support_label, ui_shortcuts_label],
    )

    ui_support_phone_markup = "+90  <span size='18pt'><b>444 5 773</b></span>"

    ui_support_phone_label = Ptk.Label(markup=ui_support_phone_markup)
    ui_shortcut_trigger_button = Ptk.Button(label=_("Open Shortcuts"), valign="start")
    ui_shortcut_trigger_button.connect("clicked", ui_shortcut_trigger_button_clicked)

    ui_support_content_box = Ptk.Box(
        spacing=23,
        hexpand=True,
        valign="center",
        halign="center",
        children=[ui_support_phone_label, ui_shortcut_trigger_button],
    )

    ui_support_box = Ptk.Box(
        orientation="vertical",
        spacing=23,
        hexpand=True,
        valign="center",
        halign="center",
        children=[ui_support_labels_box, ui_support_content_box],
    )

    ui_support_box2 = Ptk.Box(
        spacing=23,
        hexpand=True,
        valign="center",
        halign="center",
        children=[ui_support_phone_label, ui_shortcut_trigger_button],
    )
    ui_link_box = Ptk.Box(
        homogeneous=True,
        hexpand=True,
        valign="center",
        halign="center",
    )
    for data in link_datas:
        btn = Gtk.LinkButton(uri=data["url"], label=_(data["text"]))
        ui_link_box.append(btn)

    ui_outro_box = Ptk.Box(
        hexpand=True,
        homogeneous=True,
        orientation="vertical",
        valign="fill",
        halign="center",
        children=[ui_social_media_box, ui_support_box, ui_link_box],
    )

    return ui_outro_box
