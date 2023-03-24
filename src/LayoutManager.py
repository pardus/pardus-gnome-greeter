import subprocess
from ExtensionManager import ExtensionManager
from utils import get_current_theme,get_layout_name,set_layout_name,apply_layout_config

ExtensionManager = ExtensionManager()
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

class LayoutManager:
    def set_layout(self,layout_name:str):
        set_layout_name(layout_name)
        enabled_extensions = ExtensionManager.get_extensions("enabled")
        disabled_extensions = ExtensionManager.get_extensions("disabled")

        if layout_name not in layouts:
            return "There is layout named %s"%layout_name
        
        if 'enable' in layouts[layout_name]:
            for extension in layouts[layout_name]["enable"]:
                if extension not in enabled_extensions:
                    ExtensionManager.extension_operations("enable",extension)
                    #extension_manager.extension_operations("enable",extension)
        
        if 'disable' in layouts[layout_name]:
            for extension in layouts[layout_name]["disable"]:
                if extension not in disabled_extensions:
                    ExtensionManager.extension_operations("disable", extension)
                    #extension_manager.extension_operations("disable",extension)
        
        if 'config' in layouts[layout_name]:
            for conf in layouts[layout_name]["config"]:
                escape_conf = conf
                # dont directly give conf as parameter to apply_config function.
                # otherwise escape characters wont be rendered correctly
                apply_layout_config(escape_conf)