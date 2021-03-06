# Unsupported File Formats

The following 183 file formats are unsupported by dexvert.

They are still **identified** by dexvert, just not processed in any way.



## 3d (8)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
3d | [Cyber Studio/CAD-3D](http://fileformats.archiveteam.org/wiki/CAD-3D) | .3d2 .3d | [14 sample files](https://telparia.com/fileFormatSamples/3d/cyberStudioCAD3D/)
3d | [IFF TDDD 3-D Render Document](http://fileformats.archiveteam.org/wiki/TDDD) | .tdd .cel .obj | [18 sample files](https://telparia.com/fileFormatSamples/3d/iffTDDD/) - A 3D rendering file format. Some of these files may have been created by "Impulse 3D" I've never bothered trying to convert or render these into anything else
3d | [NorthCAD-3D](http://fileformats.archiveteam.org/wiki/SGI_YAODL) | .n3d | 
3d | Polyfilm 3D Model | .3d | [8 sample files](https://telparia.com/fileFormatSamples/3d/polyfilm/)
3d | [POV-Ray Scene](http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description) | .pov | [1 sample file](https://telparia.com/fileFormatSamples/3d/povRay/)
3d | Sculpt 3D Scene | .scene | [2 sample files](https://telparia.com/fileFormatSamples/3d/sculpt3DScene/) - A 3D rendering file format. I didn't bother investigating it.
3d | [SGI Yet Another Object Description Language](http://fileformats.archiveteam.org/wiki/SGI_YAODL) | .ydl | [3 sample files](https://telparia.com/fileFormatSamples/3d/ydl/)
3d | [Virtual Reality Modeling Language](http://fileformats.archiveteam.org/wiki/VRML) | .wrl .wrz | [1 sample file](https://telparia.com/fileFormatSamples/3d/vrml/) - A 3D rendering file format meant for the web.



## Archive (10)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
archive | [Anex86 PC98 Floppy Image](http://fileformats.archiveteam.org/wiki/Anex86_PC98_floppy_image) | .fdi | [12 sample files](https://telparia.com/fileFormatSamples/archive/anex86FDI/) - The DiskExplorer/editdisk program is supposed to read these, but it fails on my sample files. Removing the 4k header and attempting to mount the raw image fails. Likely because of a disk format unique to PC98. I was able to extract the files by creating a HDD image with anex86 and formatting it by following: http://www.retroprograms.com/mirrors/Protocatbert/protocat.htm After that I could run anex86 with dos6.2 in FDD #1 and the FDI image in FDD #2. Then hit Escape and at the DOS prompt I could COPY B:* C: Then I exited anex86 and then I was able to use wine editdisk.exe to open the HDD image, ctrl-a all the files and ctrl-e extract them. So I could automate this and support FDI extraction. But right now I just don't see the value in doing so.
archive | [Corel Thumbnails Archive](http://fileformats.archiveteam.org/wiki/CorelDRAW) |  | [213 sample files](https://telparia.com/fileFormatSamples/archive/corelThumbnails/) - Contains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them. Even went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed. Sent an email to the libcdr creators, to see if they know of any info on the format, but never heard back.
archive | FIZ Archive | .fiz | [8 sample files](https://telparia.com/fileFormatSamples/archive/fizArchive/) - Could not locate any info on this archive
archive | IFF LIST File |  | [15 sample files](https://telparia.com/fileFormatSamples/archive/iffLIST/) - The IFF LIST files contain 'shared' entries that are used for all chunks in the remainder of the file. In theory I could parse this file, and "extract" out by creating seperate files for each major FORM entry inside, making sure to also copy into these files the 'shared' entries, adjusting the resulting FORM lengths as needed. Couldn't find any real documentation on the LIST/SSETPROP format. See: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF
archive | [InstallShield Installer Archive](http://fileformats.archiveteam.org/wiki/InstallShield_installer_archive) | .ex_ | [4 sample files](https://telparia.com/fileFormatSamples/archive/installShieldInstallerArchive/)
archive | [Macromedia Director Compiled](http://fileformats.archiveteam.org/wiki/Shockwave_(Director)) | .dcr | [6 sample files](https://telparia.com/fileFormatSamples/archive/directorCompiled/)
archive | Pax Archive | .pax | [4 sample files](https://telparia.com/fileFormatSamples/archive/paxArchive/) - Used in Atari ST program GEM-View
archive | [TED5 Archive](http://www.shikadi.net/moddingwiki/TED5) | .wl1 .ck4 .ck6 | [4 sample files](https://telparia.com/fileFormatSamples/archive/ted5Archive/) - An archive format created by TED5. Used for games like Commander Keen. The format is detailed on the wiki link above, so in theory I could create an extractor for it.
archive | Unix Archive - Old | .a | 
archive | [Viacom New Media Sprite Archive](http://www.shikadi.net/moddingwiki/Viacom_New_Media_Graphics_File_Format) | .vnm .000 | [49 sample files](https://telparia.com/fileFormatSamples/archive/viacomNewMedia/) - An obscure format that packs multiple bitmaps and sprites into a single archive. Found the following two projects that extract them: https://github.com/jmcclell/vnmgf-exporter Sadly neither one can correctly process/extract the VNM files I encountered. The github link is much closer and is in modern Go.



## Audio (10)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
audio | [AdLib Instrument Bank](http://fileformats.archiveteam.org/wiki/AdLib_instrument_bank) | .bnk | [3 sample files](https://telparia.com/fileFormatSamples/audio/adLibInstrumentBank/) - These .bnk files include sounds/instruments used by adlib ROL/SNG/SX files to make music. Technically the sounds could be extracted, maybe with 'Bank Manager' for DOS, but meh. Awave Studio claims to support these, but under version 7 I couldn't get them to load.
audio | Aegis Sonix Instrument | .instr | [19 sample files](https://telparia.com/fileFormatSamples/audio/sonixInstrument/) - The .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic
audio | [Creative Labs Instrument Bank](http://fileformats.archiveteam.org/wiki/Instrument_Bank) | .ibk | [2 sample files](https://telparia.com/fileFormatSamples/audio/creativeLabsInstrumentBank/)
audio | [DataShow Sound File](http://www.amateur-invest.com/us_datashow.htm) | .snd | [1 sample file](https://telparia.com/fileFormatSamples/audio/dataShowSound/) - The single sample file I have is a simple text file on how to generate the sound. Probably wouldn't be too hard to create a converter for it. But it's a pretty obscure format, so probably not worth investing any time into it.
audio | [Inverse Frequency Sound Format](http://fileformats.archiveteam.org/wiki/Inverse_Frequency_Sound_format) |  | [3 sample files](https://telparia.com/fileFormatSamples/audio/inverseFrequency/) - Used in various APOGEE games like commander keen. Didn't look that hard for a player/converter.
audio | [Music Studio Sound](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .snd | [3 sample files](https://telparia.com/fileFormatSamples/audio/musicStudioSound/)
audio | [Quattro Pro Sound File](http://fileformats.archiveteam.org/wiki/Quattro_Pro) | .snd | [7 sample files](https://telparia.com/fileFormatSamples/audio/quattroProSound/) - Quattro Pro 3.0 allowed creation of slide shows which could include sounds. Couldn't locate any further information on these files except that they might be soundblaster compataible. Couldn't find anything to play them.
audio | Sonix Sound Sample | .ss | [18 sample files](https://telparia.com/fileFormatSamples/audio/sonixSoundSample/) - The .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic
audio | [Sound Blaster Instrument](http://fileformats.archiveteam.org/wiki/Sound_Blaster_Instrument) | .sbi | [10 sample files](https://telparia.com/fileFormatSamples/audio/soundBlasterInstrument/)
audio | [SoundFont 1.0](http://fileformats.archiveteam.org/wiki/SoundFont_1.0) | .sbk | [1 sample file](https://telparia.com/fileFormatSamples/audio/soundFont1/) - Awave Studio can technically convert these, but 99.9% of all SBK SoundFond 1 files just contain meta info that points to a samples in ROM, thus there isn't anything really to convert.



## Document (5)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
document | [Calamus Document](http://fileformats.archiveteam.org/wiki/Calamus) | .cdk | [12 sample files](https://telparia.com/fileFormatSamples/document/calamusDocument/)
document | Clarion Database File | .dat | [49 sample files](https://telparia.com/fileFormatSamples/document/clarionDatabase/) - Did a Google search, couldn't find anything about it. soffice didn't do anything with it either.
document | [Envision Publisher Document](http://fileformats.archiveteam.org/wiki/Envision_Publisher) | .evp .evt | [5 sample files](https://telparia.com/fileFormatSamples/document/envisionPublisherDoc/) - Envision Publisher for MSDOS doesn't have an "Export" option. I could figure out how to 'print to a file' or I could set up DOSBOX PDF Printer emulation: superuser.com/questions/270457/how-can-i-print-with-dosbox
document | [Internet Message Format](http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format) | .eml .msg | [1 sample file](https://telparia.com/fileFormatSamples/document/imf/) - With several RFC files describing the format, uou'd think this would be straight forward to parse, but it's a total nightmare. I had spent some time looking for a good program to parse it, and failed. I spent more time trying to code my own that would output JSON, but there are just a ton of edge cases and I gave up. In addition to the website link above, more details here: https://mailformat.dan.info/
document | [PC-File](http://fileformats.archiveteam.org/wiki/PC-FILE) | .dbf .rep | [3 sample files](https://telparia.com/fileFormatSamples/document/pcFile/) - Was a pretty popular database program back in the day. Didn't really dig into what converters might be possible.



## Executable (11)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
executable | AmigaOS Executable |  | 
executable | Atari Control Panel Extension Module | .cpx | [10 sample files](https://telparia.com/fileFormatSamples/executable/atariCPX/)
executable | Atari Executable | .xex | [4 sample files](https://telparia.com/fileFormatSamples/executable/xex/)
executable | Atari ST Executable |  | [11 sample files](https://telparia.com/fileFormatSamples/executable/atariSTExe/)
executable | ELF Executable |  | 
executable | FM-TownsOS App | .exp | [9 sample files](https://telparia.com/fileFormatSamples/executable/fmTownsOSApp/)
executable | Linux OMAGIC Executable |  | 
executable | MS-DOS COM Executable | .com .c0m | [4 sample files](https://telparia.com/fileFormatSamples/executable/com/)
executable | MS-DOS Driver | .sys .drv | 
executable | RISC OS Executable |  | 
executable | ZBASIC | .bas | [6 sample files](https://telparia.com/fileFormatSamples/executable/zbasic/)



## Font (13)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
font | Avery Font | .ff1 | 
font | Banner Mania Font | .fnt | [19 sample files](https://telparia.com/fileFormatSamples/font/bannerManiaFont/)
font | Borland Graphics Font | .chr .bgi | 
font | Bradford Font | .bf2 | 
font | Calamus Font | .cfn | [10 sample files](https://telparia.com/fileFormatSamples/font/calamusFont/)
font | Corel Wiffen Font | .wfn | 
font | Envision Publisher Font | .svf | [3 sample files](https://telparia.com/fileFormatSamples/font/envisionPublisherFont/)
font | LaserJet Soft Font | .sfl .sfp .sft | 
font | LinkWay Font | .fmf | 
font | MacOS Font | .fnt | 
font | PrintPartner Font | .font | 
font | TheDraw Font | .tdf | [1 sample file](https://telparia.com/fileFormatSamples/font/theDrawFont/) - Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it
font | [Windows Font](http://fileformats.archiveteam.org/wiki/FNT_(Windows_Font)) | .fnt | [3 sample files](https://telparia.com/fileFormatSamples/font/windowsFont/) - Rumor has it Fony supports bitmap fonts, but I know it doesn't support vector ones like ROMAN.fnt



## Image (14)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
image | BBC Display RAM Dump |  | [1 sample file](https://telparia.com/fileFormatSamples/image/bbcDisplayRAM/) - While supported, due to no extension and no magic, it's impossible to accurately detect. Abydos will convert invalid files and and produce a garbled image, thus not able to just try a conversion and see.
image | [DraftChoice Drawing](http://www.triusinc.com/forums/viewtopic.php?t=11) | .dch | [2 sample files](https://telparia.com/fileFormatSamples/image/draftChoice/)
image | [Draw 256 Image](http://fileformats.archiveteam.org/wiki/Draw256) | .vga | [4 sample files](https://telparia.com/fileFormatSamples/image/draw256/) - Sadly Draw256 for DOS takes any file ending with .VGA and renders garbage. Cannot determine before if it's a proper file. Due to common extension and extreme rarity of Draw256 files in the wild, this format is marked unsupported.
image | [Facsimile image FORM](http://fileformats.archiveteam.org/wiki/FAXX) | .faxx .fax | [3 sample files](https://telparia.com/fileFormatSamples/image/faxx/) - No known converter.
image | [GEM Vector Metafile](http://fileformats.archiveteam.org/wiki/GEM_VDI_Metafile) | .gem .gdi | [16 sample files](https://telparia.com/fileFormatSamples/image/gemMetafile/) - Vector file format that could be converted into SVG. abydos is working on adding support for this format.
image | KwikDraw Drawing | .kwk | A windows 'object oriented' drawing program. Don't think it was very popular. sandbox/app/KDRAW121.ZIP has the app, works in Win2k, no export ability. Could add a virtual printer driver and then use that to output as PNG.
image | [Kyss KYG](http://fileformats.archiveteam.org/wiki/KYG) | .kyg | [25 sample files](https://telparia.com/fileFormatSamples/image/kyssKYG/) - No known converter.
image | LEONARD'S Sketch Drawing | .ogf | [6 sample files](https://telparia.com/fileFormatSamples/image/leonardsSketchDrawing/) - Fairly obscure CAD type drawing program. Not aware of any drawings that were not those that were included with the program, so format not worth supporting.
image | [MLDF](http://fileformats.archiveteam.org/wiki/MLDF) | .mld | [32 sample files](https://telparia.com/fileFormatSamples/image/mldf/) - It's probably an image format. IFF format FORM with MLDF BMHD. Could not locate any info online about it and I didn't investigate further.
image | NeoPaint Pattern | .pat | While identified via magic as a "NeoPaint Palette" they appear to be "patterns" used as stamps in the MSDOS Neopaint program. Short of reverse engineering it, in theory dexvert could convert these to images by opening up DOS Neopaint, selecting the pattern, stamping it or filling a canvas with it and saving the image. Don't plan on bothing to actually do that though, it's a relatively obscure program and file format.
image | [PETSCII Screen Code Sequence](http://fileformats.archiveteam.org/wiki/PETSCII) | .seq | [1 sample file](https://telparia.com/fileFormatSamples/image/petsciiSeq/) - Just can't reliably detected this format and abydosconvert will convert a lot of things that end in .seq thare are not PETSCII code sequences
image | [Professional Draw Image](http://www.classicamiga.com/content/view/5037/62/) | .clips | [8 sample files](https://telparia.com/fileFormatSamples/image/professionalDraw/) - No known converter.
image | Telepaint | .ss .st | [7 sample files](https://telparia.com/fileFormatSamples/image/telepaint/)
image | [Teletext](http://snisurset.net/code/abydos/teletext.html) | .bin | [2 sample files](https://telparia.com/fileFormatSamples/image/teletext/) - Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on.



## Music (8)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
music | [ANSI Music](http://artscene.textfiles.com/ansimusic/) | .mus | 
music | AY Amadeus Chiptune | .amad | [7 sample files](https://telparia.com/fileFormatSamples/music/ayAMAD/) - Ay_Emul can play these under linux, but they don't offer a command line conversion option. zxtune123 doesn't seem to support them either. I tried several other programs like the AY To WAV converter here without luck: https://bulba.untergrund.net/progr_e.htm
music | [Creative Music System File](http://fileformats.archiveteam.org/wiki/CMS_(Creative_Music_System)) | .cms | [59 sample files](https://telparia.com/fileFormatSamples/music/cms/) - Creative Music System. Couldn't locate any information on the file format itself, nor can I find any 'converters' for it. Only way to play them is within DOSBOX by setting this in the DOSBOX config: [sblaster] sbtype  = gb sbbase  = 220 irq     = 7 dma     = 1 hdma    = 5 sbmixer = true oplmode = cms oplemu  = default oplrate = 22050 Then going into CMSPLAY, running CMSDRV.COM and then PLAYER.EXE However that just plays the file, on an infinite loop, in real time. So while in theory I could maybe make a virtual WAV sound driver under linux and then have DOSBOX play to that driver and then record the music that way, I'd have to wait for the song to play in real time and there is no info on how long the song is
music | [Creative Music System Intelligent Organ File](http://www.vgmpf.com/Wiki/index.php?title=Creative_Music_System_(DOS)) | .org | No modern converter known. The linked website states that there is a converter to convert to CMS, but I couldn't locate it.
music | [DigiTrekker](http://fileformats.archiveteam.org/wiki/DigiTrekker_module) | .dtm | [4 sample files](https://telparia.com/fileFormatSamples/music/digiTrekker/) - DigiTrekker for MSDOS can play these and convert to a 'SND' format, but only in 'realtime' and I couldn't determine the format of the output SND. milkytracker claims support for this format, but I couldn't get it to play any DTM files.
music | [Drum Traker Module](http://fileformats.archiveteam.org/wiki/Drum_Traker_module) | .dtl | [15 sample files](https://telparia.com/fileFormatSamples/music/drumTraker/)
music | [Microdeal Quartet Module](http://fileformats.archiveteam.org/wiki/4v) | .4v | [9 sample files](https://telparia.com/fileFormatSamples/music/quartetModule/)
music | [Music Studio Song](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .sng | [10 sample files](https://telparia.com/fileFormatSamples/music/musicStudioSong/) - In theory the Atari program 'MIDI Music Maker' can convert .sng files to .midi



## Other (98)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
other | Adobe Type Manager Font Information | .inf | 
other | Alchemy Mindworks Resource | .res | 
other | Alpha Four Script | .scp | 
other | Amiga Action Replay 3 Freeze File |  | 
other | Amiga ADF BlkDev File | .blkdev | 
other | Amiga ADF Bootcode | .bootcode | 
other | Amiga ADF XDF Meta | .xdfmeta | 
other | Amiga CLI-Mate Directory Index File |  | 
other | Amiga Hunk Library/Object | .lib .obj .o | 
other | Amiga IFF Debug File | .debug | 
other | Amiga IFF DTYP |  | 
other | Amiga Preferences | .prefs | 
other | Amiga Shared Library | .lib | 
other | Amos Amal Animation Bank | .abk | 
other | AMOS Datas Bank | .abk | 
other | ASCII Font Metrics | .afm | 
other | Atari GEM OBM File | .obm | [10 sample files](https://telparia.com/fileFormatSamples/other/atariGEMOBM/)
other | Audio Interface Library 3 Digital audio driver | .dig | 
other | Audio Interface Library 3 Music/MIDI driver | .mdi | 
other | AutoCAD Protected LISP | .lsp | 
other | Babble! Data | .bab | 
other | Block Breaker Pattern | .blc | 
other | BNUPORT Patch Table | .pat | 
other | Borland Delphi - C++ Builder Form | .dfm | 
other | Borland Delphi Compiled Unit | .dcu | 
other | Borland Graphics Interface Driver | .bgi | 
other | Borland Overlay | .ovr | 
other | BOYAN Action Model | .bam | 
other | CakeWalk Work File | .wrk | 
other | CHAOSultdGEM Parameters | .chs | [8 sample files](https://telparia.com/fileFormatSamples/other/chaosultdGEMParameters/)
other | Chemview Animation Data | .d | 
other | Confusion and Light Compressed Data | .cal | 
other | Corncob 3D Data File | .cct | 
other | Creative Signal Processor microcode | .csp | 
other | Cygnus Editor Default Settings |  | 
other | Cygnus Editor Macros |  | 
other | dBase Compiled Object Program | .dbo | 
other | dBase Index File | .ntx | 
other | dBase Query | .qbe | 
other | dBase Update | .upd | 
other | Electronic Arts LIB container | .lib | 
other | Emacs Compiled Lisp | .elc | [8 sample files](https://telparia.com/fileFormatSamples/other/emacsCompiledLisp/) - Could decompile it with: https://github.com/rocky/elisp-decompile
other | File Express Index Header | .ixh | 
other | File Express Quick Scan | .qss | 
other | FoxPro Memo File | .fpt | 
other | Full Tilt Pinball Data | .dat | 
other | Gee! Printer Driver | .pdr | 
other | GeoWorks GEOS Data | .000 .001 .002 .003 .004 .005 .006 .007 .008 .009 .010 .011 .012 .geo | 
other | Harvard Graphics Chart | .ch3 | 
other | [Hewlett-Packard Graphics Language](http://fileformats.archiveteam.org/wiki/HPGL) | .hpgl | [5 sample files](https://telparia.com/fileFormatSamples/other/hpgl/) - Sometimes used for graphics, sometimes used to control plotters and other machines. I tried to compile this but it's ancient and failed: http://ftp.funet.fi/index/graphics/packages/hpgl2ps/hpgl2ps.tar.Z Quick searches didn't turn up any other 'easy' to grab and use converters, so punt on this for now.
other | HyperPAD Pad | .pad | 
other | ICC Color Profile | .icc | 
other | [InstallShield HDR](http://fileformats.archiveteam.org/wiki/InstallShield_CAB) | .hdr | HDR files are meta data for installShieldCAB files and are not processed directly.
other | InstallShield Uninstall Script | .isu | 
other | Java Class File | .class | [4 sample files](https://telparia.com/fileFormatSamples/other/javaClass/)
other | Legend of Kyrandia EMC File | .emc | 
other | LIFE 3000 Status | .lif | 
other | Lotus 1-2-3 Formatting Data | .fm3 | 
other | Lotus 1-2-3 SQZ! Compressed | wq! | 
other | MDIFF Patch File | .mdf | 
other | Micro Lathe Object | .lat | 
other | Microsoft Printer Definition | .prd | 
other | Microsoft Visual C Library | .lib | 
other | Microsoft Windows Program Information File | .pif | 
other | Miles Sound System Driver | .adv | 
other | Moonbase Game Data | .mb | 
other | NeoPaint Palette | .pal | 
other | NeoPaint Printer Driver | .prd | 
other | Netware Loadable Module | .nlm | 
other | Netware Message | .msg | 
other | Norton Change Directory Info | .ncd | 
other | OLB Library |  | [7 sample files](https://telparia.com/fileFormatSamples/other/olbLib/)
other | Pascal Compiled Unit | .tpu .ppu | 
other | Polyfilm Preferences | .prf | 
other | Printer Font Metrics | .pfm | 
other | Puzzle Buster Puzzle | .puz | 
other | Relocatable Object Module | .obj | 
other | RIFF MSFX File | .sfx | Just contains meta info about a given soundeffect usually distributed alongside it as a .wav
other | RIFF MxSt File | .si | References to other files, seems to be meta info only. Only info I could find, failed to process: https://github.com/dutchcoders/extract-riff
other | RIFF STYL File | .par | References a font for mac and windows and includes some text in a TEXT chunk
other | RTPatch File | .rtp | 
other | SimCity 2000 Save Game Data | .sc .sc2 | 
other | SimCity City | .cty | 
other | SoftDisk Library | .shl | 
other | Startrekker Module Info | .nt | 
other | StormWizard Resource | .wizard .wizard-all | 
other | Superbase Form | .sbv | 
other | Telix Compiled Script | .slc | 
other | Turbo Pascal Help | .hlp | 
other | Visual Basic Extension | .vbx | 
other | Windows Help Global Index Data | .gid | 
other | Windows LOGO Drawing Code | .lgo .lg | 
other | Windows Shortcut | .lnk | 
other | WordPerfect for Windows Button Bar | .wwb | 
other | WordPerfect keyboard file | .wpk | 
other | WordPerfect Macro File | .wpm .wcm | 
other | WordPerfect Printer Data | .all .prd | 
other | ZZT File | .zzt | 



## Rom (1)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
rom | Game Boy ROM | .gb .gbc | 



## Video (5)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
video | [Deluxe Video](http://fileformats.archiveteam.org/wiki/VDEO) |  | [1 sample file](https://telparia.com/fileFormatSamples/video/deluxeVideo/) - Couldn't find a converter for it. Could fire up an amiga with deluxe video program from Electronic Arts.
video | [IFF VAXL](http://fileformats.archiveteam.org/wiki/VAXL) | .vaxl | [15 sample files](https://telparia.com/fileFormatSamples/video/iffVAXL/) - Could only find this potential viewer, but no download link: https://www.ultimateamiga.com/index.php?topic=9605.0
video | RIFF ANIM | .paf | [9 sample files](https://telparia.com/fileFormatSamples/video/riffANIM/) - Couldn't find any evidence of this out in the public. Could very well be a proprietary format
video | [RIFF Multimedia Movie](http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie) | .mmm | [14 sample files](https://telparia.com/fileFormatSamples/video/riffMultimediaMovie/) - Couldn't find a converter or player for it
video | [Video Master Film](http://fileformats.archiveteam.org/wiki/Video_Master_Film) | .flm .vid .vsq | [6 sample files](https://telparia.com/fileFormatSamples/video/videoMasterFilm/) - No known modern converter

