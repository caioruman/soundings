#!/bin/bash

# Loop all the folders, select certain files and zip it
for d in */ ; do
	echo "Entering folder: " "$d"
	cd $d
        snumber=${d:0:5}
	#echo $snumber
	echo "Zipping some of the .csv in the folder " "$d"

#	echo 'soundings_'${snumber}'_????.csv'
	find . -name 'soundings_'${snumber}'_????.csv' -exec zip soundings_"$snumber".zip {} \;

	cd ..
#	echo soundings_"$snumber"_????.csv
done
