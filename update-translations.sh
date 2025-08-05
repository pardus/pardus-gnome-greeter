#!/bin/bash

langs=("tr" "pt" "es")

if ! command -v xgettext &> /dev/null
then
	echo "xgettext could not be found."
	echo "you can install the package with 'apt install gettext' command on debian."
	exit
fi

echo "updating pot file"
xgettext -o data/po/pardus-gnome-greeter.pot --files-from=data/po/POTFILES

for lang in ${langs[@]}; do
	if [[ -f data/po/$lang.po ]]; then
		echo "updating $lang.po"
		msgmerge -o data/po/$lang.po data/po/$lang.po data/po/pardus-gnome-greeter.pot
	else
		echo "creating $lang.po"
		cp data/po/pardus-gnome-greeter.pot data/po/$lang.po
	fi
done 