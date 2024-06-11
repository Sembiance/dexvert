THE FINISHING TOUCH
Professional Software Installer
Version 3.0
March 21, 1995

The Finishing Touch is updated several times per year.  To get the latest
shareware copy of the Finishing Touch, call our BBS: (505) 275-9696.

Our BBS has a credit card registration feature which will allow you to
download the registered version IMMEDIATELY after you order.  Registered
users may call our BBS as often as they like to download FREE updates to
version 2.X.

This is a fully working shareware copy of THE FINISH TOUCH.
          ~~~~~~~~~~~~~
NOTE:  The ONLY difference between this shareware copy and the registered
       version is that the shareware copy does a CRC check on the files
       ORDER.TXT and INSTALL.TXT.  This causes up to a TEN SECOND TIME
       DELAY at the beginning of this program.  The registered version
       does NOT have this restriction.

To print the documentation use the command:
    COPY INSTALL.TXT LPT1:
    COPY README.TXT LPT1:

To print the order form use the command:
    COPY ORDER.TXT LPT1:

The Finishing Touch Software Installer consists of the minimum six files:
   PACKER.EXE             file compression utility
   INSTALL.EXE            installation utility
   INSTALL.FIL            sample installation script file
   INSTALL.TXT            documentation for all of the above
   ORDER.TXT              order form
   README.TXT             this file

If these files are missing or altered, the software WILL NOT run!

A seventh file, SAMPLE.PAK should be included with this software to
so people can see first hand how the software installer works with a "real"
application.  ALL SEVEN files must be on the floppy disk to see the demo
run or you will get a "Files Missing" message.

Several other, optional files are included so you can see a "real" scripts:
   Tax Sheltered Annuity Software:  1.FIL, 2C.FIL, 2B.FIL, and 4.FIL
   MOVIES TO GO! Software:          MOVIES1.FIL, MOVIES2.FIL and MOVIES.BAT
   THE COLOR WIZARD:                WIZARD.FIL and WIZARD.BIN
   To use the program as an upate:  UPDATE.FIL

Modifying INSTALL.FIL and these files is the "fast start" way to learn
how to use THE FINISHING TOUCH.  You have a fully working shareware evaluation
copy of THE FINISHING TOUCH, and hope you the smallest, most powerful,
easiest to use product with the best file compression available anywhere.

Michael J. Prestwich,
President,
ImagiSOFT, Inc.



June 10, 1992

Today we added a new feature:

A customer needed a SET.BUFFERS command similar SET.FILES so we added it.
It works exactly the same way as SET.FILES command does; see the documentation
for details.


June 15, 1992

Today we added several new commands:

PROMPT On/Off turns windows on or off for the COPY, DELETE, DISK, and UNPACK
commands.  This is easier than "hiding" windows by making them the same color
as the background as explained in the documentation.

PAUSE t
Pause for t hundredths of a second.  Nice if you want to "animate" windows.

WINMOVE x y
Moves the current window the new x y position.  If you use the command
WINMOVE +1 +1 it will move the current window relative to its current position
one row down and one row across.

BORDER t
   t = type   0 = none
              1 = single line (default)
              2 = double line

WINUPDATE x y c
          x position on the screen
          y position on the screen
          c color value

Use WINUPDATE to display a string inside the current open window. For example:
  WINUPDATE +2 +1 79
  "This line is displayed in the current"
  "window with white letters on a red"
  "background.  It is relative to the"
  "upper left corner by 2 characters across"
  "and 1 row down."

Relative Cursor / Window Positions

WINOPEN now supports relative cursor positions.  For example, WINOPEN +0 +5 17
will open a new window 5 rows down from the last window open. Relative
positioning also works in the UNPACK, PATH, DRIVE, ASK, COPY, DELETE, WINMOVE,
and WINUPDATE commands.

Relative cursor positioning is especially useful when you are printing the
selected DRIVE and PATH on the screen with the variables ~1 and ~2.
For example:

