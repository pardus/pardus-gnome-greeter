from libpardus import Ptk
import locale
from locale import gettext as _

APPNAME_CODE = "pardus-gnome-greeter"
TRANSLATIONS_PATH = "/usr/share/locale"

locale.bindtextdomain(APPNAME_CODE, TRANSLATIONS_PATH)
locale.textdomain(APPNAME_CODE)


def fun_create():
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

    ui_logo_image = Ptk.Image(file="../data/assets/logo.svg", pixel_size=180)

    ui_os_name_label = Ptk.Label(
        markup="<span size='50pt'><b>Pardus 23</b></span>", halign="center"
    )
    markup = f"<span size='25pt'>{_('Welcome')}</span>"
    os_welcome = Ptk.Label(markup=markup, halign="center")
    os_description = Ptk.Label(label=_("This application helps configure Pardus"))
    box = Ptk.Box(
        orientation="vertical",
        hexpand=True,
        vexpand=True,
        halign="center",
        valign="center",
        spacing=21,
        children=[
            ui_logo_image,
            ui_os_name_label,
            os_welcome,
            os_description,
        ],
    )
    return box
