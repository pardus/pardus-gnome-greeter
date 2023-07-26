import subprocess
class ScaleManager:
    def set_scale(self,scale:float):
        cmd = "gsettings set org.gnome.desktop.interface text-scaling-factor %s"%scale
        return subprocess.getoutput(cmd)
    def get_scale(self):
        cmd = "gsettings get org.gnome.desktop.interface text-scaling-factor"
        return subprocess.getoutput(cmd)