WINOPEN 0 0 79                                           ' red centered window
"The directory ~1~2 already exists and contains files!"
"Are you SURE you want to install your software in"
"this directory    Y / N?"
ASK +26 +3                                               ' position cursor on
                                                         ' the N character
                                                         ' no matter how the
                                                         ' window is centered


August 12, 1992    Version 2.2

We added a new command:

INPUT s l x y c
This command allows the user to input text strings which you can assign to
the variables ~A through ~Z.  Your script can substitute these codes similar
to the ~0, ~1, ~2, and ~3 variables as explained in the documentation.

    s    = String ID ("A" through "Z", your choice).
    l    = String length, from 1 to 40.

    x, y = Input position on the screen.  It is best to use
           the + and - here, because the entire input field
           must be contained within the current open window.

    c    = Input color (see the color chart in the documentation).

Example:

    WINOPEN 0 0 31           ' open a window centered on the screen
                             ' in color 31 (bright white on blue)

    ""
    "Please enter the following information:           "
    ""
    "Name:"
    "Address:"
    "City, State, Zip:"
    ""
    "License Number:"
    ""

    ' input 30 characters in color 15 (bright white on black)

    INPUT N 30 +20 +4 15     ' (Name)             assign to variable "N"
    INPUT A 30 +20 +5 15     ' (Address)          assign to variable "A"
    INPUT C 30 +20 +6 15     ' (City, State, Zip) assign to variable "C"

    ' NOTE: the license number is only 15 characters long

    INPUT L 15 +20 +8 15     ' (License Number)   assign to variable "L"

    WINCLOSE                 ' close the window

    ' write the results into an
    ' ASCII file called USER.FIL

    FILE ~1~2\USER.FIL

    "Name:              ~N"          ' The text that the user input
    "Address:           ~A"          ' will be substituted for the
    "City, State, Zip   ~C"          ' appropriate variables ~N, ~A,
    ""                               ' ~C, and ~L.
    "License Number     ~L"


February 9, 1993   Version 2.3

This version fixes a bug in the SET.PATH statement.  In previous versions
SET.PATH adds the directory to the PATH whether or not the directory already
exists in the PATH.  This was especially frustrating if the user had to
install the software several times.  Now SET.PATH looks to see if the
directory already exists in the PATH, and if it does, the SET.PATH
statement isn't executed.


We also added the CALL command:

CALL l
     l = Name of the label to call.  The last line of this label must end
         with RETURN or an error will result.

For example:

CALL TMP_DEL
.
.
.

' --------------------------------
'   * * * shared routines * * *
' --------------------------------

' --------------------------
'   delete temporary file
'    (don't inform user)
' --------------------------
:TMP_DEL
PROMPT OFF
DELETE ~A.TMP 0 0 0
PROMPT ON
BEEP
RETURN


March 3, 1993

We have forced the ~3 variable to reference the root directory of the drive
given in the COMSPEC variable found in the environment.  Several of our users
have noted that the COMSPEC=C:\COMMAND.COM entry placed in the environment
by DOS is often changed for various reasons to read COMSPEC=C:\DOS\COMMAND.COM
or something similar.  Since, in this example, the ~3 variable would be set
to C:\DOS, the CONFIG.SYS and AUTOEXEC.BAT files could not be correctly
modified.  This change discards the \DOS portion, and forces ~3 to reference
the root directory of C:.  This should resolve any problems that you have
experienced with the SET.FILES, SET.BUFFERS, and SET.PATH commands.


March 12, 1993    Version 2.4

The BEEP command has been expanded to allow the following variations:

               BEEP ON
               BEEP OFF

If the BEEP ON command is issued, all internal error messages that open
a window will beep the speaker.  The option can be disabled using the
BEEP OFF command, which is the start-up default.  This feature was added
at the request of developers who write software for visually impaired users.


March 31, 1993

