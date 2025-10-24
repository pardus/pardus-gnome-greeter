#!/bin/bash

langs=("tr" "pt" "es")

if ! command -v xgettext &> /dev/null
then
	echo "xgettext could not be found."
	echo "you can install the package with 'apt install gettext' command on debian."
	exit
fi

echo "Updating pot file..."

# Define source files for different parsers
PY_FILES=$(grep '.py$' data/po/POTFILES | tr '\n' ' ')
UI_FILES=$(grep -E '.ui$|.desktop.in$' data/po/POTFILES | tr '\n' ' ')

# Extract from Python files
xgettext -o data/po/py.pot -L Python $PY_FILES

# Extract from UI and .desktop files
xgettext -o data/po/ui.pot -L Glade --keyword=_ --keyword=Name --keyword=Comment --keyword=Keywords $UI_FILES

# Merge pot files
msgcat --sort-output data/po/py.pot data/po/ui.pot > data/po/pardus-gnome-greeter.pot

# Clean up temporary files
rm data/po/py.pot data/po/ui.pot

for lang in ${langs[@]}; do
	if [[ -f data/po/$lang.po ]]; then
		echo "Updating $lang.po"
		msgmerge -U data/po/$lang.po data/po/pardus-gnome-greeter.pot
	else
		echo "Creating $lang.po"
		cp data/po/pardus-gnome-greeter.pot data/po/$lang.po
	fi
done 