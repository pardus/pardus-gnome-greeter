import subprocess
import gi
import time

gi.require_version("Gtk", "3.0")
from gi.repository import GLib



layouts = {
    "set_1":{
        "enable":[
            "dash-to-panel@jderose9.github.com"
        ],
        "disable":[
            "dash-to-dock@micxgx.gmail.com",
            "arc-menu@pardus.org.tr"
        ]

    },
    "set_2":{
        "enable":[
            "dash-to-dock@micxgx.gmail.com"
        ],
        "disable":[
            "dash-to-panel@jderose9.github.com",
            "arc-menu@pardus.org.tr"
        ],
        "config":[
            "gsettings set org.gnome.shell.extensions.dash-to-dock dock-position LEFT",
            "gsettings set org.gnome.shell.extensions.dash-to-dock extend-height true",
            "gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed true"
        ]
    },
     "set_3":{
         "enable":[
            "dash-to-dock@micxgx.gmail.com",
        ],
        "disable":[
            "dash-to-panel@jderose9.github.com",
            "arc-menu@pardus.org.tr"
        ],
        "config":[
            "gsettings set org.gnome.shell.extensions.dash-to-dock dock-position BOTTOM",
            "gsettings set org.gnome.shell.extensions.dash-to-dock extend-height false",
            "gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed false"
        ]
        
    },
    "set_4":{
       "disable":[
            "dash-to-panel@jderose9.github.com",
            "dash-to-dock@micxgx.gmail.com",
            "arc-menu@pardus.org.tr"
        ]
    }
}

class LayoutChanger:
    def set_layout(self,layout_name:str):
        self.set_theme_on_gsettings(layout_name)
        if layout_name not in layouts:
            return "There is layout named %s"%layout_name
        
        if 'enable' in layouts[layout_name]:
            for extension in layouts[layout_name]["enable"]:
                self.extension_operations("enable",extension)
        
        if 'disable' in layouts[layout_name]:
            for extension in layouts[layout_name]["disable"]:
                self.extension_operations("disable",extension)
        
        if 'config' in layouts[layout_name]:
            for conf in layouts[layout_name]["config"]:
                self.apply_config(conf)

    def get_extensions(self,type: str): 
        if type not in ["enabled","disabled","all"]:
            return "type must be enabled, disabled or all"
        cmd = "gnome-extensions list"
        if type != "all":
            cmd += " --%s"%type
        return subprocess.getoutput(cmd)

    def extension_operations(self,type:str,ext_id:str):
        if type not in ["enable","disable"]:
            return "type must be enable or disable"
        cmd ="gnome-extensions %s %s"%(type,ext_id)
        return GLib.spawn_command_line_sync(cmd)

    def set_theme_on_gsettings(self,layout_name:str):
        cmd = "gsettings set org.pardus.pardus-gnome-greeter layout-name %s"%layout_name
        return GLib.spawn_command_line_sync(cmd)

    def apply_config(self,config:str):
        return GLib.spawn_command_line_sync(config)
