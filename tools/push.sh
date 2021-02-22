#! /bin/bash

WHEREIAM="${BASH_SOURCE%/*}/"

if [[ $1 ]]
then
    echo $1
    ampy -p /dev/ttyUSB0 -b 115200 put $1
else

    for file in $(find $WHEREAMI -maxdepth 1 -type f -name "*.py")
    do
        echo $file
        ampy -p /dev/ttyUSB0 -b 115200 put $file
    done

fi
