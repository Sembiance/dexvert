#!/bin/bash
export LD_LIBRARY_PATH=/mnt/compendium/DevLab/dexvert/bin/boo2pdf/sys/

../zulu/bin/java -cp ".:/mnt/compendium/DevLab/dexvert/bin/boo2pdf/sys/hlccommon.jar:/mnt/compendium/DevLab/dexvert/bin/boo2pdf/sys/XKS.jar" boo2pdf -d /mnt/compendium/DevLab/dexvert/bin/boo2pdf/sys/ eala2201.boo /tmp/out


# /usr/local/bin/xvfb-run.sh -f $BOOTMP/booX -s '-screen 0 1024x768x24' java -cp $BOOKMANAGER/bin:$BOOKMANAGER/sys/hlccommon.jar:$BOOKMANAGER/sys/XKS.jar boo2pdf -d $BOOKMANAGER/sys/ $FILENAME $BOOTMP/$BASENAME

