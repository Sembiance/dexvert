Vibe coded by Claude

support/ — relocatable engine bundle for folioDatabase.py
=========================================================
folioDatabase.py extracts text from Folio .NFO infobases by driving the REAL
Folio engines shipped here.  Keep this folder next to folioDatabase.py; the two
relocate to any system as a pair (all paths are resolved relative to the script).

Contents
--------
  folio32/            32-bit Folio Views 4.2 engine (nfomgr4.dll + fcsrv3b/
                      fcsrv4b/nfosrv4 servers, filters, MSVCRT40 in WinSys/),
                      the built driver nfotext.exe, the riassv3.dll rights stub,
                      and <dll>.orig backups of the (reversible) gate patches.
  dos20/              Folio "PreVIEWS" 2.1 DOS engine (flrules.exe +
                      flrules_patched.exe) for DOS-era 2.0 infobases.
  folio_extract.sh    headless wine driver for the 4.2 engine.
  folio_dos_export.py headless dosbox driver for the 2.0 engine.
  folio_objconv.py    converts Folio's headerless bitmap objects to standard .bmp
                      (lossless header-prepend; real JPEG/GIF/WMF left as-is).
  folio_codec.py      pure-Python 3.1 fallback decoder (no external deps).
  nfotext.c           source for nfotext.exe (build via build_nfotext.sh, i686 mingw);
                      nfotext.exe <in.nfo> <out.txt> [<objdir>] -- text, plus embedded
                      objects (images) dumped AS-IS to <objdir> when given.
  build_nfotext.sh    rebuilds folio32/nfotext.exe from nfotext.c.
  riassv3_stub.c/.def source for the riassv3.dll rights stub.

Host prerequisites (install on the target machine; NOT bundled)
---------------------------------------------------------------
  * wine (32-bit)                          -> 4.x / 3.1 / 3.0 infobases
  * dosbox, xdotool, ImageMagick `import`,
    Xvfb                                   -> DOS-era 2.0 infobases
  * python3                                -> always
  * i686-w64-mingw32-gcc                   -> only to rebuild the riassv3 stub
                                              (a prebuilt riassv3.dll is included)

Isolation / parallel-safe: every run works in its OWN throwaway sandbox under
$TMPDIR (private HOME, private wine prefix bootstrapped fresh in ~3 s, private
Xvfb display, private temp/work dirs) and kills ONLY the wine/dosbox/Xvfb
processes it launched.  Your real $HOME is never touched, and many copies can run
in parallel against different infobases without interfering.  Keep TMPDIR
user-owned (the default /tmp/<random> from mktemp is fine; wine refuses a prefix
under a non-owned dir like bare /tmp).

Full format spec, the rights-gate details, and what the files contain (text +
embedded images/objects, with the object-API sequence) are in ../folioDatabase.txt.
