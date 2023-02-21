import subprocess
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib
class ExtensionManager:
    
    def extension_operations(self,type,ext_id):
        print("extension operations: ",type,ext_id)
        if type not in ["enable","disable"]:
            print("enable disable da problem var")
            return "type must be enable or disable"
        
        cmd ="gnome-extensions %s %s"%(type,ext_id)
        return GLib.spawn_command_line_sync(cmd)
        
    def get_extensions(self,type: str): 
        if type not in ["enabled","disabled","all"]:
            return "type must be enabled, disabled or all"
        cmd = "gnome-extensions list"
        if type != "all":
            cmd += " --%s"%type
        return subprocess.getoutput(cmd)