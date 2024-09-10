    LZA v1.01: CHIEF'S LZSS ARCHIVER
    --------------------------------
    (c)January 1999, Dr Abimbola Olowofoyeku (The African Chief)

    Homepage: http://ourworld.compuserve.com/homepages/African_Chief/


    Introduction
    ------------
    Welcome to LZA - the African Chief's LZSS and Huffman archiver.
    This package provides yet another archive format for PCs. However, the
    advantage of this package is that it is FREE. Not only is it free, the
    full (Borland Pascal/Delphi/Virtual Pascal) source code to the compression 
    engines used in the package is available for FREE from my homepage.
    There are two types of compression used in the package (a "fast" mode,
    using LZSS compression, and a "maximum" mode, using Huffman compression).
    When using the "Maximum Compression" option, the compression ratio is as
    good as ZIP's "deflate" method, but there is a slight speed loss.


    FILES IN THE PACKAGE (; !and the compilers used to produce them!)
    -----------------------------------------------------------------
    lza.exe         - Chief's LZ Archiver (Win32 GUI Program; !Delphi 3.0 !)
    lza32.exe       - Chief's LZ Archiver (Win32 Console program; !Delphi 2.0 !)
    lza16.exe       - Chief's LZ Archiver (Win16 non-gui "CRT" program; !Borland Pascal 7.0 !)
    lzados.exe      - Chief's LZ Archiver (16-bit DOS Real Mode program; !Borland Pascal 7.0 !)
    lzadpmi.exe     - Chief's LZ Archiver (16-bit DOS Protected Mode (DPMI) program; !Borland Pascal 7.0 !)

    lzstub16.exe    - Self-Extracting EXE stub (Win16 GUI program; !Borland Pascal 7.0 (OWL) !)
    lzstub32.exe    - Self-Extracting EXE stub (Win32 GUI program; !Virtual Pascal 2.0 (OWL) !)
    stub32.exe      - Self-Extracting EXE stub (Win32 Console mode program; !Virtual Pascal 2.0 !)
    stubdos.exe     - Self-Extracting EXE stub (16-bit DOS Real Mode program; !Borland Pascal 7.0 !)
    stubdpmi.exe    - Self-Extracting EXE stub (16-bit DOS Protected Mode (DPMI) program; !Borland Pascal 7.0 !)

    rtm.exe         - DPMI loader for the 16-bit DOS Protected Mode programs
    file_id.diz     - information file for BBSes and internet sites
    readme.txt      - this file
    history.txt	    - history file


    NOTE: in order to use any of the DPMI programs, you need to have RTM.EXE
          in a directory specified in the "path"


    Features
    --------
    * single file compression and decompression
    * archive compression and decompression
    * self-extracting archive ("SFX") support - several "STUB" programs supplied
    * password protection for archives
    * disk spanning
    * any file can be marked as an archive comment file
    * up to 8,192 files in each archive
    * DOS, DOS DPMI, Win16, and Win32 executables
    * CRC checking of files in archives
    * viewing the contents of archives
    * stores version information from Windows binaries (the Windows versions only)
    * long filenames support under Windows 9x, and Windows NT
    * optionally stores and restores directory paths
    * this archive format is now being supported by some 3rd party programs!
    * uses patent-free LZSS (LZ77) and Huffman compression algorithms
    * free source code to the compression algorithms
    * fast compression or maximum compression
    * maximum compression is as good as ZIP's "deflation"


    Usage
    -----
    Most of the programs are command line programs, which operate on the basis
    of switches passed on to them.

    The Syntax is:  LZAxx <archive1/file1> [filespecs/files/file2] [Switches]
                    ---------------------------------------------------------

    The supported switches are:
    /U
    /A
    /R[1]
    /LST:listfile
    /SFX <SFX-Stub>
    /C[0,1]
    /SPAN [/DS:<size>] 
    /XA
    /X[/CRC+ [/F:file_specifications [/N:ID]]]
    /R-
    /V
    /S:password
    /Comment

    Legend
    -------
    No switch= Compress a single file (File1) to File2
              e.g.  LZA32 BIG.EXE SMALL.LZZ

    /U       = Decompress a single file (File1) to File2
              e.g.  LZA32 SMALL.LZZ BIG.EXE /U

    /A       = Compress and Archive the files (filespecs/files) into Archive (archive1)
              (Maximum of 8,192 files in Archives)
              e.g.  LZA32 TEMP.LZA C:\TEMP\*.* /A
                    LZA32 TEMP.LZA f1.exe+f2.exe+f3.bin+f4.hlp /A

    /LST:    = the files to be archived are in the specified LIST file
                    LZA32 TEMP.LZA /LST:File2.LST /A

    /R       = Recurse through directory structure (for archives)
              e.g.  LZA32 C:\TEMP\DATA.LZA C:\DATA\*.* /A /R

    /R1      = Recurse into 1st level directories (for archives)
              e.g.  LZA32 TEMP.LZA C:\TEMP\*.* /A /R1

    /S:      = Supply a password for the archive
              e.g.  LZA32 TEMP.LZA *.EXE /A /R /S:Freddy_Smith

    /SFX     = Archive files to a self-extracting .EXE, supplying the
               executable stub for the self-extracting archive
              e.g.  LZA32 TEMP.EXE C:\TEMP\*.* /SFX C:\LZ\STUB32.EXE /R


              Note: several sample SFX stubs are provided in this package;

              For DOS usage (and for DOS sessions under OS/2 or DOSEMU under
              Linux), use stubdpmi.exe. 

              For 16-bit Windows, use lzstub16.exe. For 32-bit Windows, use 
              lzstub32.exe or stub32.exe (depending on whether you want a GUI or
              console mode SFX file). 

              Stubdos.exe should only be used if *all* of these conditions exist;
                 a. (small) size is of the essence
                 b. files in the archives do not have long names
                 c. there are less than 2048 files in the archives
                 d. there is plenty of free DOS memory (i.e., more than
                    580k)
                 e. there is no need for Windows version information

              It is not recommended to use stubdos.exe at all. Its only
              advantage is its small size. But it does have many limitations.

    /C[0,1]  = Use No-compression/Maximum-compression (slow!) for archives
               (the default is to use normal (fast) compression, but the
               fast compression ratio is not as tight as the maximum
               compression ration).

              e.g.  LZA32 TEMP.LZA C:\TEMP\*.* /A /C1
                   (= use maximum compression)

                    LZA32 TEMP.LZA C:\TEMP\*.* /A /C0
                   (= use no compression; just store the files in the
                   archive)


    /SPAN    = Create an archive that spans across (floppy) disks
              e.g.  LZA32 A:\TEMP.LZA C:\TEMP\*.* /A /SPAN
              e.g.  LZA32 A:\TEMP.EXE C:\TEMP\*.* /SFX C:\LZ\STUB.EXE /SPAN /R 
		
	     NOTE: spanning can only work on the root directory of a (floppy)
                   disk. Do not attempt to create spanned archives anywhere
                   other than the root directory of a floppy disk.

    /DS:     = Set the size (in bytes) of the (floppy) disks for spanned archive
              e.g.  LZA32 A:\TEMP.LZA C:\TEMP\*.* /A /SPAN /DS:728000

    /X       = Decompress an LZ Archive into directory
              e.g.  LZA32 TEMP.LZA C:\TEMP /X

    /X /R-   = Decompress an LZ Archive - but don't restore the directory
               structure in the archive
              e.g.  LZA32 TEMP.LZA C:\TEMP /X /R-

    /X /CRC+ = Decompress an LZ Archive, and perform CRC checks on the files
              e.g.  LZA32 TEMP.LZA C:\TEMP /X /CRC+

    /XA      = Extract the LZ archive (file2) from SFX archive (file1)
              e.g.  LZA32 TEST.EXE TEST.LZA /XA

    /V       = Show contents of an LZ Archive
              e.g.  LZA32 TEMP.LZA /V

    /F:      = Extract or View only these file specifications
              e.g.  LZA32 TEMP.LZA /V /F:*.txt
                    LZA32 TEMP.LZA C:\TEMP\LZA /X /F:*.exe

    /N:      = Process only the file with the specified numeric ID
  	      e.g.  LZA32 TEMP.LZA /V /N:16

    /COMMENT = Mark the specified filed as an archive comment file
              e.g.  LZA32 MYPIC.BMP /COMMENT



    LICENCE
    -------
    This package is released as FREEWARE. You may use and copy it freely.
    You may also distribute the package freely to/via FTP sites, Bulletin
    Boards, Shareware/Freeware/Public Domain archives, CD-ROMS, Magazine
    Cover Disks and CD-ROMS, etc. Shareware/Freeware disk vendors also
    may also freely freely distribute the package.

    Distribution of this package in any form is subject to *ALL* the
    following conditions;

       [1] ALL the files which I have supplied must be included,

       and

       [2] NO ATTEMPT must be made to modify or alter ANYTHING in any of
           the files,

       and

       [3] You must not charge ANYTHING for distributing this package (disk
           vendors may charge a reasonable fee, not exceeding $5 (US) - or
           equivalent - for media and duplication).


    Please note the disclaimers below.

    DISCLAIMER
    ----------
    I DO NOT WARANTEE ANYTHING CONCERNING ANY OF THE PROGRAMS OR FILES WHICH
    MAKE UP "CHIEF'S LZ ARCHIVER". I ACCEPT NO RESPONSIBILITY FOR ANY LOSS
    OR DAMAGE OF ANY KIND, INCLUDING, BUT NOT LIMITED TO, LOSSES OF A
    PHYSICAL, MENTAL, SOCIAL, FINANCIAL, MARITAL, OR OF WHATEVER NATURE,
    RESULTING FROM THE USE, OR THE PURPORTED USE OF CHIEF'S LZ ARCHIVER", OR
    ANY OF THE FILES IN THE PACKAGE, FOR ANY PURPOSE WHATSOEVER. I DO NOT
    EVEN WARANTEE THAT THE PROGRAMS WILL NOT KILL YOU.

    YOU USE CHIEF'S LZ ARCHIVER ENTIRELY AT YOUR OWN RISK, AND YOU SUPPLY IT
    TO YOUR CUSTOMERS, FRIENDS, FAMILY, ACQUAINTANCES, OR ENEMIES, ENTIRELY
    AT YOUR OWN RISK.

    IF THESE TERMS ARE NOT ACCEPTABLE TO YOU, THEN PLEASE DELETE ALL THE
    FILES FROM YOUR DISKS IMMEDIATELY AND PERMANENTLY.


    --------------------
    Dr. A. Olowofoyeku
    January 1999
    --------------------
    Homepage: http://ourworld.compuserve.com/homepages/African_Chief/