Some of our users have expressed a need for the PATH command to permit
installation to the root directory for cases involving substituted or
network drives.  Currently, the root directory is only allowed if the user
is installing to a floppy disk, otherwise, a directory name must be given.
Today we have added a "back door" to bypass this error trap.  Simply
terminate the pre-stuffed default path (the first parameter in the PATH
command) with a semi-colon, and The Finishing Touch will allow the user
to access the root directory.  Without the semi-colon, the PATH command
will function as before.  However, if the terminator is given, it is
stripped from the string prior to input, and the error trap will be bypassed.

For example:

    PATH \WORDPRO; 10 10 31 15 20 12 79
                 ^
                 This semi-colon terminator instructs the PATH command to
                 permit installation to the root directory of a hard drive.


April 16, 1993

A new command has been added to test free disk space:

    FREE X       Where X is the minimum amount of free disk space
                 required on the target drive.  The value is given in
                 K bytes (i.e. 1024 = 1,048,576 bytes or 1Mb).  The
                 internal YES or NO flag is set to YES if the free
                 disk space is available, and set to NO if it is not.

This function differs from the SPACE command in that FREE can be issued
at any time in the script file.  The SPACE command must be issued before
the DRIVE command, and is not tested until the drive letter is entered.


September 20, 1993

The DRIVE and PATH commands can now be set to a specific location without
prompting the user by entering the command without any location or color
variables.  For example, set the DRIVE and PATH to C:\WINDOWS
   DRIVE C:
   PATH \WINDOWS

For an example of how this can be used, see the script file EASY.FIL in
SAMPLES.ZIP.  We use this new feature to install our product, EASY TO LEARN
COMPUTING in the Windows environment.



September 27, 1993  Version 2.5

The LANGUAGE command was extended today to include

   LANGUAGE DANISH  So that those in Denmark can read the error messages
                    in their own language.  For languages other than
                    English, French, Spanish, German, and now, Danish,
                    use the command PROMPT OFF and enter your own error
                    messages, PATH Prompt, Unpacking message, etc.



November 11, 1993  Version 2.6

The LANGUAGE command was extended today to include

   LANGUAGE DUTCH   So that those in Holland can read the error messages
                    in their own language.  For languages other than
                    English, French, Spanish, German, Danish, and now, Dutch,
                    use the command PROMPT OFF and enter your own error
                    messages, PATH Prompt, Unpacking message, etc.


April 18, 1994   Version 2.7

The BACKGROUND command was extended today to display a binary screen file.
It still supports the numeric backgrounds as explained in the documentation
(for example, BACKGROUND 48 displays a cyan background), but if a filename
of a binary screen is passed, it will now display that screen.  For example:

   BACKGROUND ~0\WIZARD.BIN

Binary screens can be created with THE LAUGHING DOG screen editor and
THE DRAW which are both in the shareware area of our BBS.  If you try these
programs and create a binary screen that you eventually use with THE FINISHING
TOUCH, please remember to register them with their respective authors.

An example of how we implemented this new command can be found in SAMPLES.ZIP
on our BBS in the files WIZARD.FIL (which you should rename to INSTALL.FIL) and
WIZARD.BIN.  A shareware version of THE COLOR WIZARD is available in the file
CLRWIZ10.ZIP.


May 10, 1994

We made a minor change to THE FINISHING TOUCH which allows the DRIVE
command to accept either the drive letter by itself, or the drive letter plus
a colon (C or C: now both work).  We did this for a user who wanted UNPACK
files from the hard disk to speed up disk I/O.  This involves a complicated
set of commands to reset the ~0 variable to ~1~2.  See HD.FIL in SAMPLES.ZIP
for details.


June 15, 1994   Version 2.8

The LANGUAGE command was extended today to include

   LANGUAGE NORWEGIAN  so Norwegian users can read the error messages
                       in their own language.  Registered users who want to
                       help us add other languages should download
                       LANGUAGE.ZIP from our BBS:  (505) 275-9696.


December 15, 1994  Version 2.9

