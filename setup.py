#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os, subprocess




changelog = "debian/changelog"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = ""
    f = open("src/__version__", "w")
    f.write(version)
    f.close()


data_files = [
    ("/usr/share/glib-2.0/data/schemas/", [
    		"data/schema/tr.org.pardus.pardus-gnome-greeter.gschema.xml"
    	]
    ),
    ("/usr/share/applications/", [
    		"tr.org.pardus.pardus-gnome-greeter.desktop"
    	]
    ),
    ("/usr/share/pardus/pardus-gnome-greeter/", [
    		"pardus-gnome-greeter.svg"
    	]
    ),
    ("/usr/share/pardus/pardus-gnome-greeter/src", [
    		"src/Main.py",
    		"src/MainWindow.py",
			"src/LayoutManager.py",
	        "src/ExtensionManager.py",
	        "src/utils.py",
	        "src/ScaleManager.py",
	        "src/WallpaperManager.py"
    	]
    ),
    ("/usr/share/pardus/pardus-gnome-greeter/ui", [
    		"ui/ui.ui"
    	]
    ),
    ("/usr/share/pardus/pardus-gnome-greeter/assets", [
        
            	"data/assets/set1.svg",
            	"data/assets/set2.svg",
            	"data/assets/set3.svg",
            	"data/assets/set4.svg",
            
            	"data/assets/discord.svg",
            	"data/assets/facebook.svg",
            	"data/assets/github.svg",
            	"data/assets/linkedin.svg",
            	"data/assets/medium.svg",
            	"data/assets/twitter.svg",
            	"data/assets/youtube.svg",
            
            	"data/assets/logo.svg",
            
            	"data/assets/ext_app_indicator_image.png",
            	"data/assets/ext_app_indicator_logo.png",

            	"data/assets/ext_app_menu_image.png",
            	"data/assets/ext_app_menu_logo.png",

            	"data/assets/ext_caffeine_image.png",
            	"data/assets/ext_caffeine_logo.png",

            	"data/assets/ext_drive_menu_image.png",
            	"data/assets/ext_drive_menu_logo.png",

            	"data/assets/ext_places_menu_image.png",
            	"data/assets/ext_places_menu_logo.png",
            
            	"data/assets/on.svg",
            	"data/assets/off.svg",            
    	]
    ),
    ("/usr/share/pardus/pardus-gnome-greeter/data/", [
    		"data/style.css"
    	]
    ),
    ("/usr/bin/", [
    		"pardus-gnome-greeter"
    	]
    ),
    ("/usr/share/icons/hicolor/scalable/apps/", [
			"pardus-gnome-greeter.svg"
		]
	)
]

setup(
    name="pardus-gnome-greeter",
    version="0.0.1",
    packages=find_packages(),
    scripts=["pardus-gnome-greeter"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Pardus Altyapı",
    author_email="dev@pardus.org.tr",
    description="Pardus Gnome Greeter, change the layout of the desktop.",
    license="GPLv3",
    keywords="",
    url="https://www.pardus.org.tr",
)
