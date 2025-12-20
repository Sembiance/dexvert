#!/bin/bash -e
# $1 is the input book name
# $2 is the root name (w/o extension)

BOOKMANAGER=/usr/local/BookManager
export LD_LIBRARY_PATH=$BOOKMANAGER/sys
BOOTMP=/tmp/boo2pdf
FILENAME=$1
BASENAME=$2

/usr/local/bin/xvfb-run.sh -f $BOOTMP/booX -s '-screen 0 1024x768x24' java -cp $BOOKMANAGER/bin:$BOOKMANAGER/sys/hlccommon.jar:$BOOKMANAGER/sys/XKS.jar boo2pdf -d $BOOKMANAGER/sys/ $FILENAME $BOOTMP/$BASENAME

# Fix image paths
sed -i s"|file:///||" $BOOTMP/$BASENAME.html

# Remove large indent that throws images off screen
sed -i 's|                                  <A HREF="REF:PIC|<A HREF="REF:PIC|g' $BOOTMP/$BASENAME.html

# Convert to PDF
htmldoc --compression=9 --left 36 --webpage --outfile $BOOTMP/$BASENAME.pdf $BOOTMP/$BASENAME.html

# Remove temporary Xauthority from Xvfb
rm -f $BOOTMP/booX
