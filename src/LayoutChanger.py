import subprocess
import gi
import time

gi.require_version("Gtk", "4.0")
from gi.repository import GLib



layouts = {
    "layout_1":{
        "enable":[
            "dash-to-panel@jderose9.github.com"
        ],
        "disable":[
            "dash-to-dock@micxgx.gmail.com",
            "arc-menu@pardus.org.tr"
        ]

    },
    "layout_2":{
        "enable":[
            "dash-to-dock@micxgx.gmail.com"
        ],
        "disable":[
            "dash-to-panel@jderose9.github.com",
            "arc-menu@pardus.org.tr"
        ],
        "config":[
            #"gsettings set org.gnome.shell.extensions.dash-to-dock dock-position LEFT",
            "dconf write /org/gnome/shell/extensions/dash-to-dock/dock-position \"'LEFT'\"",
            #"gsettings set org.gnome.shell.extensions.dash-to-dock extend-height TRUE",
            "dconf write /org/gnome/shell/extensions/dash-to-dock/extend-height true",
            #"gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed true"
            "dconf write /org/gnome/shell/extensions/dash-to-dock/dock-fixed true"
        ]
    },
     "layout_3":{
         "enable":[
            "dash-to-dock@micxgx.gmail.com",
        ],
        "disable":[
            "dash-to-panel@jderose9.github.com",
            "arc-menu@pardus.org.tr"
        ],
        "config":[
            #"gsettings set org.gnome.shell.extensions.dash-to-dock dock-position BOTTOM",
            "dconf write /org/gnome/shell/extensions/dash-to-dock/dock-position \"'BOTTOM'\"",
            #"gsettings set org.gnome.shell.extensions.dash-to-dock extend-height false",
            "dconf write /org/gnome/shell/extensions/dash-to-dock/extend-height false",
            #"gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed false"
            "dconf write /org/gnome/shell/extensions/dash-to-dock/dock-fixed false"
        ]
        
    },
    "layout_4":{
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
        print(layout_name)
        all_extensions = self.get_extensions("all")
        enabled_extensions = self.get_extensions("enabled")
        disabled_extensions = self.get_extensions("disabled")
        if layout_name not in layouts:
            return "There is layout named %s"%layout_name
        
        if 'enable' in layouts[layout_name]:
            for extension in layouts[layout_name]["enable"]:
                if extension not in enabled_extensions:
                    self.extension_operations("enable",extension)
        
        if 'disable' in layouts[layout_name]:
            for extension in layouts[layout_name]["disable"]:
                if extension not in disabled_extensions:
                    self.extension_operations("disable",extension)
        
        if 'config' in layouts[layout_name]:
            for conf in layouts[layout_name]["config"]:
                escape_conf = conf
                # dont directly give conf as parameter to apply_config function.
                # otherwise escape characters wont be rendered correctly
                self.apply_config(escape_conf)

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
        #return subprocess.run(cmd)


    def set_theme_on_gsettings(self,layout_name:str):
        cmd = "dconf write /org/pardus/pardus-gnome-greeter/layout-name \"'%s'\""%layout_name
        return GLib.spawn_command_line_sync(cmd)
        #return subprocess.run(escape_cmd)


    def apply_config(self,config:str):
        return GLib.spawn_command_line_sync(config)
        #return subprocess.run(config)
