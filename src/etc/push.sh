#! /bin/bash

WHEREIAM="${BASH_SOURCE%/*}/"

ampy -p /dev/ttyUSB0 -b 115200 mkdir etc 2>/dev/null

for file in $(find $WHEREIAM -type f \( -name "*.json" ! -name "*.example.json" \) -or -name "__init__.py")
do
    echo $file
    ampy -p /dev/ttyUSB0 -b 115200 put $file /etc/$(basename $file)
done
