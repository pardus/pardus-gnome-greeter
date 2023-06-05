import subprocess
import gi
gi.require_version("Gdk","4.0")
from gi.repository import Gdk


def get_layout_name():
        cmd = "gsettings get org.pardus.pardus-gnome-greeter layout-name"
        result =  subprocess.getoutput(cmd)
        return result[1:-1]


def set_layout_name(layout_name:str):
    cmd = "dconf write /org/pardus/pardus-gnome-greeter/layout-name \"'%s'\""%layout_name
    return subprocess.getoutput(cmd)
    #return subprocess.run(escape_cmd)

def get_current_theme():
    return subprocess.getoutput("dconf read /org/gnome/desktop/interface/color-scheme")

def apply_layout_config(config:str):
    return subprocess.getoutput(config)

def get_recommended_scale():
    display_server_cmd = 'echo $XDG_SESSION_TYPE'
    display_server = subprocess.getoutput(display_server_cmd)
    print(display_server)
    if display_server == 'wayland':
        return 100
    base_scale = 100
    screen_const = 50
    approximate_result = 0
    display = Gdk.Display.get_default()
    monitors = display.get_monitors()

    for monitor in monitors:

        width_mm = monitor.get_width_mm()
        height_mm = monitor.get_height_mm()

        width_px = monitor.get_geometry().width
        height_px = monitor.get_geometry().height

        wdpi = width_mm / width_px
        hdpi = height_mm / height_px

        approximate_result += screen_const / (wdpi + hdpi)
    result = base_scale * 100 / approximate_result * len(monitors)
    if result % 25 > 12.5:
        rounded_result = int(result + (25 - result % 25))
    else:
        rounded_result = int(result - (result % 25))

    return rounded_result
