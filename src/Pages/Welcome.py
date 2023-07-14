from libpardus import Ptk


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
    os_welcome = Ptk.Label(markup="<span size='25pt'>Welcome</span>", halign="center")
    os_description = Ptk.Label(label="This Application Help To Configure Pardus")
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
