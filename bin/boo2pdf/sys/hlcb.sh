#!/bin/bash
function usage()
{
    echo Usage:  hlcb.sh "<filename>" "<options>"
    echo
    echo Where:
    echo   All flags must be surrounded by at least one blank character
    echo   "<filename>"                    Optional book name
    echo   "<sourcepath>"                  Required field, path hlcb is being executed from
    echo
    echo Where "<options>" include:
    echo   -t "<topic>"                    Open book to a topic
    echo   -r "<reference>"                Open book to a reference
    echo   -s "<s_options> <arguments>"    Open book to a search
    echo   -h "<topic>" -s ...             Open book to a topic and search
    echo
    echo Where "<s_options>" are 0 "(off)" or 1 "(on)" for the following:
    echo   1: Exact matches only
    echo   2: Exact matches ignoring case
    echo   3: Fuzzy search
    echo   4: List results in sequence
    echo   5: List results in order of importance
    echo   6: Search in topic text
    echo   7: Search in titles
    echo   8: Search indexed words
    echo   9: show advanced search options
    echo
    echo Examples:
    echo   hlcb.sh \"/home/auser/books/books/book.boo/\" -t \"1.1\"
    echo   hlcb.sh \"/home/auser/books/books/book.boo/\" -s \"001011000\" \"Table 13-1\"
}

pushd "`dirname $0`" >/dev/null 2>&1
mkdir -p ~/.IBM/SCR >/dev/null 2>&1
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
if [ -e hlcb.jar ]; then
  jarfile=hlcb.jar
else
  jarfile=hlcb
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
    java -cp XKS.jar -jar $jarfile $ARGUMENTS -d $PROGRAM_DIRECTORY  > ~/.IBM/SCR/hlcb.log 2>&1
fi
popd >/dev/null 2>&1
