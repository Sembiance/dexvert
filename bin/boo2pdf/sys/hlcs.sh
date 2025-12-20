#!/bin/bash

function usage()
{
    echo 
    echo Usage:  hlcs.sh "<options>"
    echo 
    echo 
    echo Where:  "<options>" include:
    echo 
    echo   -i "shelf_name"           Open the specified shelf only
    echo                             
    echo   "shelf_name"              Display the specfied shelf followed by
    echo                             all shelves found by searching
    echo                             the User Defined Directories.
    echo 
    echo   -s -u "shelf_path(s)"     Open shelf or shelves found in the
    echo                             "location(s)" specified by the "shelf_path(s)"
    echo                             and the user defined directories
    echo 
    echo   -s "shelf_path(s)"        Open only the shelf or shelves found in
    echo                             the path specified by "shelf_path(s)".
    echo 
    echo   -b -u "book_path(s)"      Look for books in the "path(s)" specified by
    echo                             "book_path(s)" and the User Defined Directories.
    echo 
    echo   -b  "book_path(s)"        Look for books in the "path(s)" specified by
    echo                             "book_path(s)" only.
    echo 
    echo 
    echo Where:
    echo   "shelf_name"              The absolute file name of a shelf.
    echo 
    echo   "shelf_path(s)"           Semicolon-delimited list of absolute paths
    echo                             containing shelves.
    echo 
    echo   "book_path(s)"            Semicolon-delimited list of absolute paths
    echo                             containing books.
    echo 
    echo 
    echo Notes: 1. Absolute paths must be semicolon-delimited if there is more than one.
    echo        2. All flags must be surrounded by at least one blank character
    echo 
    echo 
    echo Examples:
    echo 
    echo   With No Options:
    echo 
    echo     hlcs.sh 
    echo 
    echo   With shelf option:
    echo 
    echo     hlcs.sh -i "/home/auser/shelves/shelf.bks" 
    echo 
    echo   With book options:
    echo 
    echo     hlcs.sh -b -u "/home/auser/books;/home/auser/books"
    echo 
    echo   With shelf options and book options:
    echo 
    echo     hlcs.sh -s -u "/home/auser/shelves;/home/auser/shelves" -b -u "/home/auser/books;a:/books"
    echo 
    echo   With all of the options:
    echo 
    echo     hlcs.sh -i "/home/auser/shelves/shelf.bks" -s -u "/home/auser/shelves;/opt/shelves" -b -u "/home/auser/books;/opt/books" 
    echo 
    echo   With the help option:
    echo 
    echo     hlcs.sh -help
}


pushd "`dirname $0`" >/dev/null 2>&1
mkdir -p  ~/.IBM/SCR >/dev/null 2>&1
XERCESC_NLS_HOME=$PWD
#dd3555  
#if [ "$LD_LIBRARY_PATH" = "" ]; then
#    LD_LIBRARY_PATH=/opt/scr/sys
#else
#    LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH
#fi
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD
#ee3555

PROGRAM_DIRECTORY="$PWD"
export LANG=en_US
if [ -e hlcs.jar ]; then
    jarfile=hlcs.jar
else
    jarfile=hlcs
fi

until [ -z "$1" -o "$1" = "-help" ]
do
    if [ "$1" = "-d" ]; then
        PROGRAM_DIRECTORY=$2
        shift
    else
        ARGUMENTS=$ARGUMENTS" "$1
    fi
    shift
done

if [ "$1" = "-help" ]; then
    usage
else
    export LD_LIBRARY_PATH
    java -cp XKS.jar -jar $jarfile $ARGUMENTS -d $PROGRAM_DIRECTORY  > ~/.IBM/SCR/hlcs.log 2>&1
fi

popd >/dev/null 2>&1
