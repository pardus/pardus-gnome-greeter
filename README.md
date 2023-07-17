## PARDUS GNOME GREETER
Customize and configure Pardus with few clicks.

### Testing Stored Layout
First we need to compile schema xml file. <br/>
* `glib-compile-schemas ./schema` <br/>
for testing we need to export gsettings schema directory <br>
* `export GSETTINGS_SCHEMA_DIR=<project_dir>/pardus-gnome-greeter/data/schema/`


### Running Application
To test and use application run the following command <br/>
`python3 <project_dir>/pardus-gnome-greeter/src/Main.py`

### Build deb package

* `sudo apt install devscripts git-buildpackage dh-python python3-distutils python3-lib2to3 python3-setuptools`
* `sudo mk-build-deps -ir`
* `gbp buildpackage --git-export-dir=./build/ -us -uc`

### Install deb package
After building deb package, it will be under your `<current_dir>/build/`.

You can install deb package with the following command: <br>
* ```sudo dpkg -i ./build/pardus-gnome-greeter_0.0.1_all.deb```

### Some Screenshots
![Screenshot1](/data/assets/screenshot1.png)

![Screenshot1](/data/assets/screenshot2.png)

![Screenshot1](/data/assets/screenshot3.png)

![Screenshot1](/data/assets/screenshot4.png)