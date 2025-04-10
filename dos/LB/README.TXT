        Low Bitrate Packer and Player
        -----------------------------

     This package is distributed as shareware. Detailed
information about how to register is in the file
register.txt. To get last version & other info see
LBplay home page at: http://www.inp.nsk.su/~shmunk/

Features
--------

- lossy algorithm to pack various sounds;
- ability to pack different formats of sound files:
  8bit/16bit/u-law coded,
  raw/wav/avr/au/aiff/snd/smp/iff/voc plain files,
  xm/stm/mod/s3m modules;
- both DOS and Win95/NT versions of players;
- an easy way to add new formats (through .ini file);
- different compression ratios with different quality
  lossing;
- playing to Sound Blaster, SBPro, covox, stereo covox,
  internal speaker (DOS version player);
- 9-band equalizer;
- seek operation support
- no FPU used


Disadvantages
-------------

- lossy algorithm;
- slow packing speed (about 25 seconds per one second
  of sound on 486SX80);
- player can play only plain files (raw/wav/au/...).
  For files with sequence information (s3m/mod/...) only
  images of samples will be played. When unpacking to
  file all will be correct.
- unregistered version of LBPack don't support stereo
  files;
- unregistered version of LBPack is limited to pack no
  more then 2,500,000 samples for per file (about 2
  minutes for 22050Hz sampling rate).

Requirements
------------

     System contains three program: LBPack, LBPlay and
LBWin. To use this package you must have at least 386SX.
No floating point arithmetics is used. A bit of VGA
graphics used when playing to sound devices with LBPlay,
so VGA adapter needed when playing.


LBPack
------

     With LBPack.exe you may pack various sounds into
small files. LBPack use lossy compression scheme. You
may choose one of 7 levels of archiving which gives you
different quality and compression ratio. By default
level 3 used. But you can change them by using -l#
switch (# - is a number from 0 to 6). Unregistered
version have full features of registered, except
possibility to pack stereo files and limitation to
2,500,000 samples per one file. Here is a
table of compression ratios:

旼컴컴컴컫컴컴컴컴컴컴컴컴컴컫컴컴컴컴컴컴컴컴컴컴쩡컴컴컴컴컴컴컴컴�
� Switch � Compression ratio � Bitrate (kbit/sec) � Comment         �
쳐컴컴컴컵컴컴컴컴컴컴컴컴컴컵컴컴컴컴컴컴컴컴컴컴탠컴컴컴컴컴컴컴컴�
� -l0    �     59.33         �       2.9          � Dirty sound     �
� -l1    �     26.78         �       6.6          �                 �
� -l2    �     15.42         �       11.4         �                 �
� -l3    �      9.22         �       19           � Default level   �
� -l4    �      7.18         �       25           �                 �
� -l5    �      4.31         �       41           �                 �
� -l6    �      2.47         �       71           � Highest quality �
읕컴컴컴컨컴컴컴컴컴컴컴컴컴컨컴컴컴컴컴컴컴컴컴컴좔컴컴컴컴컴컴컴컴�

Test was done with 22kHz, mono, 8-bit file.

     LBPack uses lbpack.ini file to recognize different
formats of sound files. lbpack.ini file divided into
several sections, which names are equals to file
extensions. First, packer will try section with name
equal to extension of packed file. If file extension
isn't correct, attempt will be done with other sections.
A brief description of language (some sort of script),
may by found in lbpack.ini.

     LBPack process only sound samples, founded in file.
All other information (for example sequence information
in .MOD files) will be packed to output file using
simple loseless algorithm.


Examples:

pack file mysound.wav to mysound.lb using default
compression level:

     lbpack mysound.wav

pack .au file with maximum compression but worse
quality:

     lbpack speech.au spch.lb -l0


LBPlay for DOS
--------------

     LBPlay allows you to play files packed with LBPack
or unpack them into original formats, or .wav/.au
formats.

Playing to sound devices

     In DOS version only 8-bit devices are supported
(SB/SBPro/StereoCovox). Also internal speaker is
supported. Warning: Playing to speaker or covox very
intensively uses system timer and in/out processor
commands. When playing to this devices clean boot
highly recommended.

     Some graphics will appear on screen when program
try to play sound. You may control output volume and
equalizer gain. Also you may adjust playing position
using lift on the bottom of the screen using mouse or
keyboard. Just click left mouse button on a lift you
want to change.
Keyboard:
          ->  and   <-  to change playing position;
          -   and   +   for left channel volume;
          [   and   ]   for right channel volume;
          1   and   q   for first equalizer band;
          ...........
          9   and   o   for last equalizer band.


Examples:

playing to SB:
        lbplay instr -b

unpacking to file:
        lbplay instr

unpacking to file with different name using max quality algorithm:
        lbplay instr testfile.wav -rq

playing to internal speaker with some equalizing:
        lbplay exmpl.lb -s -m -v30,30,20,28,28,28,28,28,28,28,28

playing on slow machines with SB (output at 11kHz, mono):
        lbplay exmpl2 -r0 -m -b


LBPlay for Win95/NT (lbwin.exe)
-------------------------------
see lbwin.txt


How to contact
--------------

    You may e-mail your suggestions to shmunk@csd.inp.nsk.su
    Low Bitrate Player home page: http://www.inp.nsk.su/~shmunk/

    Information about cwsdpmi.exe (DPMI manager needed
for LBPack.exe) may be obtained by contacting author -
Charles W Sandmann:
sandmann@clio.rice.edu
