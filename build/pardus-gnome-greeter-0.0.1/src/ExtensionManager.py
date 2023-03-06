import subprocess
class ExtensionManager:
    
    def extension_operations(self,type,ext_id):
        
        if type not in ["enable","disable"]:
            return "type must be enable or disable"
        
        cmd ="gnome-extensions %s %s"%(type,ext_id)
        return subprocess.getoutput(cmd)
        
    def get_extensions(self,type: str): 
        if type not in ["enabled","disabled","all"]:
            return "type must be enabled, disabled or all"
        cmd = "gnome-extensions list"
        if type != "all":
            cmd += " --%s"%type
        return subprocess.getoutput(cmd)