Today we added the /N switch to PACKER because several people have reported
frustration with large, highly compressed files.  If you are distributing
files which are already compressed such as .GIF graphics files, use a
command similar to

   PACKER A:GIFS.PAK *.GIF /N

to disable PACKER's compression algorithm.  This will greatly reduce the
time it takes to make master disks if you have large compressed files.


March 21, 1995  Version 3.0

We have had several people report that even though PACKER gives tight
compression, it is quite slow.  We purchased this, the default file compression
routine from a third party.  Several people have reported "mysterious"
intermittent problems with this third party compression routine:

  1) A software developer in Australia discovered that creating master disks
     with DOS version 6.2 causes two of his in house computers which use
     DOS 6.0 to freeze while installing the software.

  2) A software developer in Atlanta, who has been using THE FINISHING
     TOUCH flawlessly for two years on dozens of computers, suddenly
     discovered that their new Pentium 90 computer freezes.

  3) A company in Minneapolis encountered a "freezing" problem with one
     of their customer's computers.  When sending a new set of disks
     didn't fix the problem, they had the customer hit the floppy several
     times against their desk.  The "freezing" problem disappeared!

We at ImagiSOFT have NEVER been able to duplicate any of the above problems.
We use THE FINISHING TOUCH for our entertainment products and the products
we develop for life insurance companies.  We distribute several hundred
disks each month, and EACH time we have encountered "freezing" while the
computer is UNPACKing a file it has been for one of the following reasons:

  1) One of our distribution floppies was bad.

  2) There wasn't enough room on the user's hard disk.

  3) The user's hard disk had bad sectors or corrupted files.  The install
     worked beautifully after the customer ran SCANDISK.

Three years ago we developed a compression routine written entirely in
assembly language which compresses files MUCH faster than the third party
compression routine, but it packs files only about 75% as well.  This version
of THE FINISHING TOUCH now includes this routine.  If you have any apprehension
about using the third party compression routine, or if you have some room
on your last distribution disk, use the "quick" compression method by adding
the /Q option to PACKER:

   PACKER A:TEXT.PAK *.TXT /Q

The UNPACK command in INSTALL.EXE remains unchanged.  It will determine for
itself whether you used the third party compression method (default), no
compression (/N), or ImagiSOFT's own, "quick" routine (/Q).


OS/2 Bug Reported
~~~~~~~~~~~~~~~~~
A user in Germany noticed that several commands in THE FINISHING TOUCH do not
work if the computer is running OS/2 WARP AND FLOPPY DISK HAS A VOLUME LABEL.
If the floppy has no volume label, the software seems to work just fine.
Weird.  We have not been able to reproduce this error since we are not using
OS/2 WARP.  You may want to avoid using VOLUME LABELS on your disk in case
your customer is using OS/2.



ANSWERS TO COMMON QUESTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Question:  I want to leave the user at the DOS prompt in the directory
           where the software was installed.  What is the easiest way to
           do this?

Answer:    The RUN command will run .EXE files, .COM files, and DOS commands.
           The command RUN ~1~2\CLS will exit INSTALL.EXE, change to the
           directory where you installed the software, clear the screen,
           and leave the computer at the DOS prompt.


Question:  How do you tell whether or not a DIRECTORY exists on the user's
           hard drive?

Answer:    The EXIST command works exactly the way the DIR command does from
           DOS.  For example, DIR \MIKE will list all the files in the \MIKE
           directory.  The problem most people have is detecting a directory
           which has no files in it.  For example:
               EXIST \MIKE\*.*
               JUMP.NO CREATE_DIRECTORY
           fails if no files are in the \MIKE directory.  Use this command
           instead:
               EXIST \MIKE*.
               JUMP.NO CREATE_DIRECTORY

           This command will work whether or not there are files in the
           \MIKE directory.  The only possible way to this will return the
           wrong answer is if there is a file named "MIKE" with no extension
           in the root directory.

