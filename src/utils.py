import subprocess

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
