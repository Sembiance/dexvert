# Unsupported File Formats

The following 121 file formats are unsupported by dexvert.

They are still **identified** by dexvert, just not processed in any way.



## 3d (7)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
3d | [Cyber Studio/CAD-3D](http://fileformats.archiveteam.org/wiki/CAD-3D) | .3d2 .3d | [14 sample files](https://telparia.com/fileFormatSamples/3d/cyberStudioCAD3D/)
3d | [IFF TDDD 3-D Render Document](http://fileformats.archiveteam.org/wiki/TDDD) | .tdd .cel .obj | [18 sample files](https://telparia.com/fileFormatSamples/3d/iffTDDD/) - A 3D rendering file format. Some of these files may have been created by "Impulse 3D" I've never bothered trying to convert or render these into anything else
3d | Polyfilm 3D Model | .3d | [8 sample files](https://telparia.com/fileFormatSamples/3d/polyfilm/)
3d | [POV-Ray Scene](http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description) | .pov | [1 sample file](https://telparia.com/fileFormatSamples/3d/povRay/)
3d | Sculpt 3D Scene | .scene | [2 sample files](https://telparia.com/fileFormatSamples/3d/sculpt3DScene/) - A 3D rendering file format. I didn't bother investigating it.
3d | [SGI Yet Another Object Description Language](http://fileformats.archiveteam.org/wiki/SGI_YAODL) | .ydl | [3 sample files](https://telparia.com/fileFormatSamples/3d/ydl/)
3d | [Virtual Reality Modeling Language](http://fileformats.archiveteam.org/wiki/VRML) | .wrl .wrz | [1 sample file](https://telparia.com/fileFormatSamples/3d/vrml/) - A 3D rendering file format meant for the web.



## Archive (9)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
archive | [Anex86 PC98 Floppy Image](http://fileformats.archiveteam.org/wiki/Anex86_PC98_floppy_image) | .fdi | [12 sample files](https://telparia.com/fileFormatSamples/archive/anex86FDI/) - The DiskExplorer/editdisk program is supposed to read these, but it fails on my sample files. Removing the 4k header and attempting to mount the raw image fails. Likely because of a disk format unique to PC98. I was able to extract the files by creating a HDD image with anex86 and formatting it by following: http://www.retroprograms.com/mirrors/Protocatbert/protocat.htm After that I could run anex86 with dos6.2 in FDD #1 and the FDI image in FDD #2. Then hit Escape and at the DOS prompt I could COPY B:* C: Then I exited anex86 and then I was able to use wine editdisk.exe to open the HDD image, ctrl-a all the files and ctrl-e extract them. So I could automate this and support FDI extraction. But right now I just don't see the value in doing so.
archive | [Corel Thumbnails Archvie](http://fileformats.archiveteam.org/wiki/CorelDRAW) |  | [213 sample files](https://telparia.com/fileFormatSamples/archive/corelThumbnails/) - Contains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them. Even went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed. Sent an email to the libcdr creators, to see if they know of any info on the format, but never heard back.
archive | IFF LIST File |  | [15 sample files](https://telparia.com/fileFormatSamples/archive/iffLIST/) - The IFF LIST files contain 'shared' entries that are used for all chunks in the remainder of the file. In theory I could parse this file, and "extract" out by creating seperate files for each major FORM entry inside, making sure to also copy into these files the 'shared' entries, adjusting the resulting FORM lengths as needed. Couldn't find any real documentation on the LIST/SSETPROP format. See: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF
archive | [InstallShield Installer Archive](http://fileformats.archiveteam.org/wiki/InstallShield_installer_archive) | .ex_ | [4 sample files](https://telparia.com/fileFormatSamples/archive/installShieldInstallerArchive/)
archive | [Macromedia Director Compiled](http://fileformats.archiveteam.org/wiki/Shockwave_(Director)) | .dcr | [6 sample files](https://telparia.com/fileFormatSamples/archive/directorCompiled/)
archive | Pax Archive | .pax | [4 sample files](https://telparia.com/fileFormatSamples/archive/paxArchive/) - Used in Atari ST program GEM-View
archive | [TED5 Archive](http://www.shikadi.net/moddingwiki/TED5) | .wl1 .ck4 .ck6 | [4 sample files](https://telparia.com/fileFormatSamples/archive/ted5Archive/) - An archive format created by TED5. Used for games like Commander Keen. The format is detailed on the wiki link above, so in theory I could create an extractor for it.
archive | Unix Archive - Old | .a | 
archive | [Viacom New Media Sprite Archive](http://www.shikadi.net/moddingwiki/Viacom_New_Media_Graphics_File_Format) | .vnm .000 | [49 sample files](https://telparia.com/fileFormatSamples/archive/viacomNewMedia/) - An obscure format that packs multiple bitmaps and sprites into a single archive. Found the following two projects that extract them: https://github.com/jmcclell/vnmgf-exporter Sadly neither one can correctly process/extract the VNM files I encountered. The github link is much closer and is in modern Go.



## Audio (9)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
audio | [AdLib Instrument Bank](http://fileformats.archiveteam.org/wiki/AdLib_instrument_bank) | .bnk | [3 sample files](https://telparia.com/fileFormatSamples/audio/adLibInstrumentBank/) - These .bnk files include sounds/instruments used by adlib ROL/SNG/SX files to make music. Technically the sounds could be extracted, maybe with 'Bank Manager' for DOS, but meh. Awave Studio claims to support these, but under version 7 I couldn't get them to load.
audio | Aegis Sonix Instrument | .instr | [19 sample files](https://telparia.com/fileFormatSamples/audio/sonixInstrument/) - The .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic
audio | [Creative Music System File](http://fileformats.archiveteam.org/wiki/CMS_(Creative_Music_System)) | .cms | [59 sample files](https://telparia.com/fileFormatSamples/audio/cms/) - Creative Music System. Couldn't locate any information on the file format itself, nor can I find any 'converters' for it. Only way to play them is within DOSBOX by setting this in the DOSBOX config: [sblaster] sbtype  = gb sbbase  = 220 irq     = 7 dma     = 1 hdma    = 5 sbmixer = true oplmode = cms oplemu  = default oplrate = 22050 Then going into CMSPLAY, running CMSDRV.COM and then PLAYER.EXE However that just plays the file, on an infinite loop, in real time. So while in theory I could maybe make a virtual WAV sound driver under linux and then have DOSBOX play to that driver and then record the music that way, I'd have to wait for the song to play in real time and there is no info on how long the song is
audio | [DataShow Sound File](http://www.amateur-invest.com/us_datashow.htm) | .snd | [1 sample file](https://telparia.com/fileFormatSamples/audio/dataShowSound/) - The single sample file I have is a simple text file on how to generate the sound. Probably wouldn't be too hard to create a converter for it. But it's a pretty obscure format, so probably not worth investing any time into it.
audio | [Inverse Frequency Sound Format](http://fileformats.archiveteam.org/wiki/Inverse_Frequency_Sound_format) |  | [3 sample files](https://telparia.com/fileFormatSamples/audio/inverseFrequency/) - Used in various APOGEE games like commander keen. Didn't look that hard for a player/converter.
audio | [Music Studio Sound](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .snd | [3 sample files](https://telparia.com/fileFormatSamples/audio/musicStudioSound/)
audio | [Quattro Pro Sound File](http://fileformats.archiveteam.org/wiki/Quattro_Pro) | .snd | [7 sample files](https://telparia.com/fileFormatSamples/audio/quattroProSound/) - Quattro Pro 3.0 allowed creation of slide shows which could include sounds. Couldn't locate any further information on these files except that they might be soundblaster compataible. Couldn't find anything to play them.
audio | Sonix Sound Sample | .ss | [18 sample files](https://telparia.com/fileFormatSamples/audio/sonixSoundSample/) - The .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic
audio | [SoundFont 1.0](http://fileformats.archiveteam.org/wiki/SoundFont_1.0) | .sbk | [1 sample file](https://telparia.com/fileFormatSamples/audio/soundFont1/) - Awave Studio can technically convert these, but 99.9% of all SBK SoundFond 1 files just contain meta info that points to a samples in ROM, thus there isn't anything really to convert.



## Document (9)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
document | [Amiga IFF Catalog](http://fileformats.archiveteam.org/wiki/IFF) | .catalog | [11 sample files](https://telparia.com/fileFormatSamples/document/iffCTLG/) - Contains strings used by programs. Not currently enabled as my parser isn't quite right and I don't feel like debugging it more.
document | [Calamus Document](http://fileformats.archiveteam.org/wiki/Calamus) | .cdk | [12 sample files](https://telparia.com/fileFormatSamples/document/calamusDocument/)
document | Clarion Database File | .dat | [49 sample files](https://telparia.com/fileFormatSamples/document/clarionDatabase/) - Did a Google search, couldn't find anything about it. unoconv didn't do anything with it either.
document | [Envision Publisher Document](http://fileformats.archiveteam.org/wiki/Envision_Publisher) | .evp .evt | [5 sample files](https://telparia.com/fileFormatSamples/document/envisionPublisherDoc/) - Envision Publisher for MSDOS doesn't have an "Export" option. I could figure out how to 'print to a file' or I could set up DOSBOX PDF Printer emulation: superuser.com/questions/270457/how-can-i-print-with-dosbox
document | [Help Librarian Help File](http://fileformats.archiveteam.org/wiki/Help_Librarian) | .hlp | [5 sample files](https://telparia.com/fileFormatSamples/document/helpLibrarian/) - Help Librarian files. No information about them could be found anywhere.
document | InfoFile Database File | .flr | [7 sample files](https://telparia.com/fileFormatSamples/document/infoFile/) - Did a very quick Google search and didn't turn up any sort of converter program. This was a very obscure amiga database program.
document | [Internet Message Format](http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format) | .eml .msg | [1 sample file](https://telparia.com/fileFormatSamples/document/imf/) - With several RFC files describing the format, uou'd think this would be straight forward to parse, but it's a total nightmare. I had spent some time looking for a good program to parse it, and failed. I spent more time trying to code my own that would output JSON, but there are just a ton of edge cases and I gave up. In addition to the website link above, more details here: https://mailformat.dan.info/
document | [PC-File](http://fileformats.archiveteam.org/wiki/PC-FILE) | .dbf .rep | [3 sample files](https://telparia.com/fileFormatSamples/document/pcFile/) - Was a pretty popular database program back in the day. Didn't really dig into what converters might be possible.
document | Timeworks Publisher/Publish It! | .dtp | [7 sample files](https://telparia.com/fileFormatSamples/document/timeworksPublisher/) - All I could find on it: https://sparcie.wordpress.com/2018/01/22/open-access-for-dos/



## Executable (10)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
executable | AmigaOS Executable |  | 
executable | Atari Control Panel Extension Module |  | [12 sample files](https://telparia.com/fileFormatSamples/executable/atariCPX/)
executable | Atari Executable | .xex | [4 sample files](https://telparia.com/fileFormatSamples/executable/xex/)
executable | Atari ST Executable |  | [11 sample files](https://telparia.com/fileFormatSamples/executable/atariSTExe/)
executable | ELF Executable |  | 
executable | Linux OMAGIC Executable |  | 
executable | MacOS Executable |  | 
executable | MS-DOS COM Executable | .com .c0m | [4 sample files](https://telparia.com/fileFormatSamples/executable/com/)
executable | MS-DOS Driver | .sys .drv | 
executable | ZBASIC | .bas | [6 sample files](https://telparia.com/fileFormatSamples/executable/zbasic/)



## Font (6)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
font | [Borland Graphics Font](http://fileformats.archiveteam.org/wiki/CHR_(Borland_font)) | .chr .bgi | No sample files yet.
font | [Calamus Font](http://fileformats.archiveteam.org/wiki/Calamus_Font) | .cfn | [10 sample files](https://telparia.com/fileFormatSamples/font/calamusFont/)
font | [Envision Publisher Font](http://fileformats.archiveteam.org/wiki/Envision_Publisher) | .svf | [3 sample files](https://telparia.com/fileFormatSamples/font/envisionPublisherFont/) - Font file for the MSDOS program Envsion Publisher. Fontforge doesn't handle it and I didn't bother trying to convert further.
font | LaserJet Soft Font | .sfl .sfp .sft | No sample files yet.
font | LinkWay Font | .fmf | No sample files yet.
font | [The Draw Font](http://fileformats.archiveteam.org/wiki/TheDraw_font) | .tdf | [1 sample file](https://telparia.com/fileFormatSamples/font/theDrawFont/) - Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it



## Image (7)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
image | BBC Display RAM Dump |  | [1 sample file](https://telparia.com/fileFormatSamples/image/bbcDisplayRAM/) - While supported, due to no extension and no magic, it's impossible to accurately detect. Abydos will convert invalid files and and produce a garbled image, thus not able to just try a conversion and see.
image | [Facsimile image FORM](http://fileformats.archiveteam.org/wiki/FAXX) | .faxx .fax | [3 sample files](https://telparia.com/fileFormatSamples/image/faxx/) - No known converter.
image | [GEM Vector Metafile](http://fileformats.archiveteam.org/wiki/GEM_VDI_Metafile) | .gem .gdi | [16 sample files](https://telparia.com/fileFormatSamples/image/gemMetafile/) - Vector file format that could be converted into SVG. abydos is working on adding support for this format.
image | [MLDF](http://fileformats.archiveteam.org/wiki/MLDF) | .mld | [32 sample files](https://telparia.com/fileFormatSamples/image/mldf/) - It's probably an image format. IFF format FORM with MLDF BMHD. Could not locate any info online about it and I didn't investigate further.
image | NeoPaint Pattern | .pat | While identified via magic as a "NeoPaint Palette" they appear to be "patterns" used as stamps in the MSDOS Neopaint program. Short of reverse engineering it, in theory dexvert could convert these to images by opening up DOS Neopaint, selecting the pattern, stamping it or filling a canvas with it and saving the image. Don't plan on bothing to actually do that though, it's a relatively obscure program and file format.
image | [Remote Imaging Protocol Script](http://fileformats.archiveteam.org/wiki/RIPscrip) | .rip | [15 sample files](https://telparia.com/fileFormatSamples/image/ripScrip/) - A vector based format. Would love to convert to SVG. This project started support for that: https://github.com/cgorringe/RIPtermJS I could extend that project to make a true ripscrip-to-svg node based converter. Other tools: http://archives.thebbs.org/ra109a.htm
image | [Teletext](http://snisurset.net/code/abydos/teletext.html) | .bin | [2 sample files](https://telparia.com/fileFormatSamples/image/teletext/) - Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on.



## Music (4)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
music | [DigiTrekker](http://fileformats.archiveteam.org/wiki/DigiTrekker_module) | .dtm | [4 sample files](https://telparia.com/fileFormatSamples/music/digiTrekker/) - DigiTrekker for MSDOS can play these and convert to a 'SND' format, but only in 'realtime' and I couldn't determine the format of the output SND. milkytracker claims support for this format, but I couldn't get it to play any DTM files.
music | [Microdeal Quartet Module](http://fileformats.archiveteam.org/wiki/4v) | .4v | [9 sample files](https://telparia.com/fileFormatSamples/music/quartetModule/)
music | [Music Studio Song](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .sng | [10 sample files](https://telparia.com/fileFormatSamples/music/musicStudioSong/) - In theory the Atari program 'MIDI Music Maker' can convert .sng files to .midi
music | [Slight Atari Player](http://fileformats.archiveteam.org/wiki/Slight_Atari_Player) | .sap | A bit more modern of a format, haven't really looked into how best to support it yet.



## Other (55)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
other | Adobe Type Manager Font Information | .inf | 
other | Alchemy Mindworks Resource | .res | 
other | Amiga Action Replay 3 Freeze File |  | 
other | Amiga ADF BlkDev File | .blkdev | 
other | Amiga ADF Bootcode | .bootcode | 
other | Amiga ADF XDF Meta | .xdfmeta | 
other | Amiga CLI-Mate Directory Index File |  | 
other | Amiga IFF DTYP |  | 
other | Amiga Preferences | .prefs | 
other | Amos Amal Animation Bank | .abk | 
other | AMOS Datas Bank | .abk | 
other | ASCII Font Metrics | .afm | 
other | Asymetrix ToolBook File | .tbk | 
other | Atari GEM OBM File | .obm | [10 sample files](https://telparia.com/fileFormatSamples/other/atariGEMOBM/)
other | Audio Interface Library 3 Digital audio driver | .dig | 
other | Audio Interface Library 3 Music/MIDI driver | .mdi | 
other | Borland Graphics Interface Driver | .bgi | 
other | Borland Turbo C Project | .prj | 
other | CHAOSultdGEM Parameters | .chs | [8 sample files](https://telparia.com/fileFormatSamples/other/chaosultdGEMParameters/)
other | Chemview Animation Data | .d | 
other | Corncob 3D Data File | .cct | 
other | Creative Signal Processor microcode | .csp | 
other | Cygnus Editor Default Settings |  | 
other | Cygnus Editor Macros |  | 
other | dBase Index File | .ntx | 
other | Emacs Compiled Lisp | .elc | [8 sample files](https://telparia.com/fileFormatSamples/other/emacsCompiledLisp/) - Could decompile it with: https://github.com/rocky/elisp-decompile
other | FoxPro Memo File | .fpt | 
other | Full Tilt Pinball Data | .dat | 
other | [Hewlett-Packard Graphics Language](http://fileformats.archiveteam.org/wiki/HPGL) | .hpgl | [5 sample files](https://telparia.com/fileFormatSamples/other/hpgl/) - Sometimes used for graphics, sometimes used to control plotters and other machines. I tried to compile this but it's ancient and failed: http://ftp.funet.fi/index/graphics/packages/hpgl2ps/hpgl2ps.tar.Z Quick searches didn't turn up any other 'easy' to grab and use converters, so punt on this for now.
other | ICC Color Profile | .icc | 
other | [InstallShield HDR](http://fileformats.archiveteam.org/wiki/InstallShield_CAB) | .hdr | HDR files are meta data for installShieldCAB files and are not processed directly.
other | InstallShield Script | .ins | 
other | Java Class File | .class | [4 sample files](https://telparia.com/fileFormatSamples/other/javaClass/)
other | [MacBinary](http://fileformats.archiveteam.org/wiki/MacBinary) | .bin | 
other | Microsoft Visual C Library | .lib | 
other | Microsoft Windows Help File Content | .cnt | Just a table of contents as to what's in the corresponding .hlp file. Not useful.
other | Microsoft Windows Program Information File | .pif | 
other | Miles Sound System Driver | .adv | 
other | NeoPaint Palette | .pal | 
other | NeoPaint Printer Driver | .prd | 
other | Norton Change Directory Info | .ncd | 
other | OLB Library |  | [7 sample files](https://telparia.com/fileFormatSamples/other/olbLib/)
other | Pascal Compiled Unit | .tpu .ppu | 
other | Polyfilm Preferences | .prf | 
other | Printer Font Metrics | .pfm | 
other | RIFF MSFX File | .sfx | Just contains meta info about a given soundeffect usually distributed alongside it as a .wav
other | RIFF MxSt File | .si | References to other files, seems to be meta info only. Only info I could find, failed to process: https://github.com/dutchcoders/extract-riff
other | RIFF STYL File | .par | References a font for mac and windows and includes some text in a TEXT chunk
other | Startrekker Module Info | .nt | 
other | Turbo Basic Chain module | .tbc | 
other | Turbo C Context File | .dsk | 
other | Turbo Pascal Overlay | .ovr | 
other | Visual Basic Extension | .vbx | 
other | WordPerfect keyboard file | .wpk | 
other | WordPerfect Macro File | .wpm | 



## Rom (1)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
rom | Game Boy ROM | .gb .gbc | 



## Video (4)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
video | [Deluxe Video](http://fileformats.archiveteam.org/wiki/VDEO) |  | [1 sample file](https://telparia.com/fileFormatSamples/video/deluxeVideo/) - Couldn't find a converter for it. Could fire up an amiga with deluxe video program from Electronic Arts.
video | [IFF VAXL](http://fileformats.archiveteam.org/wiki/VAXL) | .vaxl | [15 sample files](https://telparia.com/fileFormatSamples/video/iffVAXL/) - Could only find this potential viewer, but no download link: https://www.ultimateamiga.com/index.php?topic=9605.0
video | RIFF ANIM | .paf | [9 sample files](https://telparia.com/fileFormatSamples/video/riffANIM/) - Couldn't find any evidence of this out in the public. Could very well be a proprietary format
video | [RIFF Multimedia Movie](http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie) | .mmm | [14 sample files](https://telparia.com/fileFormatSamples/video/riffMultimediaMovie/) - Couldn't find a converter or player for it

