boo2pdf
=======

*WARNING: This program is a kludge :)*

There's an web service version available at http://ps-2.kev009.com/boo2pdf/
that's easier if you just need to convert some documents.

##Questions?
Contact Kevin Bowling, info at http://www.kev009.com/

##Running boo2pdf
The bulk of the app is in the Java code, using IBM's SoftCopy 
Reader(SCR) libraries to do the heavy lifting.  boo2pdf.java
is a small replacement main class that makes it easy to script against 
SCR.  It outputs really ugly HTML and .gif and .jpg images in SCR's 
preset cache directory (~/.IBM/)

##Example Run Script

_Note: This script requires Xvfb, xvfb-run, htmldoc_

Take a look at convert.sh for an example run script.  You will want to 
customize this to your system and take into account the notes below.
  
This script takes two parameters: `<name>.boo` `<name>`. `<name>` is the 
root file name.  It will output an intermediate `<name>.html` and then 
`<name>.pdf` once htmldoc is run.

## Notes
This repo is Linux only.  By using the Windows SCR and editing 
boo2pdf.java to load the correct .dll files (in place of the .so files) 
it is possible to get the same effect on Windows.  You might want to use 
Cygwin, PowerShell, Perl, or similar for your run script.

There are a lot of things to be aware of:
* Only one instance can run at a time due to the paths SCR assumes
 - I use lock files to ensure this in my run scripts
* SCR creates a Swing JFrame (GUI) and assumes it is present for most 
  methods.  I used Xvfb to essentially pipe the graphics to null.
* Classpath must be set when running
* LD_LIBRARY_PATH must be set to sys/ for native libraries
* In my run scripts, I clean up after the PDF is generated, removing the 
  lock file and .html.
* The Linux SCR does not support some of the early graphics formats.  
  Use the IBM TransMogrifier program (in transmogrifier/) to preprocess 
  older BookManager files.  It *runs* in wine on Linux, but the output 
  is hit or miss and many images invalid.  Best to preprocess on Windows.

##Build Instructions

```
cd src
javac -cp ../sys/hlccommon.jar boo2pdf.java
mv boo2pdf.class ../bin/
```

##Patches or help with a C/C++ port welcome.
We'd need docs or reversing of the file formats.
