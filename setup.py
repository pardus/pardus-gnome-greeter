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
    ("/usr/share/applications/", ["tr.org.pardus.pardus-gnome-greeter.desktop"]),
    ("/usr/share/pardus/pardus-gnome-greeter/", ["pardus-gnome-greeter.svg"]),
    ("/usr/share/pardus/pardus-gnome-greeter/src", [
        "src/Main.py",
        "src/MainWindow.py",
        "src/LayoutChanger.py"
    ]),
    ("/usr/share/pardus/pardus-gnome-greeter/ui", ["ui/ui2.glade"]),
        ("/usr/share/pardus/pardus-gnome-greeter/assets", [
            "assets/set1.svg",
            "assets/set2.svg",
            "assets/set3.svg",
            "assets/set4.svg",
    ]),

    ("/usr/share/pardus/pardus-gnome-greeter/css/", ["css/style.css"]),
    ("/usr/bin/", ["pardus-gnome-greeter"]),
    ("/usr/share/icons/hicolor/scalable/apps/", ["pardus-gnome-greeter.svg"])
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