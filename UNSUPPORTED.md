# Unsupported File Formats (530)
These formats can still be **identified** by dexvert, they just are not converted into modern ones.<br>
Some are not converted because they are not very useful, or are specific to a single application.<br>
Others are not converted because there are no known programs to do so. For these formats I maintain a <a href="https://telparia.com/fileFormatBounties.html">bounty list</a> so we can get converter programs written.



## Archive (24)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
archive | [Anex86 PC98 Floppy Image](http://fileformats.archiveteam.org/wiki/Anex86_PC98_floppy_image) | .fdi | [12 sample files](https://telparia.com/fileFormatSamples/archive/anex86FDI/) - The DiskExplorer/editdisk program is supposed to read these, but it fails on my sample files. Removing the 4k header and attempting to mount the raw image fails. Likely because of a disk format unique to PC98. I was able to extract the files by creating a HDD image with anex86 and formatting it by following: http://www.retroprograms.com/mirrors/Protocatbert/protocat.htm After that I could run anex86 with dos6.2 in FDD #1 and the FDI image in FDD #2. Then hit Escape and at the DOS prompt I could COPY B:* C: Then I exited anex86 and then I was able to use wine editdisk.exe to open the HDD image, ctrl-a all the files and ctrl-e extract them. So I could automate this and support FDI extraction. But right now I just don't see the value in doing so.
archive | [Apple Sparse Disk Image](https://en.wikipedia.org/wiki/Sparse_image) | .sparseimage | [1 sample file](https://telparia.com/fileFormatSamples/archive/sparseImage/) - No known linux converter that I could find. Could emulate MacOS X with qemu and do: https://github.com/torarnv/sparsebundlefs/issues/7#issuecomment-326625187
archive | ASetup Installer Archive | .arv | [4 sample files](https://telparia.com/fileFormatSamples/archive/aSetup/) - No known extractor program.
archive | [Corel Thumbnails Archive](http://fileformats.archiveteam.org/wiki/CorelDRAW) |  | [8 sample files](https://telparia.com/fileFormatSamples/archive/corelThumbnails/) - Contains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them. Even went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed. Sent an email to the libcdr creators, to see if they know of any info on the format, but never heard back. NOTE, if the only thing in this is images, then it should be moved to image family
archive | Eschalon Setup ARCV Container |  | No known extractor program.
archive | FIZ Archive | .fiz | [8 sample files](https://telparia.com/fileFormatSamples/archive/fizArchive/) - Could not locate any info on this archive
archive | HomeBrew Game Data Archive | .gw1 .gw2 .gw3 | [4 sample files](https://telparia.com/fileFormatSamples/archive/homeBrewArchive/)
archive | [Icon Heavn](http://fileformats.archiveteam.org/wiki/Icon_Heaven_library) | .fim | [7 sample files](https://telparia.com/fileFormatSamples/archive/iconHeaven/) - Could support it by using icon heaven under an emulated OS/2 instance. NOTE, if the only thing in this is images, then it should be moved to image family
archive | IFF LIST File |  | [18 sample files](https://telparia.com/fileFormatSamples/archive/iffLIST/) - The IFF LIST files contain 'shared' entries that are used for all chunks in the remainder of the file. In theory I could parse this file, and "extract" out by creating seperate files for each major FORM entry inside, making sure to also copy into these files the 'shared' entries, adjusting the resulting FORM lengths as needed. Couldn't find any real documentation on the LIST/SSETPROP format. See: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF
archive | [Installer VISE Package](https://en.wikipedia.org/wiki/Installer_VISE) | .mac | Haven't found non-mac files yet. They appear to be self extracting, so I could just run them under a MAC emulator to get the files out.
archive | [InstallShield Installer Archive](http://fileformats.archiveteam.org/wiki/InstallShield_installer_archive) | .ex_ | [4 sample files](https://telparia.com/fileFormatSamples/archive/installShieldInstallerArchive/)
archive | [Interfaze Application](http://fileformats.archiveteam.org/wiki/Interfaze) | .app | [8 sample files](https://telparia.com/fileFormatSamples/archive/interfaze/)
archive | MoPaQ Archive | .mpq | Need some sample archives. Can use this to extract: https://github.com/Kanma/MPQExtractor or https://github.com/uakfdotb/umpqx
archive | Netscape SNM Archive | .snm | [5 sample files](https://telparia.com/fileFormatSamples/archive/netscapeSNM/) - Could convert with: https://github.com/lantaoxu/Windows-Server-2003/blob/5c6fe3db626b63a384230a1aa6b92ac416b0765f/inetcore/outlookexpress/import/netscape/commimp.cpp
archive | Newton Package | .pkg | 
archive | [OS/2 FTCOMP Archive](http://fileformats.archiveteam.org/wiki/FTCOMP) |  | [6 sample files](https://telparia.com/fileFormatSamples/archive/os2FTCOMP/) - OS/2 packed file. Can be unpackde by UNPACK.EXE or UNPACK2.EXE under OS/2. Available in OS/2 Warp, so I could support these by setting up a QEMU emulated OS/2 machine. Maybe some day.
archive | OS/2 Installation Package | .pkg .pak | [8 sample files](https://telparia.com/fileFormatSamples/archive/os2InstallPackage/) - Could support this with OS/2 unpack if I ever emulated OS/2
archive | Pax Archive | .pax | [8 sample files](https://telparia.com/fileFormatSamples/archive/paxArchive/) - Used in Atari ST program GEM-View
archive | Setup Program Archive | .mva | [6 sample files](https://telparia.com/fileFormatSamples/archive/setupMVA/)
archive | [TED5 Archive](http://www.shikadi.net/moddingwiki/TED5) | .wl1 .ck4 .ck6 | [4 sample files](https://telparia.com/fileFormatSamples/archive/ted5Archive/) - An archive format created by TED5. Used for games like Commander Keen. The format is detailed on the wiki link above, so in theory I could create an extractor for it.
archive | Unix Archive - Old | .a | [8 sample files](https://telparia.com/fileFormatSamples/archive/unixArchiveOld/)
archive | [Viacom New Media Sprite Archive](http://www.shikadi.net/moddingwiki/Viacom_New_Media_Graphics_File_Format) | .vnm .000 | [49 sample files](https://telparia.com/fileFormatSamples/archive/viacomNewMedia/) - An obscure format that packs multiple bitmaps and sprites into a single archive. Found the following two projects that extract them: https://github.com/jmcclell/vnmgf-exporter Sadly neither one can correctly process/extract the VNM files I encountered. The github link is much closer and is in modern Go.
archive | [Warp Disk Image](http://fileformats.archiveteam.org/wiki/WRP) | .wrp | [4 sample files](https://telparia.com/fileFormatSamples/archive/wrp/) - UnWarp on the amiga wants to write directly to an floppy, which we can't easily support. https://github.com/ipr/qXpkLib has some code to unwarp, but in 10 year old lib format for Qt. However it looks somewhat self contained and so we could use this code as an example: https://github.com/ipr/qUnLZX
archive | ZOOM Disk Image | .zom | [1 sample file](https://telparia.com/fileFormatSamples/archive/zoomDiskImage/) - No known modern converter/extractor. Amiga program ZOOM to create and write to floppy: http://aminet.net/package/misc/fish/fish-0459



## Audio (24)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
audio | [AdLib Instrument Bank](http://fileformats.archiveteam.org/wiki/AdLib_instrument_bank) | .bnk | [3 sample files](https://telparia.com/fileFormatSamples/audio/adLibInstrumentBank/) - These .bnk files include sounds/instruments used by adlib ROL/SNG/SX files to make music. Technically the sounds could be extracted, maybe with 'Bank Manager' for DOS, but meh. Awave Studio claims to support these, but under version 7 I couldn't get them to load.
audio | Aegis Sonix Instrument | .instr | [21 sample files](https://telparia.com/fileFormatSamples/audio/sonixInstrument/) - The sampled .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic
audio | AM Sound |  | [4 sample files](https://telparia.com/fileFormatSamples/audio/amSound/)
audio | Art of Noise Instrument | .fm | [5 sample files](https://telparia.com/fileFormatSamples/audio/artOfNoiseInstrument/)
audio | [Creative Labs Instrument Bank](http://fileformats.archiveteam.org/wiki/Instrument_Bank) | .ibk | [2 sample files](https://telparia.com/fileFormatSamples/audio/creativeLabsInstrumentBank/)
audio | [DataShow Sound File](http://www.amateur-invest.com/us_datashow.htm) | .snd | [1 sample file](https://telparia.com/fileFormatSamples/audio/dataShowSound/) - The single sample file I have is a simple text file on how to generate the sound. Probably wouldn't be too hard to create a converter for it. But it's a pretty obscure format, so probably not worth investing any time into it.
audio | Deluxe Sound Sample | .instr | 
audio | HomeBrew Sound | .hse | [1 sample file](https://telparia.com/fileFormatSamples/audio/homeBrewSound/)
audio | [Inverse Frequency Sound Format](http://fileformats.archiveteam.org/wiki/Inverse_Frequency_Sound_format) |  | [3 sample files](https://telparia.com/fileFormatSamples/audio/inverseFrequency/) - Used in various APOGEE games like commander keen. Didn't look that hard for a player/converter.
audio | MaxonMAGIC Sound Sample | .hsn | [8 sample files](https://telparia.com/fileFormatSamples/audio/maxonMagicSoundSample/)
audio | MED Synth Sound |  | [4 sample files](https://telparia.com/fileFormatSamples/audio/medSynthSound/)
audio | [Music Studio Sound](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .snd | [3 sample files](https://telparia.com/fileFormatSamples/audio/musicStudioSound/)
audio | [Musicline Instrument](https://www.musicline.org/) |  | [7 sample files](https://telparia.com/fileFormatSamples/audio/musiclineInstrument/)
audio | [Playstation Sound Format](http://fileformats.archiveteam.org/wiki/PSF) | .psf .minipsf | [5 sample files](https://telparia.com/fileFormatSamples/audio/psf/) - sexypsf will play these, but it doesn't seem to have a way to save to disk as a WAV. It's open source, so I could modify it to support this, or seek an alternate converter. Being a more modern format and console only, not highly motivated.
audio | Proline Voice | .pvd | [8 sample files](https://telparia.com/fileFormatSamples/audio/prolineVoice/)
audio | Psion AICA Audio | .aik | [3 sample files](https://telparia.com/fileFormatSamples/audio/psionAIKAudio/)
audio | [Quattro Pro Sound File](http://fileformats.archiveteam.org/wiki/Quattro_Pro) | .snd | [7 sample files](https://telparia.com/fileFormatSamples/audio/quattroProSound/) - Quattro Pro 3.0 allowed creation of slide shows which could include sounds. Couldn't locate any further information on these files except that they might be soundblaster compataible. Couldn't find anything to play them.
audio | Sonix Sound Sample | .ss | [18 sample files](https://telparia.com/fileFormatSamples/audio/sonixSoundSample/) - These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's
audio | [Sound Blaster Instrument](http://fileformats.archiveteam.org/wiki/Sound_Blaster_Instrument) | .sbi | [10 sample files](https://telparia.com/fileFormatSamples/audio/soundBlasterInstrument/)
audio | [SoundFont 1.0](http://fileformats.archiveteam.org/wiki/SoundFont_1.0) | .sbk | [1 sample file](https://telparia.com/fileFormatSamples/audio/soundFont1/) - Awave Studio can technically convert these, but 99.9% of all SBK SoundFond 1 files just contain meta info that points to a samples in ROM, thus there isn't anything really to convert.
audio | StoneTracker Sample | .sps | [3 sample files](https://telparia.com/fileFormatSamples/audio/stoneTrackerSample/)
audio | [STOS Sample](https://en.wikipedia.org/wiki/STOS_BASIC) | .sam | [3 sample files](https://telparia.com/fileFormatSamples/audio/stosSample/)
audio | [WinRec DVSM](https://temlib.org/AtariForumWiki/index.php/DVSM) | .dvs | [6 sample files](https://telparia.com/fileFormatSamples/audio/dvsm/) - No known linux/windows/amiga converter
audio | ZyXEL Voice Data | .zvd .zyx | [2 sample files](https://telparia.com/fileFormatSamples/audio/zyxelVoice/)



## Document (20)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
document | [Aldus/Adobe PageMaker](http://fileformats.archiveteam.org/wiki/PageMaker) | .pmd .pmt .pm3 .pm4 .pm5 .pm6 .p65 | [3 sample files](https://telparia.com/fileFormatSamples/document/pageMaker/) - No known converter. It's a bit of a nightmare format, only well supported in the version the file was original created in. I have in sandbox/app/AdobePageMaker6.5 which seems to load v4 files. However the app pops up tons of font substitution confirmations, external file references, and other BS. Choosing not to bother supporting these right now, but if I start to discover a ton of them, I could rethink this.
document | Amiga Vision Flow | .avf | [3 sample files](https://telparia.com/fileFormatSamples/document/amigaVisionFlow/)
document | AmigaWriter Documet |  | [3 sample files](https://telparia.com/fileFormatSamples/document/amigaWriter/) - Could probably convert this with the actual AmigaWriter program (sandbox/app/amiwrite.rar) but it's manual doesn't mention anything about CLI conversion.
document | Applesoft BASIC Source Code | .bas | [2 sample files](https://telparia.com/fileFormatSamples/document/applesoftBASIC/)
document | [Calamus Document](http://fileformats.archiveteam.org/wiki/Calamus) | .cdk | [12 sample files](https://telparia.com/fileFormatSamples/document/calamusDocument/)
document | [CanDo Deck](https://cando.amigacity.xyz/index.php/downloads/category/7-cando-software) | .deck | [1 sample file](https://telparia.com/fileFormatSamples/document/canDoDeck/) - Could use 'DeckViewer' from above, or something else to view/convert. More info: https://randocity.com/2018/03/27/cando-an-amiga-programming-language/
document | Clarion Database File | .dat | [49 sample files](https://telparia.com/fileFormatSamples/document/clarionDatabase/) - Did a Google search, couldn't find anything about it. soffice didn't do anything with it either.
document | Cloanto C1-Text Document | .c1text | [1 sample file](https://telparia.com/fileFormatSamples/document/cloantoC1Text/) - Have only encountered just 1 file in the wild. If I encounter more, I can get Cloanto C1-Text program, load it into the Amiga and convert it there.
document | Dart Hypertext |  | [5 sample files](https://telparia.com/fileFormatSamples/document/dartHypertext/) - The DART/DART.EXE program in sandbox/apps/ can open these, it's a text format. It has no way to export as text. It can 'print' the file, but the dosbox I'm using doesn't support printing. Thus this format isn't currently supported.
document | [Envision Publisher Document](http://fileformats.archiveteam.org/wiki/Envision_Publisher) | .evp .evt | [5 sample files](https://telparia.com/fileFormatSamples/document/envisionPublisherDoc/) - Envision Publisher for MSDOS doesn't have an "Export" option. I could figure out how to 'print to a file' or I could set up DOSBOX PDF Printer emulation: superuser.com/questions/270457/how-can-i-print-with-dosbox
document | [Epic TFP Document](https://www.vogons.org/viewtopic.php?f=5&t=35657&start=40) | .tfp | Used in EPIC games. Supposedly can contain hyperlinks, graphics and animations all in a single document format
document | [HotHelp Text](http://fileformats.archiveteam.org/wiki/HotHelp) | .txt .hdr | [6 sample files](https://telparia.com/fileFormatSamples/document/hotHelpText/)
document | [Internet Message Format](http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format) | .eml .msg | [1 sample file](https://telparia.com/fileFormatSamples/document/imf/) - With several RFC files describing the format, uou'd think this would be straight forward to parse, but it's a total nightmare. I had spent some time looking for a good program to parse it, and failed. I spent more time trying to code my own that would output JSON, but there are just a ton of edge cases and I gave up. In addition to the website link above, more details here: https://mailformat.dan.info/
document | Lotus Symphony Worksheet | .wk1 wr1 | 
document | MasterCook Cookbook | .mcf | [2 sample files](https://telparia.com/fileFormatSamples/document/masterCook/) - Was able to open samples with sandbox/app/MasterCook7.iso in WinXP, but couldn't find an easy way to export all recipes to text or PDF. I could write a script that would manually open every recipe, select all the text and copy it and save to disk, like I do with MacroMedia, but meh, overkill for recipes.
document | MediaPaq DCF Catalog | .dcf | [5 sample files](https://telparia.com/fileFormatSamples/document/mediaPaqDCF/) - Metadata and thumbnails archive for MediaClips clip art CDs. NOT related to the DCF camera standard.
document | Microsoft Advisor Help | .hlp | [4 sample files](https://telparia.com/fileFormatSamples/document/microsoftAdvisorHelp/)
document | [Multimedia Viewer Book](http://fileformats.archiveteam.org/wiki/Multimedia_Viewer_Book) | .mvb | [3 sample files](https://telparia.com/fileFormatSamples/document/multimediaViewerBook/)
document | OPHelp | .hlp | [5 sample files](https://telparia.com/fileFormatSamples/document/opHelp/) - Couldn't locate additional info for it
document | TurboCalc Document | .tcd | [4 sample files](https://telparia.com/fileFormatSamples/document/turboCalc/)



## Executable (18)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
executable | a.out Executable | .o | 
executable | AmigaOS Executable |  | 
executable | Atari Control Panel Extension Module | .cpx | [10 sample files](https://telparia.com/fileFormatSamples/executable/atariCPX/)
executable | Atari Executable | .xex | [4 sample files](https://telparia.com/fileFormatSamples/executable/xex/)
executable | Atari ST Executable |  | [11 sample files](https://telparia.com/fileFormatSamples/executable/atariSTExe/)
executable | ELF Executable |  | 
executable | FM-TownsOS App | .exp | [9 sample files](https://telparia.com/fileFormatSamples/executable/fmTownsOSApp/)
executable | Linux i386 Executable |  | 
executable | Linux OMAGIC Executable |  | 
executable | Linux ZMAGIC Exectutable |  | 
executable | Mach-O m68k Executable |  | 
executable | MacOS PPC PEF Executable |  | 
executable | MIPSL ECOFF Executable |  | 
executable | MS-DOS COM Executable | .com .c0m | [4 sample files](https://telparia.com/fileFormatSamples/executable/com/)
executable | MS-DOS Driver | .sys .drv | 
executable | RISC OS Executable |  | 
executable | SPARC Demand Paged Exe |  | 
executable | Superbase Program | .sbp | 



## Font (30)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
font | 3D Construction Kit Font | .3fd | 
font | AmigaOS Outline Font | .font | 
font | AmiWrite Font |  | 
font | Avery Font | .ff1 | 
font | Banner Mania Font | .fnt | [19 sample files](https://telparia.com/fileFormatSamples/font/bannerManiaFont/)
font | Borland Graphics Font | .chr .bgi | 
font | Bradford Font | .bf2 | 
font | Calamus Font | .cfn | [10 sample files](https://telparia.com/fileFormatSamples/font/calamusFont/)
font | Corel Wiffen Font | .wfn | 
font | DynaCADD Vector Font | .fnt | 
font | Envision Publisher Font | .svf | [3 sample files](https://telparia.com/fileFormatSamples/font/envisionPublisherFont/)
font | GRX Font | .fnt | 
font | [IntelliFont Font](http://fileformats.archiveteam.org/wiki/IntelliFont) | .lib .type | [7 sample files](https://telparia.com/fileFormatSamples/font/intelliFont/)
font | LaserJet Soft Font | .sfl .sfp .sft | 
font | LinkWay Font | .fmf | 
font | Lotus Raster Font | .lrf | 
font | Lotus Vector Font | .lvf | 
font | MacOS Font | .fnt | 
font | [Portable Font Resource](http://fileformats.archiveteam.org/wiki/PFR) | .pfr | [3 sample files](https://telparia.com/fileFormatSamples/font/portableFontResource/) - Could create a custom HTML file that references the PFR and load it in Netscape 4.03 and take a screenshot.
font | PrintPartner Font | .font | 
font | Psion Font | .fon | 
font | Signum Font | .e24 | 
font | [Speedo Font](http://fileformats.archiveteam.org/wiki/Speedo) | .spd | [3 sample files](https://telparia.com/fileFormatSamples/font/speedo/)
font | TeX Packed Font | .pf | 
font | TheDraw Font | .tdf | [1 sample file](https://telparia.com/fileFormatSamples/font/theDrawFont/) - Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it
font | VFONT Font | .fnt | 
font | Westwood Font | .fnt | [3 sample files](https://telparia.com/fileFormatSamples/font/westwoodFont/)
font | [Windows Font](http://fileformats.archiveteam.org/wiki/FNT_(Windows_Font)) | .fnt | [3 sample files](https://telparia.com/fileFormatSamples/font/windowsFont/) - Rumor has it Fony supports bitmap fonts, but I know it doesn't support vector ones like ROMAN.fnt
font | WordUp Graphics Toolkit Font | .wfn | 
font | X11/NeWS font family | .ff | 



## Image (31)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
image | Atari ST Graph Diagram | .dia | [3 sample files](https://telparia.com/fileFormatSamples/image/atariGraphDiagram/) - No known converter. Atari ST graphing program by Hans-Christoph Ostendorf.
image | AutoCAD Shape | .shx | [6 sample files](https://telparia.com/fileFormatSamples/image/autoCADShape/)
image | AutoSketch Drawing | .skd | [5 sample files](https://telparia.com/fileFormatSamples/image/autoSketchDrawing/)
image | BBC Display RAM Dump |  | [1 sample file](https://telparia.com/fileFormatSamples/image/bbcDisplayRAM/) - While supported by abydos, due to no extension and no magic, it's impossible to detect accurately.
image | [DraftChoice Drawing](http://www.triusinc.com/forums/viewtopic.php?t=11) | .dch | [30 sample files](https://telparia.com/fileFormatSamples/image/draftChoice/)
image | [Draw 256 Image](http://fileformats.archiveteam.org/wiki/Draw256) | .vga | [4 sample files](https://telparia.com/fileFormatSamples/image/draw256/) - Unsupported because .vga ext is too common, no known magic and converters can't be trusted to verify input file is correct before outputting garbage
image | [DrawStudio Drawing](http://fileformats.archiveteam.org/wiki/DrawStudio) | .dsdr | [8 sample files](https://telparia.com/fileFormatSamples/image/drawStudio/) - Amiga program DrawStudio creates these. No known converter. DrawStudio demo available: https://aminet.net/package/gfx/edit/DrawStudioFPU
image | [Fastgraph Pixel Run Format](http://fileformats.archiveteam.org/wiki/Fastgraph_Pixel_Run_Format) | .prf | [12 sample files](https://telparia.com/fileFormatSamples/image/fastgraphPRF/) - No known converter. IMPROCES (see website) can load these images and save as GIF/PCX but sadly it's a mouse driven interface which dexvert can't automate yet.
image | [FLI Profi](http://fileformats.archiveteam.org/wiki/FLI_Profi) | .fpr .flp | [1 sample file](https://telparia.com/fileFormatSamples/image/fpr/) - Due to no known magic and how recoil2png/view64 will convert ANYTHING, we disable this for now.
image | [GEM Vector Metafile](http://fileformats.archiveteam.org/wiki/GEM_VDI_Metafile) | .gem .gdi | [16 sample files](https://telparia.com/fileFormatSamples/image/gemMetafile/) - Vector file format that could be converted into SVG. abydos is working on adding support for this format.
image | HomeBrew Icon | .hic | [1 sample file](https://telparia.com/fileFormatSamples/image/homeBrewIcon/)
image | ID Software Sprite | .spr | [3 sample files](https://telparia.com/fileFormatSamples/image/idSoftwareSprite/)
image | [JPEG XL](http://fileformats.archiveteam.org/wiki/JPEG_XL) | .jxl | [8 sample files](https://telparia.com/fileFormatSamples/image/jpegXL/) - Modern format. Pain in the butt to build the JPEG-XL reference package, I started, see overlay/legacy/JPEG-XL but then gave up because meh.
image | LEONARD'S Sketch Drawing | .ogf | [6 sample files](https://telparia.com/fileFormatSamples/image/leonardsSketchDrawing/) - Fairly obscure CAD type drawing program. Not aware of any drawings that were not those that were included with the program, so format not worth supporting.
image | Micro Illustrator | .mic | [1 sample file](https://telparia.com/fileFormatSamples/image/microIllustrator/) - NOT the same as image/mil Micro Illustrator. Sadly. due to no known magic and how recoil2png/view64 will convert ANYTHING, we disable this for now.
image | [Micrografx Icon](http://fileformats.archiveteam.org/wiki/Micrografx_Icon) | .icn | [4 sample files](https://telparia.com/fileFormatSamples/image/micrografxIcon/) - No known converter.
image | NeoPaint Pattern | .pat | [2 sample files](https://telparia.com/fileFormatSamples/image/neoPaintPattern/) - While identified via magic as a "NeoPaint Palette" they appear to be "patterns" used as stamps in the MSDOS Neopaint program. Short of reverse engineering it, in theory dexvert could convert these to images by opening up DOS Neopaint, selecting the pattern, stamping it or filling a canvas with it and saving the image. Don't plan on bothing to actually do that though, it's a relatively obscure program and file format.
image | [Painter Raster Image Format](http://fileformats.archiveteam.org/wiki/Painter_RIFF) | .rif | [2 sample files](https://telparia.com/fileFormatSamples/image/painterRIF/)
image | PC-Draft-CAD Drawing | .dwg | 
image | [PCR Image](http://fileformats.archiveteam.org/wiki/PCR_image) | .pcr | [1 sample file](https://telparia.com/fileFormatSamples/image/pcrImage/)
image | [PETSCII Screen Code Sequence](http://fileformats.archiveteam.org/wiki/PETSCII) | .seq | [1 sample file](https://telparia.com/fileFormatSamples/image/petsciiSeq/) - Just can't reliably detected this format and abydosconvert will convert a lot of things that end in .seq thare are not PETSCII code sequences
image | [PMDraw](http://fileformats.archiveteam.org/wiki/PmDraw) | .pmd | [6 sample files](https://telparia.com/fileFormatSamples/image/pmDraw/) - No known converter. OS/2 drawing program. I could emulate OS/2 and run actual PMDraw and export.
image | [Professional Draw Image](http://www.classicamiga.com/content/view/5037/62/) | .clips | [8 sample files](https://telparia.com/fileFormatSamples/image/professionalDraw/) - No known converter.
image | ProShape Drawing | .psp | [5 sample files](https://telparia.com/fileFormatSamples/image/proShapeDrawing/) - No known converter.
image | Second Nature Slide Show | .cat | [7 sample files](https://telparia.com/fileFormatSamples/image/secondNatureSlideShow/) - Could probably spy on how the second nature DLL files are called when reading these files and figure out how to call the DLL myself with AutoIt. Meh.
image | [Simple Vector Format](http://fileformats.archiveteam.org/wiki/Simple_Vector_Format) | .svf | [5 sample files](https://telparia.com/fileFormatSamples/image/simpleVectorFormat/)
image | [SLP Image](http://fileformats.archiveteam.org/wiki/Age_of_Empires_Graphics_File) | .slp | [2 sample files](https://telparia.com/fileFormatSamples/image/slpImage/) - Could use SLP Editor or SLPCNVT (see sandbox/app) but both had issues opening several files and since it's just for AoE, not worth the effort.
image | Telepaint | .ss .st | [7 sample files](https://telparia.com/fileFormatSamples/image/telepaint/)
image | [Teletext](http://snisurset.net/code/abydos/teletext.html) | .bin | [2 sample files](https://telparia.com/fileFormatSamples/image/teletext/) - Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on.
image | [Universal BitMap Format](http://retromission.com/browse/749/HACKER2.mdf/tsoft/bjim040.zip) | .ubf | [8 sample files](https://telparia.com/fileFormatSamples/image/universalBitMapFormat/)
image | [Ventura Publisher Graphic](http://fileformats.archiveteam.org/wiki/Ventura_Publisher) | .vgr | [4 sample files](https://telparia.com/fileFormatSamples/image/venturaPublisher/) - Tried both Ventura Publisher 4.1 and Corel Draw 5 (which includes it) and neither could open the sample VGR files I have.



## Music (68)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
music | Ace Tracker Module | .am | [3 sample files](https://telparia.com/fileFormatSamples/music/aceTracker/)
music | Aero Studio | .aero | [2 sample files](https://telparia.com/fileFormatSamples/music/aeroStudio/)
music | All Sound Tracker Module | .ast | [2 sample files](https://telparia.com/fileFormatSamples/music/allSoundTracker/)
music | AND XSynth Module | .amx | [1 sample file](https://telparia.com/fileFormatSamples/music/andXSynth/)
music | [ANSI Music](http://artscene.textfiles.com/ansimusic/) | .mus | 
music | AProSys Module | .amx | [2 sample files](https://telparia.com/fileFormatSamples/music/aProSys/)
music | Atari Digi-Mix Module | .mix | [3 sample files](https://telparia.com/fileFormatSamples/music/atariDigiMix/)
music | AXS Module | .axs | [2 sample files](https://telparia.com/fileFormatSamples/music/axsModule/)
music | AY Amadeus Chiptune | .amad | [7 sample files](https://telparia.com/fileFormatSamples/music/ayAMAD/) - Ay_Emul can play these under linux, but they don't offer a command line conversion option. zxtune123 doesn't seem to support them either. I tried several other programs like the AY To WAV converter here without luck: https://bulba.untergrund.net/progr_e.htm
music | AY STRC Module | .strc | [1 sample file](https://telparia.com/fileFormatSamples/music/aySTRC/)
music | Beepola Module | .bbsong | [3 sample files](https://telparia.com/fileFormatSamples/music/beepola/)
music | [Beni Tracker Module](http://fileformats.archiveteam.org/wiki/Beni_Tracker_module) | .pis | [5 sample files](https://telparia.com/fileFormatSamples/music/beniTracker/)
music | BeRoTracker Module | .brt | [2 sample files](https://telparia.com/fileFormatSamples/music/beRoTracker/) - A 32bit linux 1997 player in: sandbox/app/BeRoLinuxPlayer v1.0.rar  Could get an OLD linux OS and install in QEMU: https://soft.lafibre.info/
music | Chuck Biscuits/Black Artist Module | .cba | [3 sample files](https://telparia.com/fileFormatSamples/music/cba/)
music | [Creative Music System File](http://fileformats.archiveteam.org/wiki/CMS_(Creative_Music_System)) | .cms | [59 sample files](https://telparia.com/fileFormatSamples/music/cms/) - Creative Music System. Couldn't locate any information on the file format itself, nor can I find any 'converters' for it. Only way to play them is within DOSBOX by setting this in the DOSBOX config: [sblaster] sbtype  = gb sbbase  = 220 irq     = 7 dma     = 1 hdma    = 5 sbmixer = true oplmode = cms oplemu  = default oplrate = 22050 Then going into CMSPLAY, running CMSDRV.COM and then PLAYER.EXE However that just plays the file, on an infinite loop, in real time. So while in theory I could maybe make a virtual WAV sound driver under linux and then have DOSBOX play to that driver and then record the music that way, I'd have to wait for the song to play in real time and there is no info on how long the song is
music | [Creative Music System Intelligent Organ File](http://www.vgmpf.com/Wiki/index.php?title=Creative_Music_System_(DOS)) | .org | No modern converter known. The linked website states that there is a converter to convert to CMS, but I couldn't locate it.
music | DeLuxe Music Score |  | [2 sample files](https://telparia.com/fileFormatSamples/music/deLuxeMusicScore/) - Likely from the Deluxe Music Construction Set
music | Digital Sound Interface Kit Module | .dsm | [1 sample file](https://telparia.com/fileFormatSamples/music/digitalSoundInterfaceKit/)
music | [DigiTrekker](http://fileformats.archiveteam.org/wiki/DigiTrekker_module) | .dtm | [4 sample files](https://telparia.com/fileFormatSamples/music/digiTrekker/) - DigiTrekker for MSDOS can play these and convert to a 'SND' format, but only in 'realtime' and I couldn't determine the format of the output SND. milkytracker claims support for this format, but I couldn't get it to play any DTM files.
music | DreamStation Module | .dss | [3 sample files](https://telparia.com/fileFormatSamples/music/dreamStation/)
music | [Drum Traker Module](http://fileformats.archiveteam.org/wiki/Drum_Traker_module) | .dtl | [15 sample files](https://telparia.com/fileFormatSamples/music/drumTraker/)
music | [Dynamic Studio Professional Module](http://fileformats.archiveteam.org/wiki/Dynamic_Studio_Professional_module) | .dsm .dsp | [3 sample files](https://telparia.com/fileFormatSamples/music/dynamicStudio/)
music | Encore Musical Notation | .enc .mus | [3 sample files](https://telparia.com/fileFormatSamples/music/encoreMusicalNotation/)
music | [Face The Music Module](http://eab.abime.net/showthread.php?t=62254) | .ftm | [5 sample files](https://telparia.com/fileFormatSamples/music/faceTheMusic/)
music | FamiTracker Module | .fmt | [4 sample files](https://telparia.com/fileFormatSamples/music/famiTracker/) - I tried using FamiTracker under WinXP http://famitracker.com/ but it just created a WAV of zero bytes long. Maybe because I'm not emulating a sound card...
music | Flash Tracker | .fls | [5 sample files](https://telparia.com/fileFormatSamples/music/flashTracker/)
music | FMTracker Module | .fmt | [4 sample files](https://telparia.com/fileFormatSamples/music/fmTracker/)
music | Fuxoft AY Language | .fxm | [5 sample files](https://telparia.com/fileFormatSamples/music/fuxoftAYLanguage/)
music | GoatTracker Module | .sng | [6 sample files](https://telparia.com/fileFormatSamples/music/goatTracker/)
music | Improvise Music Data | .imp | [5 sample files](https://telparia.com/fileFormatSamples/unsupported/improviseMusicData/)
music | Ixalance Module | .ixs | [5 sample files](https://telparia.com/fileFormatSamples/music/ixalance/)
music | JayTrax Module | .jxs | [4 sample files](https://telparia.com/fileFormatSamples/music/jayTrax/)
music | Jeskola Buzz Module | .bmx .bmw | [3 sample files](https://telparia.com/fileFormatSamples/music/buzz/)
music | Klystrack Module | .kt | [5 sample files](https://telparia.com/fileFormatSamples/music/klystrack/)
music | [Master Tracker AdLib Module](http://fileformats.archiveteam.org/wiki/Master_Tracker_module) | .mtr | [4 sample files](https://telparia.com/fileFormatSamples/music/masterTracker/)
music | Master Tracks Pro | .mts | [1 sample file](https://telparia.com/fileFormatSamples/music/masterTracksPro/) - So the Pro version of Master Tracks Pro software, which I own, can convert this to MIDI, but it only runs on Vista/7/8/10. I could add a QEMU server for Win 7 I suppose, but not really worth it for 1 format.
music | MaxTrax Module | .mxtx | [8 sample files](https://telparia.com/fileFormatSamples/music/maxTrax/)
music | [Music Studio Song](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .sng | [10 sample files](https://telparia.com/fileFormatSamples/music/musicStudioSong/) - In theory the Atari program 'MIDI Music Maker' can convert .sng files to .midi
music | MusicMaker Module | .mm8 | [5 sample files](https://telparia.com/fileFormatSamples/music/musicMakerModule/)
music | MVSTracker Module | .mus | [2 sample files](https://telparia.com/fileFormatSamples/music/mvsTracker/)
music | MVX Module | .mvm | [4 sample files](https://telparia.com/fileFormatSamples/music/mvxModule/)
music | NerdTracker Module | .ned | [4 sample files](https://telparia.com/fileFormatSamples/music/nerdTracker/)
music | [NoiseTrekker Module](http://fileformats.archiveteam.org/wiki/Noisetrekker_module) | .ntk | [5 sample files](https://telparia.com/fileFormatSamples/music/noiseTrekker/)
music | Onyx Music File Module | .omf | [4 sample files](https://telparia.com/fileFormatSamples/music/onyxMusicFile/)
music | Organya Module | .org | [7 sample files](https://telparia.com/fileFormatSamples/music/organya/)
music | Palladix | .plx | [3 sample files](https://telparia.com/fileFormatSamples/music/palladix/)
music | Paragon 5 Gameboy Tracker Module | .mgb | [4 sample files](https://telparia.com/fileFormatSamples/music/gameboyTracker/)
music | Piston Collage Module | .ptcop | [6 sample files](https://telparia.com/fileFormatSamples/music/pistonCollage/)
music | PollyTracker Module | .mod | [4 sample files](https://telparia.com/fileFormatSamples/music/pollyTracker/)
music | Pro Trekkr Module | .ixs | [6 sample files](https://telparia.com/fileFormatSamples/music/proTrekkr/)
music | Psycle Module | .psy | [4 sample files](https://telparia.com/fileFormatSamples/music/psycle/)
music | [Quartet 4V Module](http://fileformats.archiveteam.org/wiki/4v) | .4v | [9 sample files](https://telparia.com/fileFormatSamples/music/quartet4V/)
music | RamTracker Module | .trk | [4 sample files](https://telparia.com/fileFormatSamples/music/ramTracker/)
music | [Renoise Module](http://fileformats.archiveteam.org/wiki/Renoise_song) | .xrns .rns | [8 sample files](https://telparia.com/fileFormatSamples/music/renoise/) - The XRNS format is just a ZIP file with samples inside as FLACS and a song XML. The archive/zip format will end up handling that. I tried using renoise program, but it doesn't have CLI conversion nor did it even work anyways to render a song. Sigh.
music | SBStudio Module | .pac | [3 sample files](https://telparia.com/fileFormatSamples/music/sbStudio/)
music | ShroomPlayer Module | .sho | [5 sample files](https://telparia.com/fileFormatSamples/music/shroomPlayer/)
music | Skale Tracker Module | .skm | [5 sample files](https://telparia.com/fileFormatSamples/music/skaleTracker/)
music | Sound Club Module | .sn .sn2 | [9 sample files](https://telparia.com/fileFormatSamples/music/soundClub/)
music | STarKos Module | .psy | [4 sample files](https://telparia.com/fileFormatSamples/music/starkos/)
music | StoneTracker Module | .spm .sps | [6 sample files](https://telparia.com/fileFormatSamples/music/stoneTracker/)
music | SunVox Module | .psy | [4 sample files](https://telparia.com/fileFormatSamples/music/sunVox/)
music | [SVArTracker Module](https://www.kvraudio.com/product/svartracker-by-svar-software) | .svar | [3 sample files](https://telparia.com/fileFormatSamples/music/svarTracker/) - I tried using sandbox/app/svartracker_1_22_free_inst.exe under win2k but got lots of errors and couldn't even figure out how to 'render' the file to WAV, VERY clumsy program and only a tiny handful of songs seem to exist for it.
music | Synder SNG-Player Module | .sng | [5 sample files](https://telparia.com/fileFormatSamples/music/synderSNG/) - An old 3bit linux player binary can be found sandbox/app/Synder SNG-Player Linux32 build 2008-05-19.rar   Could get an OLD linux OS and install in QEMU: https://soft.lafibre.info/
music | Synder Tracker Module | .sng | [2 sample files](https://telparia.com/fileFormatSamples/music/synderTrackerModule/)
music | T'SoundSystem Source Module | .tss | [4 sample files](https://telparia.com/fileFormatSamples/music/tss/)
music | The 0ok Amazing Synth Tracker Module | .t0ast | [4 sample files](https://telparia.com/fileFormatSamples/music/t0ast/)
music | VGM Music Maker Module | .vge | [4 sample files](https://telparia.com/fileFormatSamples/music/vgmMusicMaker/)
music | Vic-Tracker Module | .vt | [5 sample files](https://telparia.com/fileFormatSamples/music/vicTracker/)



## Other (280)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
other | 3D Construction Kit Area | .3ad | 
other | 3D Construction Kit Object | .3od .obj | 
other | 3D Construction Kit Shape Data | .3sd | 
other | 3D Construction Kit World Data | .kit | 
other | 3D Studio Project | .prj | 
other | 4D Paint Project | .4dp | [1 sample file](https://telparia.com/fileFormatSamples/other/fourDPaintProject/)
other | Abuse Level | .lvl .spe | 
other | Adobe Duotone Options | .ado | 
other | Adobe Hyphenation/Spelling Dictionary | .hyp | 
other | Adobe Multiple Master Metrics | .mmm | 
other | Adobe Photoshop Gradient | .grd | 
other | Adobe Type Manager Font Information | .inf | 
other | Adventure Game Toolkit Strings | .d$$ | 
other | Aegis Pro Motion Geometry | .geo | 
other | Alchemy Mindworks Resource | .res | 
other | Alcohol 120% Media Descriptor | .mds | [2 sample files](https://telparia.com/fileFormatSamples/unsupported/mdfMediaDescriptor/)
other | Allways Printer Driver | .apc .apd .apf | 
other | Alpha Four Script | .scp | 
other | AmiAtlas File | .borders .coasts .index .islands .prefs .rivers .route .town .countries .country | 
other | Amiga Action Replay 3 Freeze File |  | [4 sample files](https://telparia.com/fileFormatSamples/unsupported/amigaActionReplay3/)
other | Amiga ADF BlkDev File | .blkdev | 
other | Amiga ADF Bootcode | .bootcode | 
other | Amiga ADF XDF Meta | .xdfmeta | 
other | Amiga BASIC Protected File | .bas | 
other | Amiga CLI-Mate Directory Index File |  | 
other | Amiga E Module | .m | 
other | Amiga Hunk Library/Object | .lib .obj .o | 
other | Amiga IFF Debug File | .debug | [7 sample files](https://telparia.com/fileFormatSamples/unsupported/iffSDBG/)
other | Amiga IFF DTYP |  | 
other | Amiga IFF GXUI | .gui | 
other | Amiga Outline Tag | .otag | 
other | Amiga Preferences | .prefs | 
other | Amiga Shared Library | .lib | 
other | Amos Amal Animation Bank | .abk | 
other | AMOS ASM Bank | .abk | 
other | AMOS Datas Bank | .abk | [10 sample files](https://telparia.com/fileFormatSamples/unsupported/amosDatasBank/)
other | AMOS Work Bank | .abk | 
other | AniMouse Tutorial | .sdemo | 
other | ArtEffect Brush |  | 
other | ArtEffect Convolution |  | 
other | ASCII Font Metrics | .afm | 
other | Atari CTB File | .ctb | [5 sample files](https://telparia.com/fileFormatSamples/unsupported/atariCTBFile/)
other | Atari GEM OBM File | .obm | [16 sample files](https://telparia.com/fileFormatSamples/unsupported/atariGEMOBM/)
other | Audio Interface Library 3 Digital audio driver | .dig | 
other | Audio Interface Library 3 Music/MIDI driver | .mdi | 
other | AutoCAD Compiled Menu | .mnx | 
other | AutoCAD Protected LISP | .lsp | 
other | AutoDesk 3D-Studio Material Library | .mli | 
other | Babble! Data | .bab | 
other | Bars and Pipes File | .gchone .gchord .song | 
other | Binary Color Format | .bcf | 
other | Block Breaker Pattern | .blc | 
other | BNUPORT Patch Table | .pat | 
other | Borland Delphi Compiled Unit | .dcu | 
other | Borland Graphics Interface Driver | .bgi | 
other | Borland Language Library | .bll | 
other | Borland Overlay | .ovr | 
other | BOYAN Action Model | .bam | 
other | Build Engine Demo Data | .dem | 
other | Build Engine RFF Container | .rff | 
other | BWSB Music and Sound Engine Driver | .mse | 
other | CAD/Draw Library | .tbl | 
other | CAD/Draw Settings | .mpi | 
other | Cakewalk Studio Ware Panel | .CakewalkStudioWare | 
other | CakeWalk Work File | .wrk | 
other | Calamus Farb Color Table | .cft .cf | 
other | Calamus Raster Information | .cri .cr | 
other | Calamus Text Style List | .csl .cs | 
other | Caligari TrueSpace Data |  | 
other | CHAOSultdGEM Parameters | .chs | [8 sample files](https://telparia.com/fileFormatSamples/unsupported/chaosultdGEMParameters/)
other | Character Table Library | .tlb | 
other | Chemview Animation Data | .d | 
other | Chess Assistant File | .bic .bid .bim .bis .lib .bfi .dsc .ndx .bdy | 
other | Clipper Pre-Linked Library | .pll | 
other | Compiled AppleScript Script |  | [2 sample files](https://telparia.com/fileFormatSamples/unsupported/appleScriptCompiled/)
other | Confusion and Light Compressed Data | .cal | 
other | Corel Editor Macro | .edm | 
other | Corel Shell Macro | .shm | 
other | Corncob 3D Data File | .cct | 
other | Cornel Huth Compressed Library | .li_ | 
other | Create Adventure Games Project | .cag | 
other | Creative Signal Processor Microcode | .csp | 
other | Cybervision Monitor Info |  | 
other | Cygnus Editor Default Settings |  | 
other | Cygnus Editor Macros |  | 
other | dBase Compiled Object Program | .dbo | 
other | dBase Index File | .ntx | 
other | dBase Query | .qbe | 
other | dBase Update | .upd | 
other | DeHackEd Patch | .deh | 
other | Descent Level | .rdl | 
other | Dive File Format | .dff | 
other | DOOM Save Game | .dsg | 
other | Dr.Web Anti-Virus Database | .vdb | 
other | Dynamic Message System File | .msg | 
other | Electronic Arts LIB container | .lib | 
other | Emacs Compiled Lisp | .elc | [8 sample files](https://telparia.com/fileFormatSamples/unsupported/emacsCompiledLisp/) - Could decompile it with: https://github.com/rocky/elisp-decompile
other | Ensoniq VFX Patch File | .vfx | 
other | Expressware Printer Definition File | .pdf | 
other | Fiasco Database File | .fdat .fidx .frec .fdb .fpr | 
other | File Express Index Header | .ixh | 
other | File Express Quick Scan | .qss | 
other | Flight Sim Toolkit Terrain Data | .ftd | 
other | FoxPro Memo File | .fpt | 
other | Fractal Design Painter Paper Texture | .pap | 
other | Full Tilt Pinball Data | .dat | 
other | Game Boy ROM | .gb .gbc | 
other | GammaCAD Document | .sym .gc1 | 
other | Gee! Printer Driver | .pdr | 
other | GeoWorks GEOS Data | .000 .001 .002 .003 .004 .005 .006 .007 .008 .009 .010 .011 .012 .geo | 
other | Gettext Machine Object | .gmo | 
other | Half-Life 2 Save Game | .sav | 
other | Harvard Graphics Chart | .ch3 | 
other | High Speed Pascal Unit | .unit | 
other | HomeBrew Level | .hle | 
other | HomeBrew Palette | .hpa | 
other | HomeBrew Tile | .hti | 
other | HotMap VBX Regions Description | .hmd | 
other | Human Machine Interfaces Sound Driver | .386 | 
other | HyperPAD Pad | .pad | 
other | ICC Color Map | .iff | 
other | ICC Color Profile | .icc | 
other | IDA Signatures | .sig | 
other | IFF Binary Patch | .pch .patch | 
other | Imagine Staging Data | .istg | 
other | Index Volume GUID |  | 
other | Infinity Engine File | .dlg .cre .itm .are .tlk .spl .sto | 
other | [InstallShield HDR](http://fileformats.archiveteam.org/wiki/InstallShield_CAB) | .hdr | [2 sample files](https://telparia.com/fileFormatSamples/other/installShieldHDR/) - HDR files are meta data for installShieldCAB files and are not processed directly.
other | InstallShield Uninstall Script | .isu | 
other | Intel Common Object File Format Object | .obj | 
other | Java Class File | .class | [4 sample files](https://telparia.com/fileFormatSamples/unsupported/javaClass/)
other | Javelin Printer Driver | .pr .pr2 | 
other | Jazz Jackrabbit File | .0sc .0fn | 
other | Kapersky Anti-Virus License Key | .key | 
other | Kodak Precision Transform | .pt | 
other | KryoFlux Raw Stream | .raw | [1 sample file](https://telparia.com/fileFormatSamples/unsupported/kryoFluxRawStream/)
other | LabView Virtual Instrument | .vi | 
other | LDIFF Differences Data | .lzd | 
other | Legend of Kyrandia EMC File | .emc | 
other | LIFE 3000 Status | .lif | 
other | Linux 8086 Object File | .o | 
other | Linux Kernel |  | 
other | Linux Swap File |  | 
other | LogicSim Circuit |  | 
other | Lotus 1-2-3 Formatting Data | .fm3 | 
other | Lotus 1-2-3 SQZ! Compressed | wq! | 
other | Lotus Freelance Presentation | .prz | 
other | Lotus Magellan Viewer | .vw2 | 
other | LucasFilm Data | .lfd | 
other | Mach-O m68k Object | .o | 
other | Maple Common Binary | .m | 
other | MASI Music Driver | .mus | 
other | MathCad Document | .mcd | 
other | MDIFF Patch File | .mdf | 
other | MegaPaint Printer Driver | .trb | 
other | MetaCreations Resource Composite File |  | 
other | Micro Lathe Object | .lat | 
other | [Microsoft Comic Chat Character](http://fileformats.archiveteam.org/wiki/Microsoft_Comic_Chat) | .avb | [5 sample files](https://telparia.com/fileFormatSamples/other/microsoftChatCharacter/)
other | Microsoft Incremental Linker Data | .ilk | 
other | Microsoft Printer Definition | .prd | 
other | Microsoft Program Database | .pdb | 
other | Microsoft Security Catalog | .cat | 
other | Microsoft Separate Debug Format | .dbg | 
other | Microsoft Serialized Certificate Store | .sst | 
other | Microsoft Visual C Files | .bsc .sbr .wsp | 
other | Microsoft Visual C Library | .lib | 
other | Microsoft Windows Program Information File | .pif | 
other | Microsoft Word Style Sheet | .sty | 
other | MIDI Drum Machine | .drm | Program and source at: /browse/111/130%20MIDI%20Tool%20Box.iso/drum
other | MIDI-MAZE II Maze | .mze | 
other | Miles Sound System Driver | .adv | 
other | Moonbase Game Data | .mb | 
other | MS-DOS Code Page Info | .cp .cpi | 
other | MUI Builder Project | .muib | 
other | NeoPaint Palette | .pal | 
other | NeoPaint Printer Driver | .prd | 
other | Netware Loadable Module | .nlm | 
other | Netware Message | .msg | 
other | Nintendo ROM | .nes | 
other | Norton Change Directory Info | .ncd | 
other | Novell System PrintDef Device Definition | .pdf | 
other | Oberon Symbol | .sym | 
other | OLB Library |  | [7 sample files](https://telparia.com/fileFormatSamples/unsupported/olbLib/)
other | PaperPort Slide Show | .fss | 
other | Pascal Compiled Unit | .tpu .ppu | 
other | PatchMeister Driver | .pmdriver | 
other | PCAnywhere Data | .bhf | 
other | PGP Key Ring | .key .pgp | 
other | Platinen Layout Program Layout | .pla | 
other | Platinen Layout Programm Bibliotheken/library | .bib | 
other | Polyfilm Preferences | .prf | 
other | Ports of Call Save Game | .trp | 
other | Power Up! Album Project | .alb | 
other | PowerBASIC Help | .pbh | 
other | PowerBuilder Dynamic Library | .pbd | 
other | Printer Font Metrics | .pfm | 
other | Proximity Technology Lexicon/Thesaurus | .lex .ths | 
other | Psion Application Alias | .als | 
other | Psion Library | .dyl | 
other | Psion Physical Device Driver | .pdd | 
other | Psion Printer Driver | .wdr | 
other | Puzzle Buster Puzzle | .puz | 
other | Quake II Map | .bsp | 
other | Quake II Sprite Reference | .sp2 | 
other | Quake Map | .bsp | 
other | QuickText Titles |  | 
other | Reflections Camera | .kam | 
other | Reflections Data | .r3 | 
other | Reflections Material | .mat | 
other | Reflections Scene |  | 
other | Relocatable Object Module | .obj .o | 
other | RIFF MSFX File | .sfx | Just contains meta info about a given soundeffect usually distributed alongside it as a .wav
other | RIFF MxSt File | .si | References to other files, seems to be meta info only. Only info I could find, failed to process: https://github.com/dutchcoders/extract-riff
other | RIFF Palette | .pal | 
other | RIFF STYL File | .par | References a font for mac and windows and includes some text in a TEXT chunk
other | Rise of the Triad Level | .rtc .rtl | 
other | ROT Object 3D Action | .rotact | 
other | RTPatch File | .rtp | 
other | Samplitude RAM Project | .rap | 
other | Scenery Animator Landscape | .scape | 
other | SciTech Driver | .drv | 
other | Scorched Earth Mountain Data | .mtn | 
other | Sculpt 3D Take | .take | 
other | Show Partner Mastered Show | .pro | 
other | SimCity 2000 Save Game Data | .sc .sc2 | 
other | SimCity City | .cty | 
other | Slicks 'n' Slide Track | .ss | 
other | SmartDraw Template | .sdt .sdr | 
other | Snoop Capture | .snoop | 
other | SNX Snapshot | .snx | 
other | SoftDisk Library | .shl | 
other | StarCraft Map | .scm .scx | 
other | Startrekker Module Info | .nt | 
other | StarWriter Printer Driver | .gpm | 
other | StarWriter Video Driver | .hgd | 
other | StormWizard Resource | .wizard .wizard-all | 
other | Su-27 Flanker Mission | .mis | 
other | Super ZZT File | .szt | 
other | Superbase Form | .sbv | 
other | SuperJAM! File | .chords .style .section .band .keyboard .patch .drummap | 
other | symlink |  | This format is a hardcoded match at the beginning of identify.js
other | SYSLINUX loader | .sys | 
other | TADS | .t .gam | 
other | TCPDUMP Style Capture | .dmp .pcap | 
other | Telix Compiled Script | .slc | 
other | TermInfo |  | 
other | TeX Font Metric Data | .tfm | 
other | TeX Virtual Font | .vf | 
other | Thunderbyte AV | .dat .eci .ec .sig sig | 
other | TimeZone Data | .tz | 
other | Turbo Lightning Environment | .env | 
other | Turbo Modula-2 Symbol Data | .sym | 
other | Turbo Pascal Help | .hlp | 
other | Type Library | .tlb | 
other | Ulead Imageioo Thumbnail Info | .pe3 .pe4 | [5 sample files](https://telparia.com/fileFormatSamples/other/uleadImageiioThumbnailInfo/)
other | VCD Entries File | .vcd | 
other | Vektor Grafix Driver | .drv | 
other | VESA Display Identification File | .vdb | 
other | VideoTracker Routine | .rot | [10 sample files](https://telparia.com/fileFormatSamples/unsupported/videoTrackerRoutine/)
other | Vista Digital Elevation Map | .dem | 
other | Visual Basic Extension | .vbx | 
other | Visual Basic Tokenized Source | .bas | 
other | Visual FoxPro Compound Index | .cdx | 
other | Visual Smalltalk Enterprise Objects Library | .sll | 
other | Vocal-Eyes Set | .set | 
other | WarCraft Map | .pud | 
other | Windows Help Full Text Search Index | .fts | 
other | Windows Help Global Index Data | .gid | 
other | Windows LOGO Drawing Code | .lgo .lg | 
other | Windows Shim Database | .sdb | 
other | Windows Shortcut | .lnk | 
other | Winzle Puzzle | .wzl | 
other | Wipeout 2097 Track Data | .wad | 
other | WordPerfect Driver | .vrs | 
other | WordPerfect for Windows Button Bar | .wwb | 
other | WordPerfect keyboard file | .wpk | 
other | WordPerfect Macro File | .wpm .wcm | 
other | WordPerfect Printer Data | .all .prd | 
other | ZBASIC | .bas | [6 sample files](https://telparia.com/fileFormatSamples/other/zbasic/)
other | ZZT File | .zzt | 



## Poly (20)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
poly | 3D Studio Mesh | .3ds | [1 sample file](https://telparia.com/fileFormatSamples/poly/studioMesh3D/)
poly | Caligari TrueSpace 3D Object | .sobj | [7 sample files](https://telparia.com/fileFormatSamples/poly/trueSpace3D/)
poly | [Cinema 4D](http://fileformats.archiveteam.org/wiki/C4D) | .c4d .mc4d | [9 sample files](https://telparia.com/fileFormatSamples/poly/cinema4D/)
poly | [Cyber Studio/CAD-3D](http://fileformats.archiveteam.org/wiki/CAD-3D) | .3d2 .3d | [14 sample files](https://telparia.com/fileFormatSamples/poly/cyberStudioCAD3D/)
poly | Direct3D Object | .x | [1 sample file](https://telparia.com/fileFormatSamples/poly/direct3DObject/)
poly | [IFF TDDD 3-D Render Document](http://fileformats.archiveteam.org/wiki/TDDD) | .tdd .cel .obj | [18 sample files](https://telparia.com/fileFormatSamples/poly/iffTDDD/) - A 3D rendering file format. Some of these files may have been created by "Impulse 3D" I've never bothered trying to convert or render these into anything else
poly | LightWave 3D Object | .lwo .lw .lightwave | [1 sample file](https://telparia.com/fileFormatSamples/poly/lightWave/)
poly | MoRay 3D Model | .mdl | [18 sample files](https://telparia.com/fileFormatSamples/poly/moRay/)
poly | NetImmerse File | .nif | [5 sample files](https://telparia.com/fileFormatSamples/poly/netImmerse/)
poly | [NorthCAD-3D](http://fileformats.archiveteam.org/wiki/SGI_YAODL) | .n3d | 
poly | Polyfilm 3D Model | .3d | [8 sample files](https://telparia.com/fileFormatSamples/poly/polyfilm/)
poly | [POV-Ray Scene](http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description) | .pov | [1 sample file](https://telparia.com/fileFormatSamples/poly/povRay/)
poly | [Quake 2 Model](http://fileformats.archiveteam.org/wiki/MD2) | .md2 | [6 sample files](https://telparia.com/fileFormatSamples/poly/quake2Model/)
poly | [QuickDraw 3D Metafile](http://fileformats.archiveteam.org/wiki/3DMF) | .3dmf | [5 sample files](https://telparia.com/fileFormatSamples/poly/quickDraw3D/)
poly | Real 3D | .real .obj | [4 sample files](https://telparia.com/fileFormatSamples/poly/real3D/) - Realsoft 3D may be able to view/render these. See linux version in: sandbox/app/realsoft3d-8.2.tar
poly | ROT! Object | .rotobj | [5 sample files](https://telparia.com/fileFormatSamples/poly/rotObject/)
poly | Sculpt 3D Scene | .scene | [2 sample files](https://telparia.com/fileFormatSamples/poly/sculpt3DScene/) - A 3D rendering file format. I didn't bother investigating it.
poly | [SGI Yet Another Object Description Language](http://fileformats.archiveteam.org/wiki/SGI_YAODL) | .ydl | [3 sample files](https://telparia.com/fileFormatSamples/poly/ydl/)
poly | [Vertex Binary 3D Object](http://fileformats.archiveteam.org/wiki/CAD-3D) | .3d | 
poly | [Virtual Reality Modeling Language](http://fileformats.archiveteam.org/wiki/VRML) | .wrl .wrz | [1 sample file](https://telparia.com/fileFormatSamples/poly/vrml/) - A 3D rendering file format meant for the web.



## Video (15)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
video | Accent Software DemoMaker Sequence | .seq | [2 sample files](https://telparia.com/fileFormatSamples/video/accentDemoMakerSequence/)
video | Accent Software Show Sequence | .seq | [11 sample files](https://telparia.com/fileFormatSamples/video/accentShowSequence/) - Old MS-DOS software. Couldn't find a standalone player/converter, and also probably wasn't very popular.
video | Adorage Animation | .awm | [1 sample file](https://telparia.com/fileFormatSamples/video/adorageAnimation/)
video | Animation Works Movie | .awm | [5 sample files](https://telparia.com/fileFormatSamples/video/animationWorks/) - Couldn't locate a converter or extractor
video | [ClariSSA Super Smooth Animation](http://fileformats.archiveteam.org/wiki/IFF-SSA) | .ssa .anim | [7 sample files](https://telparia.com/fileFormatSamples/video/iffSSA/) - Couldn't find any working modern converter that works on any of the sample files.
video | Delphine CIN Video | .cin | [5 sample files](https://telparia.com/fileFormatSamples/video/delphineCIN/) - FFMPEG has support for something called Delphine Software International CIN, but it couldn't convert the test files
video | [Deluxe Video](http://fileformats.archiveteam.org/wiki/VDEO) |  | [1 sample file](https://telparia.com/fileFormatSamples/video/deluxeVideo/) - Couldn't find a converter for it. Could fire up an amiga with deluxe video program from Electronic Arts.
video | DK Multimedia Animation | .ani | [7 sample files](https://telparia.com/fileFormatSamples/video/dkAnimation/)
video | Magic Lantern DIFF Animation | .diff | No known converter
video | NTitler Animation | .nt | [8 sample files](https://telparia.com/fileFormatSamples/video/ntitler/) - Couldn't locate a converter or extractor. Original Amiga program is here: http://aminet.net/package/gfx/misc/ntpro
video | [Optonica Videostream VAXL](http://fileformats.archiveteam.org/wiki/VAXL) | .vaxl | [15 sample files](https://telparia.com/fileFormatSamples/video/iffVAXL/) - Could only find this potential viewer, but no download link: https://www.ultimateamiga.com/index.php?topic=9605.0
video | [Psygnosis MultiMedia Video](https://wiki.multimedia.cx/index.php?title=PMM) | .pmm | Couldn't locate a converter
video | RIFF ANIM | .paf | [9 sample files](https://telparia.com/fileFormatSamples/video/riffANIM/) - Couldn't find any evidence of this out in the public. Could very well be a proprietary format
video | [RIFF Multimedia Movie](http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie) | .mmm | [14 sample files](https://telparia.com/fileFormatSamples/video/riffMultimediaMovie/) - Couldn't find a converter or player for it
video | [Zoetrope Animation](https://elisoftware.org/w/index.php/Zoetrope_(Amiga,_3_1/2%22_Disk)_Antic_Software_-_1988_USA,_Canada_Release) | .rif | [4 sample files](https://telparia.com/fileFormatSamples/video/zoetropeAnimation/)

