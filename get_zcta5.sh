#!/bin/sh

COLLECTION=$1


if [ -z $COLLECTION ]; then
  echo "usage $0 COLLECTION"
  echo "e.g. COLLECTION: TIGER2017"
  exit 1
fi

#wget --random-wait --recursive --continue --no-parent -e robots=off --force-directories -A .zip https://www2.census.gov/geo/tiger/${COLLECTION}/ZCTA5/

zipfile=`find www2.census.gov -name \*zip`

dbf=`zipinfo $zipfile | awk '{print $9}' | grep dbf`

unzip $zipfile $dbf
