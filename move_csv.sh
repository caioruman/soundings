#!/bin/bash

# Loop all the folders, select certain files and zip it
for d in */ ; do
	echo "Entering folder: " "$d"
	cd $d
        snumber=${d:0:5}
	#echo $snumber
	#echo "Zipping some of the .csv in the folder " "$d"
	echo "Moving zip file to usb key"
	mv 'soundings_'$snumber'.zip' /media/caioruman/CAIO_USBKEY/SoundingsV2/CSV/

#	echo 'soundings_'${snumber}'_????.csv'
#	find . -name 'soundings_'${snumber}'_????.csv' -exec zip soundings_"$snumber".zip {} \;
#	exit
	cd ..
#	echo soundings_"$snumber"_????.csv
done
