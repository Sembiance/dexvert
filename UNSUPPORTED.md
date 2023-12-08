# Unsupported File Formats (933)
These formats can still be **identified** by dexvert, they just are not converted into modern ones.<br>
Some are not converted because they are not very useful, or are specific to a single application.<br>
Others are not converted because it was deemed low priority, or there are no known programs to do so.



## Archive (60)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
archive | 64LAN Container | .l64 | [2 sample files](https://telparia.com/fileFormatSamples/archive/sixtyFourLANContainer/)
archive | ABackup Disk Image | .adf | 
archive | AIX backup/restore | .img | 
archive | Aldus Zip Compressed File |  | No known extractor program.
archive | [Apple Sparse Disk Image](https://en.wikipedia.org/wiki/Sparse_image) | .sparseimage | [1 sample file](https://telparia.com/fileFormatSamples/archive/sparseImage/) - No known linux converter that I could find. Could emulate MacOS X and do: https://github.com/torarnv/sparsebundlefs/issues/7#issuecomment-326625187
archive | [AR Archive](http://fileformats.archiveteam.org/wiki/AR) | .a .lib | [11 sample files](https://telparia.com/fileFormatSamples/archive/arArchive/) - We used to convert with deark/ar but all that usually is stored inside is .o object which are not interesting and some .a files like libphobos2.a produce 9,999 files which is a lot of noise.
archive | Arts and Letters Clip Art Library | .yal | 
archive | [ASDG's File Split](https://wiki.amigaos.net/wiki/SPLT_IFF_File_Splitting) |  | 
archive | ASetup Installer Archive | .arv | [4 sample files](https://telparia.com/fileFormatSamples/archive/aSetup/) - No known extractor program.
archive | Atari Cassette Tape Image | .cas | [4 sample files](https://telparia.com/fileFormatSamples/unsupported/atariCassetteTapeImage/)
archive | Authorware Application/Package | .app .apw | [9 sample files](https://telparia.com/fileFormatSamples/archive/authorware/) - Installed the latest Authorware 7.02 (sandbox/app/) but it wouldn't open the sample files, probably because they are 'packaged'. Couldn't locate a decompilier/depackager.
archive | BeOS Installation Package | .pkg | 
archive | BeOS Resource Data | .rsrc | 
archive | BZIP Compressed Archive | .bz | [2 sample files](https://telparia.com/fileFormatSamples/archive/bzip/) - Was only in use for a very brief time and the only files I've encountered are the two samples that shipped with bzip-0.21
archive | CCS64 Cartridge | .crt .car | 
archive | Colorado Memory System Package | .cmp | 
archive | Commodore 16 Tape | .tap | 
archive | [Corel Thumbnails Archive](http://fileformats.archiveteam.org/wiki/CorelDRAW) |  | [8 sample files](https://telparia.com/fileFormatSamples/archive/corelThumbnails/) - Contains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them. Even went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed. Sent an email to the libcdr creators, to see if they know of any info on the format, but never heard back. NOTE, if the only thing in this is images, then it should be moved to image family
archive | Eschalon Setup ARCV Container |  | No known extractor program.
archive | FIZ Archive | .fiz | [8 sample files](https://telparia.com/fileFormatSamples/archive/fizArchive/) - Could not locate any info on this archive
archive | [FreeArc Archive](http://fileformats.archiveteam.org/wiki/ARC_(FreeArc)) | .arc | [1 sample file](https://telparia.com/fileFormatSamples/archive/freeArc/) - I have the bz2 linux source code, but I don't trust it to be free of malware, so haven't compiled it. Pretty rare format I imagine and it didn't really exist until 2010, so not important to support at this time.
archive | [Icon Heavn](http://fileformats.archiveteam.org/wiki/Icon_Heaven_library) | .fim | [7 sample files](https://telparia.com/fileFormatSamples/archive/iconHeaven/) - Could support it by using icon heaven under an emulated OS/2 instance. NOTE, if the only thing in this is images, then it should be moved to image family
archive | IFF LIST File |  | [18 sample files](https://telparia.com/fileFormatSamples/archive/iffLIST/) - The IFF LIST files contain 'shared' entries that are used for all chunks in the remainder of the file. In theory I could parse this file, and "extract" out by creating seperate files for each major FORM entry inside, making sure to also copy into these files the 'shared' entries, adjusting the resulting FORM lengths as needed. Couldn't find any real documentation on the LIST/SSETPROP format. See: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF
archive | [Installer VISE Package](https://en.wikipedia.org/wiki/Installer_VISE) | .mac | Haven't found non-mac files yet. They appear to be self extracting, so I could just run them under a MAC emulator to get the files out.
archive | Interchangeable Preservation Format Floppy Disk Image | .ipf | 
archive | [Interfaze Application](http://fileformats.archiveteam.org/wiki/Interfaze) | .app | [8 sample files](https://telparia.com/fileFormatSamples/archive/interfaze/)
archive | MetaCard Stack | .rev | 
archive | Micrografx Archive | .mda | 
archive | Microsoft Internet Explorer Cache | .dat | Can use this to list contents, but to extract needs to connect to the cache files which is tricky: https://github.com/libyal/libmsiecf
archive | MoPaQ Archive | .mpq | Need some sample archives. Can use this to extract: https://github.com/Kanma/MPQExtractor or https://github.com/uakfdotb/umpqx
archive | MSX Cassette Tape | .cas | 
archive | Netscape SNM Archive | .snm | [5 sample files](https://telparia.com/fileFormatSamples/archive/netscapeSNM/) - Could convert with: https://github.com/lantaoxu/Windows-Server-2003/blob/5c6fe3db626b63a384230a1aa6b92ac416b0765f/inetcore/outlookexpress/import/netscape/commimp.cpp
archive | Newton Package | .pkg | 
archive | [Omnis Studio Application](https://en.wikipedia.org/wiki/Omnis_Studio) | .dap | [1 sample file](https://telparia.com/fileFormatSamples/archive/omnisStudio/)
archive | [ORIC Disk Image](http://fileformats.archiveteam.org/wiki/DSK_(Oric)) | .dsk | [6 sample files](https://telparia.com/fileFormatSamples/archive/oricDisk/) - The sandbox/app/oric-dsk-manager program can extract these files, but I couldn't get it to run under linux, so meh.
archive | [ORIC Tape Image](http://fileformats.archiveteam.org/wiki/TAP_(Oric)) | .dat .tap | [4 sample files](https://telparia.com/fileFormatSamples/archive/oricTape/)
archive | [OS/2 FTCOMP Archive](http://fileformats.archiveteam.org/wiki/FTCOMP) |  | [6 sample files](https://telparia.com/fileFormatSamples/archive/os2FTCOMP/) - OS/2 packed file. Can be unpackde by UNPACK.EXE or UNPACK2.EXE under OS/2. Available in OS/2 Warp, so I could support these by setting up a OS emulated OS/2 machine. Maybe some day.
archive | OS/2 Installation Package | .pkg .pak | [8 sample files](https://telparia.com/fileFormatSamples/archive/os2InstallPackage/) - Could support this with OS/2 unpack if I ever emulated OS/2
archive | [Palm Web Content Record](http://fileformats.archiveteam.org/wiki/Compressed_Markup_Language) |  | [3 sample files](https://telparia.com/fileFormatSamples/archive/palmWebContentRecord/) - I could create an extractor for this format, as there doesn't appear to be any out there. These come from extracted palmQueryApplication files from deark. 		See spec here: https://lauriedavis9.tripod.com/copilot/download/Palm_File_Format_Specs.pdf#page=36 		Extra constans here: https://github.com/jichu4n/palm-os-sdk/blob/2592eaafadd803833296dad6bda4b5728ec962d8/sdk-5r4/include/Core/System/CMLConst.h
archive | Pax Archive | .pax | [8 sample files](https://telparia.com/fileFormatSamples/archive/paxArchive/) - Used in Atari ST program GEM-View
archive | [PGNPack Archive](http://fileformats.archiveteam.org/wiki/PGNPack) | .ppk | 
archive | Print Shop Deluxe Graphics Library | .psg | [2 sample files](https://telparia.com/fileFormatSamples/archive/printShopDeluxeGraphicsLibrary/) - No known extractor program.
archive | [PS1 Memory Card](https://www.psdevwiki.com/ps3/PS1_Savedata) | .mcr .mcd | [3 sample files](https://telparia.com/fileFormatSamples/archive/ps1MemoryCard/)
archive | [RED Archive](http://fileformats.archiveteam.org/wiki/RED_(Knowledge_Dynamics)) | .red | [5 sample files](https://telparia.com/fileFormatSamples/archive/redArchive/)
archive | Setup Program Archive | .mva | [6 sample files](https://telparia.com/fileFormatSamples/archive/setupMVA/)
archive | Shockwave Flash Debug | .swd | 
archive | SNATCH-IT Disk Image | .cp2 .img | 
archive | SPIS TCompress |  | 
archive | [TED5 Archive](http://www.shikadi.net/moddingwiki/TED5) | .wl1 .ck4 .ck6 | [4 sample files](https://telparia.com/fileFormatSamples/archive/ted5Archive/) - An archive format created by TED5. Used for games like Commander Keen. The format is detailed on the wiki link above, so in theory I could create an extractor for it.
archive | [The Print Shop DAT](http://fileformats.archiveteam.org/wiki/The_Print_Shop) | .dat | [1 sample file](https://telparia.com/fileFormatSamples/archive/printShopDAT/) - Deark will extract almost anything ending in .dat and produce garbage PNG files. Since we don't have a better way to identify these files, this can't be safely enabled right now.
archive | [Top Draw Shapes Archive](http://fileformats.archiveteam.org/wiki/Top_Draw) | .tds .td | [3 sample files](https://telparia.com/fileFormatSamples/archive/topDrawShapes/) - No known extractor. I could probably use the original program and figure out a way to get them out, but meh.
archive | Unix Archive - Old | .a | [8 sample files](https://telparia.com/fileFormatSamples/archive/unixArchiveOld/)
archive | Unreal Package | .ut2 .uasset | 
archive | [Viacom New Media Sprite Archive](http://www.shikadi.net/moddingwiki/Viacom_New_Media_Graphics_File_Format) | .vnm .000 | [49 sample files](https://telparia.com/fileFormatSamples/archive/viacomNewMedia/) - An obscure format that packs multiple bitmaps and sprites into a single archive. Found the following two projects that extract them: https://github.com/jmcclell/vnmgf-exporter Sadly neither one can correctly process/extract the VNM files I encountered. The github link is much closer and is in modern Go.
archive | [Warp Disk Image](http://fileformats.archiveteam.org/wiki/WRP) | .wrp | [4 sample files](https://telparia.com/fileFormatSamples/archive/wrp/) - UnWarp on the amiga wants to write directly to an floppy, which we can't easily support. https://github.com/ipr/qXpkLib has some code to unwarp, but in 10 year old lib format for Qt. However it looks somewhat self contained and so we could use this code as an example: https://github.com/ipr/qUnLZX
archive | WRAptor Archive | .wra .wr3 | [5 sample files](https://telparia.com/fileFormatSamples/archive/wraptor/) - DirMaster says it supports WR3, but couldn't get anything useful from it.
archive | WWarp Disk Image | .wwp | 
archive | XelaSoft Archive | .xsa | 
archive | ZOOM Disk Image | .zom | [1 sample file](https://telparia.com/fileFormatSamples/archive/zoomDiskImage/) - No known modern converter/extractor. Amiga program ZOOM to create and write to floppy: http://aminet.net/package/misc/fish/fish-0459
archive | ZX Spectrum TZX Tape | .tzx | 



## Audio (34)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
audio | [AdLib Instrument Bank](http://fileformats.archiveteam.org/wiki/AdLib_instrument_bank) | .bnk | [3 sample files](https://telparia.com/fileFormatSamples/audio/adLibInstrumentBank/) - These .bnk files include sounds/instruments used by adlib ROL/SNG/SX files to make music. Technically the sounds could be extracted, maybe with 'Bank Manager' for DOS, but meh. Awave Studio claims to support these, but under version 7 I couldn't get them to load.
audio | Aegis Sonix Instrument | .instr | [21 sample files](https://telparia.com/fileFormatSamples/audio/sonixInstrument/) - The sampled .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic
audio | AM Sound |  | [4 sample files](https://telparia.com/fileFormatSamples/audio/amSound/)
audio | Amiga 16VX Sound |  | [1 sample file](https://telparia.com/fileFormatSamples/audio/amiga16vx/)
audio | Art of Noise Instrument | .fm | [5 sample files](https://telparia.com/fileFormatSamples/audio/artOfNoiseInstrument/)
audio | AudioWorks Sound Sample |  | 
audio | [Creative Labs Instrument Bank](http://fileformats.archiveteam.org/wiki/Instrument_Bank) | .ibk | [2 sample files](https://telparia.com/fileFormatSamples/audio/creativeLabsInstrumentBank/) - gamemus supports reading this format, but doesn't have a way to convert or extract it
audio | [DataShow Sound File](http://www.amateur-invest.com/us_datashow.htm) | .snd | [1 sample file](https://telparia.com/fileFormatSamples/audio/dataShowSound/) - The single sample file I have is a simple text file on how to generate the sound. Probably wouldn't be too hard to create a converter for it. But it's a pretty obscure format, so probably not worth investing any time into it.
audio | Deluxe Sound Sample | .instr | 
audio | Digital Symphony Sound Sample |  | 
audio | DMS OP2 Instrument Data |  | 
audio | HomeBrew Sound | .hse | [1 sample file](https://telparia.com/fileFormatSamples/audio/homeBrewSound/)
audio | [Inverse Frequency Sound Format](http://fileformats.archiveteam.org/wiki/Inverse_Frequency_Sound_format) |  | [3 sample files](https://telparia.com/fileFormatSamples/audio/inverseFrequency/) - Used in various APOGEE games like commander keen. Didn't look that hard for a player/converter.
audio | KixTart SPK Notation | .spk | 
audio | Kurzweil K2 Sample | .kr1 .kr2 .krz | 
audio | MaxonMAGIC Sound Sample | .hsn | [8 sample files](https://telparia.com/fileFormatSamples/audio/maxonMagicSoundSample/)
audio | MED Synth Sound |  | [4 sample files](https://telparia.com/fileFormatSamples/audio/medSynthSound/)
audio | [Music Studio Sound](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .snd | [3 sample files](https://telparia.com/fileFormatSamples/audio/musicStudioSound/)
audio | [Musicline Instrument](https://www.musicline.org/) |  | [7 sample files](https://telparia.com/fileFormatSamples/audio/musiclineInstrument/)
audio | Performance Music Bank |  | 
audio | Proline Voice | .pvd | [8 sample files](https://telparia.com/fileFormatSamples/audio/prolineVoice/)
audio | Psion AICA Audio | .aik | [3 sample files](https://telparia.com/fileFormatSamples/audio/psionAIKAudio/)
audio | [Quattro Pro Sound File](http://fileformats.archiveteam.org/wiki/Quattro_Pro) | .snd | [7 sample files](https://telparia.com/fileFormatSamples/audio/quattroProSound/) - Quattro Pro 3.0 allowed creation of slide shows which could include sounds. Couldn't locate any further information on these files except that they might be soundblaster compataible. Couldn't find anything to play them.
audio | Rich Music Format | .rmf | [4 sample files](https://telparia.com/fileFormatSamples/audio/richMusicFormat/)
audio | Sonic Arranger instrument |  | No known converter
audio | Sonix Sound Sample | .ss | [18 sample files](https://telparia.com/fileFormatSamples/audio/sonixSoundSample/) - These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's
audio | [Sound Blaster Instrument](http://fileformats.archiveteam.org/wiki/Sound_Blaster_Instrument) | .sbi | [10 sample files](https://telparia.com/fileFormatSamples/audio/soundBlasterInstrument/)
audio | [SoundFont 1.0](http://fileformats.archiveteam.org/wiki/SoundFont_1.0) | .sbk | [1 sample file](https://telparia.com/fileFormatSamples/audio/soundFont1/) - Awave Studio can technically convert these, but 99.9% of all SBK SoundFond 1 files just contain meta info that points to a samples in ROM, thus there isn't anything really to convert.
audio | StoneTracker Sample | .sps | [3 sample files](https://telparia.com/fileFormatSamples/audio/stoneTrackerSample/)
audio | [STOS Sample](https://en.wikipedia.org/wiki/STOS_BASIC) | .sam | [3 sample files](https://telparia.com/fileFormatSamples/audio/stosSample/)
audio | [VQF TwinVQ](https://wiki.multimedia.cx/index.php/VQF) | .vqf | [2 sample files](https://telparia.com/fileFormatSamples/audio/vqf/) - I attempted to use TwinDec from http://www.rarewares.org/rrw/nttvqf.php but it failed to decode my sample files
audio | [WinRec DVSM](https://temlib.org/AtariForumWiki/index.php/DVSM) | .dvs | [6 sample files](https://telparia.com/fileFormatSamples/audio/dvsm/) - No known linux/windows/amiga converter
audio | [Yamaha Synthetic Music Mobile Application Format](https://lpcwiki.miraheze.org/wiki/Yamaha_SMAF) | .mmf | [1 sample file](https://telparia.com/fileFormatSamples/audio/yamahaSMAF/)
audio | ZyXEL Voice Data | .zvd .zyx | [2 sample files](https://telparia.com/fileFormatSamples/audio/zyxelVoice/)



## Document (44)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
document | Adobe InDesign Document | .indd .ind | 
document | Alan Interactive Fiction | .acd | 
document | Amiga Vision Flow | .avf | [3 sample files](https://telparia.com/fileFormatSamples/document/amigaVisionFlow/)
document | AmigaWriter Documet |  | [3 sample files](https://telparia.com/fileFormatSamples/document/amigaWriter/) - Could probably convert this with the actual AmigaWriter program (sandbox/app/amiwrite.rar) but it's manual doesn't mention anything about CLI conversion.
document | Applesoft BASIC Source Code | .bas | [2 sample files](https://telparia.com/fileFormatSamples/document/applesoftBASIC/) - Maybe I can use something like: https://github.com/AppleCommander/AppleCommander/search?q=Applesoft
document | [Astound Presentation](http://fileformats.archiveteam.org/wiki/Astound_Presentation) | .asd .smp .asv | [1 sample file](https://telparia.com/fileFormatSamples/document/astoundPresentation/)
document | [Calamus Document](http://fileformats.archiveteam.org/wiki/Calamus) | .cdk | [12 sample files](https://telparia.com/fileFormatSamples/document/calamusDocument/)
document | [CanDo Deck](https://cando.amigacity.xyz/index.php/downloads/category/7-cando-software) | .deck | [1 sample file](https://telparia.com/fileFormatSamples/document/canDoDeck/) - Could use 'DeckViewer' from above, or something else to view/convert. More info: https://randocity.com/2018/03/27/cando-an-amiga-programming-language/
document | Clarion Database File | .dat | [49 sample files](https://telparia.com/fileFormatSamples/document/clarionDatabase/) - Did a Google search, couldn't find anything about it. soffice didn't do anything with it either.
document | Cloanto C1-Text Document | .c1text | [1 sample file](https://telparia.com/fileFormatSamples/document/cloantoC1Text/) - Have only encountered just 1 file in the wild. If I encounter more, I can get Cloanto C1-Text program, load it into the Amiga and convert it there.
document | Dart Hypertext |  | [5 sample files](https://telparia.com/fileFormatSamples/document/dartHypertext/) - The DART/DART.EXE program in sandbox/apps/ can open these, it's a text format. It has no way to export as text. It can 'print' the file, but the dosbox I'm using doesn't support printing. Thus this format isn't currently supported.
document | dBASE Compiled Form | .fro .fmo | 
document | [Envision Publisher Document](http://fileformats.archiveteam.org/wiki/Envision_Publisher) | .evp .evt | [5 sample files](https://telparia.com/fileFormatSamples/document/envisionPublisherDoc/) - Envision Publisher for MSDOS doesn't have an "Export" option. I could figure out how to 'print to a file' or I could set up DOSBOX PDF Printer emulation: superuser.com/questions/270457/how-can-i-print-with-dosbox
document | [Epic TFP Document](https://www.vogons.org/viewtopic.php?f=5&t=35657&start=40) | .tfp | Used in EPIC games. Supposedly can contain hyperlinks, graphics and animations all in a single document format
document | Excellence! Document | .doc | 
document | FinalCalc Spreadsheet | .sheet | [1 sample file](https://telparia.com/fileFormatSamples/document/finalCalcSpreadsheet/)
document | [Flow Charting](http://fileformats.archiveteam.org/wiki/Flow_Charting) | .cht .fcd .gfc .pdq .fc5 .fcx | [3 sample files](https://telparia.com/fileFormatSamples/document/flowCharting/)
document | [Folio Database](http://fileformats.archiveteam.org/wiki/Folio_Infobase) | .nfo .sdw .fff .def | 
document | [Greenstreet Publisher Document/Snippet](http://fileformats.archiveteam.org/wiki/Greenstreet_Publisher) | .dtp .srp | [10 sample files](https://telparia.com/fileFormatSamples/document/greenstreetPublisher/) - I could open these just fine under Win2k with Publishing Suite 99, but it can't save in ANY other format, and print to file crashes QEMU, sigh.
document | [Hancom Word](http://fileformats.archiveteam.org/wiki/HWP) | .hwp | [1 sample file](https://telparia.com/fileFormatSamples/document/hancomWord/)
document | [HotHelp Text](http://fileformats.archiveteam.org/wiki/HotHelp) | .txt .hdr | [6 sample files](https://telparia.com/fileFormatSamples/document/hotHelpText/)
document | I.E.S. HyperText | .hyp | [6 sample files](https://telparia.com/fileFormatSamples/document/iesHyperText/)
document | InstallShield Compiled Script | .inx | [10 sample files](https://telparia.com/fileFormatSamples/document/installShieldCompiledScript/) - We used to decompile this using SID, but it produces nearly useless boilerplate content
document | InterBase/Firebird Database | .gdb .fdb | In theory I could import it into a running FireBird instance and then export to CSV/SQL, but meh.
document | InterSpread Spreadsheet |  | 
document | Lotus Symphony Worksheet | .wk1 wr1 | 
document | [Lotus Word Pro](http://fileformats.archiveteam.org/wiki/Lotus_Word_Pro) | .lwp | [1 sample file](https://telparia.com/fileFormatSamples/document/lotusWordPro/)
document | MasterCook Cookbook | .mcf | [2 sample files](https://telparia.com/fileFormatSamples/document/masterCook/) - Was able to open samples with sandbox/app/MasterCook7.iso in WinXP, but couldn't find an easy way to export all recipes to text or PDF. I could write a script that would manually open every recipe, select all the text and copy it and save to disk, like I do with MacroMedia, but meh, overkill for recipes.
document | MediaPaq DCF Catalog | .dcf | [5 sample files](https://telparia.com/fileFormatSamples/document/mediaPaqDCF/) - Metadata and thumbnails archive for MediaClips clip art CDs. NOT related to the DCF camera standard.
document | Microsoft Advisor Help | .hlp | [4 sample files](https://telparia.com/fileFormatSamples/document/microsoftAdvisorHelp/)
document | Microsoft OneNote | .one | 
document | OPHelp | .hlp | [5 sample files](https://telparia.com/fileFormatSamples/document/opHelp/) - Couldn't locate additional info for it
document | OrCAD Schematic | .sch .sht | 
document | P-Suite |  | [5 sample files](https://telparia.com/fileFormatSamples/document/pSuite/)
document | Pen Pal Database | .flr | 
document | Pen Pal Document | .wtr | 
document | [Perfect Forms](https://winworldpc.com/product/expert-perfect-forms/300) | .frm | [8 sample files](https://telparia.com/fileFormatSamples/document/perfectForms/)
document | PPrint Page | .pag | 
document | [Serif PagePlus Publication](http://fileformats.archiveteam.org/wiki/Pageplus) | .ppp .ppx .ppb .ppt | [9 sample files](https://telparia.com/fileFormatSamples/document/pagePlus/) - Could probably very easily install PagePlus 9 or 10 (NOT X9) and use it to convert to RTF/PDF, but have only encountered a single CD with these files on it so far.
document | Storybook Weaver Story | .swd .sts | 
document | TurboCalc Document | .tcd | [4 sample files](https://telparia.com/fileFormatSamples/document/turboCalc/)
document | [vCard](http://fileformats.archiveteam.org/wiki/VCard) | .vcf .vcard | [1 sample file](https://telparia.com/fileFormatSamples/document/vCard/) - Could write my own parser/converter using package libvformat
document | Vizawrite Document |  | 
document | WinFax Document | .fxm .fxr | 



## Executable (35)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
executable | a.out Executable | .o | 
executable | Adventure Game eXecutable | .agx | 
executable | AmigaOS Executable |  | 
executable | Atari Control Panel Extension Module | .cpx | [10 sample files](https://telparia.com/fileFormatSamples/executable/atariCPX/)
executable | Atari Executable | .xex | [4 sample files](https://telparia.com/fileFormatSamples/executable/xex/)
executable | Atari ST Executable |  | [11 sample files](https://telparia.com/fileFormatSamples/executable/atariSTExe/)
executable | BlackBerry Executable | .cod | 
executable | ELF Executable |  | 
executable | FM-TownsOS App | .exp | [9 sample files](https://telparia.com/fileFormatSamples/executable/fmTownsOSApp/)
executable | HP Palmtop Executable | .exm | [2 sample files](https://telparia.com/fileFormatSamples/executable/hpPalmtopExecutable/)
executable | Linux 8086 Executable |  | 
executable | Linux i386 Executable |  | 
executable | Linux OMAGIC Executable |  | 
executable | Linux ZMAGIC Exectutable |  | 
executable | Mac OS X Universal Binary |  | 
executable | Mac OS X Universal Shared Library | .dylib | 
executable | Mach-O HPPA Executable |  | 
executable | Mach-O Intel Executable |  | 
executable | Mach-O m68k Executable |  | 
executable | Mach-O PPC Executable |  | 
executable | Mach-O SPARC Executable |  | 
executable | MacOS PPC PEF Executable |  | 
executable | [Microsoft Compiled Help 2](http://fileformats.archiveteam.org/wiki/Microsoft_Help_2) | .HxS .HxI | 
executable | MIPSL ECOFF Executable |  | 
executable | MS-DOS COM Executable | .com .c0m | [4 sample files](https://telparia.com/fileFormatSamples/executable/com/)
executable | MS-DOS Driver | .sys .drv | 
executable | MSX Terminate and Stay Resident Executable | .tsr | 
executable | Palm OS Dynamic Library | .prc | 
executable | QDOS Executable |  | 
executable | RISC OS Executable |  | 
executable | Sony Playstation Executable | .exe | 
executable | SPARC Demand Paged Exe |  | 
executable | Superbase Program | .sbp | 
executable | Texas Instruments Calculator Program | .73p .82p .83p .85p .86p .89p .92p | 
executable | Xbox Executable | .xbe | [2 sample files](https://telparia.com/fileFormatSamples/executable/xBoxExecutable/)



## Font (53)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
font | 3D Construction Kit Font | .3fd | 
font | AmigaOS Outline Font | .ofnt .font | 
font | AmiWrite Font |  | 
font | Avery Font | .ff1 | 
font | Banner Mania Font | .fnt | [19 sample files](https://telparia.com/fileFormatSamples/font/bannerManiaFont/)
font | Bitmapped Signum! Font | .p24 .e24 .p9 .l30 | 
font | Borland Graphics Font | .chr .bgi | 
font | Bradford Font | .bf2 | 
font | Calamus Font | .cfn | [10 sample files](https://telparia.com/fileFormatSamples/font/calamusFont/)
font | ChiWriter Printer Font | .pft | 
font | ChiWriter Screen Font | .sft | 
font | Corel Wiffen Font | .wfn | 
font | DemoManiac Font | .font | 
font | DOS Code Page Font |  | 
font | DynaCADD Vector Font | .fnt | 
font | Envision Publisher Font | .svf | [3 sample files](https://telparia.com/fileFormatSamples/font/envisionPublisherFont/)
font | ExpertDraw Font | .expf | 
font | [F3 Font](http://fileformats.archiveteam.org/wiki/F3_font) | .f3b | 
font | FrameMaker Font | .bfont | 
font | GeoWorks GEOS Font | .fnt | 
font | GRX Font | .fnt | 
font | [IntelliFont Font](http://fileformats.archiveteam.org/wiki/IntelliFont) | .lib .type | [7 sample files](https://telparia.com/fileFormatSamples/font/intelliFont/)
font | Japanese Word Processor Kanji Font | .f00 | 
font | LaserJet Soft Font | .sfl .sfp .sft | 
font | LinkWay Font | .fmf | 
font | Lotus Impress Font | .ifl | 
font | Lotus Raster Font | .lrf | 
font | Lotus Vector Font | .lvf | 
font | MaconCAD Font | .mcfont | 
font | MacOS Font | .fnt | 
font | Matrox Font | .fnt | 
font | MSX Kanji Font |  | 
font | Personal Font Maker Font/Character Set | .fnt .set | 
font | [Portable Font Resource](http://fileformats.archiveteam.org/wiki/PFR) | .pfr | [3 sample files](https://telparia.com/fileFormatSamples/font/portableFontResource/) - Could create a custom HTML file that references the PFR and load it in Netscape 4.03 and take a screenshot.
font | PrintPartner Font | .font | 
font | Psion Font | .fon | 
font | RIPterm Font | .fnt | 
font | RISC OS Outline Font Data | outlines | 
font | Signum Font | .e24 | 
font | [Speedo Font](http://fileformats.archiveteam.org/wiki/Speedo) | .spd | [3 sample files](https://telparia.com/fileFormatSamples/font/speedo/)
font | TeX Packed Font | .pf | 
font | [TexFont Texture Mapped Font](http://fileformats.archiveteam.org/wiki/TexFont) | .txf | [6 sample files](https://telparia.com/fileFormatSamples/font/texFont/) - Using sandbox/app/glut-master/progs/texfont/showtxf.c I can render it to a cube. Could write C code to render the whole test alphabet letters and then save that to an image, but MEH.
font | TheDraw Font | .tdf | [1 sample file](https://telparia.com/fileFormatSamples/font/theDrawFont/) - Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it
font | VFONT Font | .fnt | 
font | VGAPaint 386 Font | .vfn | 
font | Westwood Font | .fnt | [3 sample files](https://telparia.com/fileFormatSamples/font/westwoodFont/)
font | Wildfire 3D Font | .3dfont | 
font | [Windows Font](http://fileformats.archiveteam.org/wiki/FNT_(Windows_Font)) | .fnt | [3 sample files](https://telparia.com/fileFormatSamples/font/windowsFont/) - Rumor has it Fony supports bitmap fonts, but I know it doesn't support vector ones like ROMAN.fnt and MODERN.fnt
font | WordUp Graphics Toolkit Font | .wfn | 
font | X-CAD Font |  | 
font | X11 Server Natural Format font | .snf | 
font | X11/NeWS Bitmap Font | .fb | 
font | X11/NeWS font family | .ff | 



## Image (88)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
image | Actor Object Graphic | .ogl | [2 sample files](https://telparia.com/fileFormatSamples/image/actorObjectGraphic/)
image | [AFLI-Editor Image](http://fileformats.archiveteam.org/wiki/AFLI-Editor) | .afl .afli | [1 sample file](https://telparia.com/fileFormatSamples/image/afl/) - Due to not having any 'MAGIC' identification or specific file size? and the rarity of any user files in the wild and that recoil+view64 will convert almost any .afl into a garbage output, dexvert doesn't support converting this file.
image | Aldus IntelliDraw Drawing | .idw | 
image | AmiDraw Drawing | .sdw | 
image | Animator PIC/CEL | .pic .cel | 
image | Applause Palette | .pal | 
image | Apple II Sprites | .spr | [1 sample file](https://telparia.com/fileFormatSamples/image/a2Sprites/) - Currently marked as unsupported because I can only really match extension and recoil2png isn't picky about what it converts resulting in a lot of 'garbage' output. Only have 1 sample file, so pretty rare format.
image | Arts and Letters Graphic | .ged | 
image | [ArtWorks Drawing](http://fileformats.archiveteam.org/wiki/Artworks) |  | [12 sample files](https://telparia.com/fileFormatSamples/image/artWorks/) - Viewer/Renderer: http://mw-software.com/software/awmodules/awrender.html
image | Artworx Drawing | .cwg | 
image | Atari ST Graph Diagram | .dia | [3 sample files](https://telparia.com/fileFormatSamples/image/atariGraphDiagram/) - No known converter. Atari ST graphing program by Hans-Christoph Ostendorf.
image | AutoCAD Shape | .shx | [6 sample files](https://telparia.com/fileFormatSamples/image/autoCADShape/)
image | AutoSketch Drawing | .skd | [5 sample files](https://telparia.com/fileFormatSamples/image/autoSketchDrawing/)
image | BBC Display RAM Dump |  | [1 sample file](https://telparia.com/fileFormatSamples/image/bbcDisplayRAM/) - While supported by abydos, due to no extension and no magic, it's impossible to detect accurately.
image | Blue Scan Drawing | .blsc | 
image | CAD Vantage Drawing | .dwg | 
image | Calamus Vector Document | .cvd | 
image | Chompsters Sprite | .spr | 
image | Claris Draw | .cdd | [1 sample file](https://telparia.com/fileFormatSamples/image/clarisDraw/)
image | Continuous Edge Graphic Bitmap | .ceg | [1 sample file](https://telparia.com/fileFormatSamples/image/continuousEdge/) - PV says it can convert these, but didn't work on my 1 and only sample file.
image | Crayola Art Studio | .art | 
image | DAUB Drawing | .dob | [1 sample file](https://telparia.com/fileFormatSamples/image/daubDrawing/)
image | DesignWorks Drawing |  | [2 sample files](https://telparia.com/fileFormatSamples/image/designWorks/)
image | Drafix Windows CAD Drawing | .cad .slb | 
image | [DraftChoice Drawing](http://www.triusinc.com/forums/viewtopic.php?t=11) | .dch | [30 sample files](https://telparia.com/fileFormatSamples/image/draftChoice/)
image | [Draw 256 Image](http://fileformats.archiveteam.org/wiki/Draw256) | .vga | [4 sample files](https://telparia.com/fileFormatSamples/image/draw256/) - Unsupported because .vga ext is too common, no known magic and converters can't be trusted to verify input file is correct before outputting garbage
image | Drawing Interchange Binary Format | .dxb | 
image | [DrawStudio Drawing](http://fileformats.archiveteam.org/wiki/DrawStudio) | .dsdr | [8 sample files](https://telparia.com/fileFormatSamples/image/drawStudio/) - Amiga program DrawStudio creates these. No known converter. DrawStudio demo available: https://aminet.net/package/gfx/edit/DrawStudioFPU
image | EasyCAD Drawing | .fcd | 
image | [Excel Chart](http://fileformats.archiveteam.org/wiki/Ascii-Art_Editor) | .xlc | [7 sample files](https://telparia.com/fileFormatSamples/image/excelChart/) - Canvas claims support for this, but I couldn't get it to convert any of my samples.
image | [Fastgraph Pixel Run Format](http://fileformats.archiveteam.org/wiki/Fastgraph_Pixel_Run_Format) | .prf | [12 sample files](https://telparia.com/fileFormatSamples/image/fastgraphPRF/) - No known converter. IMPROCES (see website) can load these images and save as GIF/PCX but sadly it's a mouse driven interface which dexvert can't automate yet.
image | [FLI Profi](http://fileformats.archiveteam.org/wiki/FLI_Profi) | .fpr .flp | [1 sample file](https://telparia.com/fileFormatSamples/image/fpr/) - Due to no known magic and how recoil2png/view64 will convert ANYTHING, we disable this for now.
image | Freelance Graphics Drawing | .drw | 
image | FXG Bitmap | .fxg | [3 sample files](https://telparia.com/fileFormatSamples/image/fxgBitmap/)
image | Generic CADD | .gcd | 
image | GraphicWorks Vector Drawing | .dvg | 
image | Greenstreet Drawing | .art | [6 sample files](https://telparia.com/fileFormatSamples/image/greenstreetDrawing/)
image | HomeBrew Icon | .hic | [1 sample file](https://telparia.com/fileFormatSamples/image/homeBrewIcon/)
image | ID Software Sprite | .spr | [3 sample files](https://telparia.com/fileFormatSamples/image/idSoftwareSprite/)
image | [IFF Retargetable Graphic](http://fileformats.archiveteam.org/wiki/RGFX) | .rgfx .rgx | [8 sample files](https://telparia.com/fileFormatSamples/image/rgfx/)
image | [Imagine Texture](http://fileformats.archiveteam.org/wiki/Imagine_Texture_File) | .itx | [5 sample files](https://telparia.com/fileFormatSamples/image/imagineTexture/)
image | Intergraph Raster RGB | .rgb | 
image | [IntroCAD Drawing](https://www.amigafuture.de/asd.php?asd_id=476) | .cad | [3 sample files](https://telparia.com/fileFormatSamples/image/introCAD/)
image | IRIS Showcase Presentation/Drawing | .sc .showcase | 
image | JAM Bitmap | .jam | 
image | KeyCAD Complete Drawing | .kcf | [7 sample files](https://telparia.com/fileFormatSamples/image/keyCADCompleteDrawing/)
image | LEONARD'S Sketch Drawing | .ogf | [6 sample files](https://telparia.com/fileFormatSamples/image/leonardsSketchDrawing/) - Fairly obscure CAD type drawing program. Not aware of any drawings that were not those that were included with the program, so format not worth supporting.
image | Lotus Smart Icon | .smi | 
image | MaconCAD Drawing | .mc2 | [1 sample file](https://telparia.com/fileFormatSamples/image/maxonCADDrawing/)
image | [Mad Studio](http://fileformats.archiveteam.org/wiki/Mad_Studio) | .gr1 .gr2 .gr3 .gr0 .mpl .msl .spr .an2 .an4 .an5 .tl4 | [12 sample files](https://telparia.com/fileFormatSamples/image/madStudio/) - Only thing that identifies it are extensions. Also the program didn't come out until 2016, so not worth supporting.
image | MegaPaint Vector | .vek | 
image | Micro Illustrator | .mic | [1 sample file](https://telparia.com/fileFormatSamples/image/microIllustrator/) - NOT the same as image/mil Micro Illustrator. Sadly. due to no known magic and how recoil2png/view64 will convert ANYTHING, we disable this for now.
image | [Micrografx Icon](http://fileformats.archiveteam.org/wiki/Micrografx_Icon) | .icn | [4 sample files](https://telparia.com/fileFormatSamples/image/micrografxIcon/) - No known converter.
image | Microsoft Border Art | .bdr | 
image | MVP Paint Animation | .af | 
image | NeoPaint Pattern | .pat | [2 sample files](https://telparia.com/fileFormatSamples/image/neoPaintPattern/) - While identified via magic as a "NeoPaint Palette" they appear to be "patterns" used as stamps in the MSDOS Neopaint program. Short of reverse engineering it, in theory dexvert could convert these to images by opening up DOS Neopaint, selecting the pattern, stamping it or filling a canvas with it and saving the image. Don't plan on bothing to actually do that though, it's a relatively obscure program and file format.
image | p.OS Workbench Icon | .info | 
image | [Painter Raster Image Format](http://fileformats.archiveteam.org/wiki/Painter_RIFF) | .rif | [2 sample files](https://telparia.com/fileFormatSamples/image/painterRIF/)
image | Paintpro Bitmap | .tb1 .ppp | 
image | PC-Draft-CAD Drawing | .dwg | 
image | [PCR Image](http://fileformats.archiveteam.org/wiki/PCR_image) | .pcr | [1 sample file](https://telparia.com/fileFormatSamples/image/pcrImage/)
image | [PETSCII Screen Code Sequence](http://fileformats.archiveteam.org/wiki/PETSCII) | .seq | [1 sample file](https://telparia.com/fileFormatSamples/image/petsciiSeq/) - Can't reliably detect this format and abydosconvert will convert a lot of things that end in .seq thare are not PETSCII code sequences
image | [Pixel Perfect](http://fileformats.archiveteam.org/wiki/Pixel_Perfect) | .pp .ppp | [1 sample file](https://telparia.com/fileFormatSamples/image/pixelPerfect/) - Can't reliably detect this format and recoil2png & view64 will convert almost any file you give it into garbage
image | [Pixie Vector](http://fileformats.archiveteam.org/wiki/Pixie_(vector_graphics)) | .pxi .pxs | [2 sample files](https://telparia.com/fileFormatSamples/image/pixie/)
image | PlayStation 3 Icon | .gim | 
image | [PMDraw](http://fileformats.archiveteam.org/wiki/PmDraw) | .pmd | [6 sample files](https://telparia.com/fileFormatSamples/image/pmDraw/) - No known converter. OS/2 drawing program. I could emulate OS/2 and run actual PMDraw and export.
image | Print Magic Graphic | .pmg | 
image | [Professional Draw Image](http://www.classicamiga.com/content/view/5037/62/) | .clips | [10 sample files](https://telparia.com/fileFormatSamples/image/professionalDraw/) - No known converter.
image | ProShape Drawing | .psp | [5 sample files](https://telparia.com/fileFormatSamples/image/proShapeDrawing/) - No known converter.
image | Quattro Pro Clip Art | .clp | 
image | [Run Length Encoded True Colour Picture](http://fileformats.archiveteam.org/wiki/Spooky_Sprites) | .tre | [5 sample files](https://telparia.com/fileFormatSamples/image/rleTRE/)
image | Satori Paint | .cvs .rir | [6 sample files](https://telparia.com/fileFormatSamples/image/satoriPaint/) - Only sample files I've encountered shipped with the actual program, thus doesn't seem worthwhile to support this image format if the files weren't really distributed.
image | Second Nature Slide Show | .cat | [7 sample files](https://telparia.com/fileFormatSamples/image/secondNatureSlideShow/) - Could probably spy on how the second nature DLL files are called when reading these files and figure out how to call the DLL myself with AutoIt. Meh.
image | SHF-XL Edit | .shx .shf | [2 sample files](https://telparia.com/fileFormatSamples/image/shfXLEdit/) - Due to no known magic and how recoil2png will convert ANYTHING, we disable this for now.
image | [Simple Vector Format](http://fileformats.archiveteam.org/wiki/Simple_Vector_Format) | .svf | [5 sample files](https://telparia.com/fileFormatSamples/image/simpleVectorFormat/)
image | SkyRoads Bitmap | .lzs | 
image | [SLP Image](http://fileformats.archiveteam.org/wiki/Age_of_Empires_Graphics_File) | .slp | [2 sample files](https://telparia.com/fileFormatSamples/image/slpImage/) - Could use SLP Editor or SLPCNVT (see sandbox/app) but both had issues opening several files and since it's just for AoE, not worth the effort.
image | Somera Graphic Format | .sgf | 
image | Telepaint | .ss .st | [7 sample files](https://telparia.com/fileFormatSamples/image/telepaint/)
image | [Teletext](http://snisurset.net/code/abydos/teletext.html) | .bin | [2 sample files](https://telparia.com/fileFormatSamples/image/teletext/) - Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on.
image | [Top Draw Drawing](http://fileformats.archiveteam.org/wiki/Top_Draw) | .tdr .td | [3 sample files](https://telparia.com/fileFormatSamples/image/topDrawDrawing/)
image | [Universal BitMap Format](http://discmaster.textfiles.com/browse/749/HACKER2.mdf/tsoft/bjim040.zip) | .ubf | [9 sample files](https://telparia.com/fileFormatSamples/image/universalBitMapFormat/)
image | [Ventura Publisher Graphic](http://fileformats.archiveteam.org/wiki/Ventura_Publisher) | .vgr | [4 sample files](https://telparia.com/fileFormatSamples/image/venturaPublisher/) - Tried both Ventura Publisher 4.1 and Corel Draw 5 (which includes it) and neither could open the sample VGR files I have.
image | Windows FAX Cover | .cpe | [5 sample files](https://telparia.com/fileFormatSamples/image/windowsFAXCover/)
image | WinFax CoverPage Image | .cvp .cv | 
image | X-CAD Drawing | .xdr | [1 sample file](https://telparia.com/fileFormatSamples/image/xCADDrawing/)
image | [xRes Image](http://fileformats.archiveteam.org/wiki/XRes) | .lrg | [6 sample files](https://telparia.com/fileFormatSamples/image/xRes/)
image | [Yanagisawa PIC2](http://fileformats.archiveteam.org/wiki/PIC2) | .p2 | [7 sample files](https://telparia.com/fileFormatSamples/image/yanagisawaPIC2/) - A request was made to add support to recoil, but that is looking unlikely: https://sourceforge.net/p/recoil/bugs/73/ 		There is a PIC2 plugin for 'xv' so maybe I could create a CLI program that leverages that to convert: https://github.com/DavidGriffith/xv/blob/master/xvpic2.c



## Music (102)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
music | Ace Tracker Module | .am | [3 sample files](https://telparia.com/fileFormatSamples/music/aceTracker/)
music | ADrum Drumkit | .kit | 
music | ADrum Track |  | 
music | Aero Studio | .aero | [2 sample files](https://telparia.com/fileFormatSamples/music/aeroStudio/)
music | All Sound Tracker Module | .ast | [2 sample files](https://telparia.com/fileFormatSamples/music/allSoundTracker/)
music | AND XSynth Module | .amx | [1 sample file](https://telparia.com/fileFormatSamples/music/andXSynth/)
music | [ANSI Music](http://artscene.textfiles.com/ansimusic/) | .mus | No known converter. Maybe easiest would be converting to MIDI? More info and samples from: http://artscene.textfiles.com/ansimusic/
music | AProSys Module | .amx | [2 sample files](https://telparia.com/fileFormatSamples/music/aProSys/)
music | Atari Digi-Mix Module | .mix | [3 sample files](https://telparia.com/fileFormatSamples/music/atariDigiMix/)
music | AXS Module | .axs | [2 sample files](https://telparia.com/fileFormatSamples/music/axsModule/)
music | AY Amadeus Chiptune | .amad | [7 sample files](https://telparia.com/fileFormatSamples/music/ayAMAD/) - Ay_Emul can play these under linux, but they don't offer a command line conversion option. Source is available (delphi) so I could add support for this feature myself. zxtune123 doesn't seem to support them either. I tried several other programs like the AY To WAV converter here without luck: https://bulba.untergrund.net/progr_e.htm
music | AY STRC Module | .strc | [1 sample file](https://telparia.com/fileFormatSamples/music/aySTRC/)
music | Beepola Module | .bbsong | [3 sample files](https://telparia.com/fileFormatSamples/music/beepola/)
music | [Beni Tracker Module](http://fileformats.archiveteam.org/wiki/Beni_Tracker_module) | .pis | [5 sample files](https://telparia.com/fileFormatSamples/music/beniTracker/)
music | BeRoTracker Module | .brt | [2 sample files](https://telparia.com/fileFormatSamples/music/beRoTracker/) - A 32bit linux 1997 player in: sandbox/app/BeRoLinuxPlayer v1.0.rar  Could get an OLD linux OS emulated: https://soft.lafibre.info/
music | Cheese Cutter Song | .ct | [3 sample files](https://telparia.com/fileFormatSamples/music/cheeseCutterSong/) - Player here https://github.com/theyamo/CheeseCutter requires D compiler gdc to build (https://wiki.gentoo.org/wiki/Dlang) but player doesn't seem to convert CLI conversion anyways
music | Chuck Biscuits/Black Artist Module | .cba | [3 sample files](https://telparia.com/fileFormatSamples/music/cba/)
music | [Creative Music System File](http://fileformats.archiveteam.org/wiki/CMS_(Creative_Music_System)) | .cms | [59 sample files](https://telparia.com/fileFormatSamples/music/cms/) - Creative Music System. Couldn't locate any information on the file format itself, nor can I find any 'converters' for it. Only way to play them is within DOSBOX by setting this in the DOSBOX config: [sblaster] sbtype  = gb sbbase  = 220 irq     = 7 dma     = 1 hdma    = 5 sbmixer = true oplmode = cms oplemu  = default oplrate = 22050 Then going into CMSPLAY, running CMSDRV.COM and then PLAYER.EXE However that just plays the file, on an infinite loop, in real time. So while in theory I could maybe make a virtual WAV sound driver under linux and then have DOSBOX play to that driver and then record the music that way, I'd have to wait for the song to play in real time and there is no info on how long the song is
music | [Creative Music System Intelligent Organ File](http://www.vgmpf.com/Wiki/index.php?title=Creative_Music_System_(DOS)) | .org | No modern converter known. The linked website states that there is a converter to convert to CMS, but I couldn't locate it.
music | [Cubase Song](http://fileformats.archiveteam.org/wiki/ALL) | .all | [1 sample file](https://telparia.com/fileFormatSamples/music/cubaseSong/)
music | CyberTracker 64 Chiptune | .ct | 
music | DeLuxe Music CMUS | .dmcs .iff | [2 sample files](https://telparia.com/fileFormatSamples/music/iffCMUS/)
music | DeLuxe Music Score |  | [2 sample files](https://telparia.com/fileFormatSamples/music/deLuxeMusicScore/) - Likely from the Deluxe Music Construction Set
music | Digital Sound Interface Kit Module | .dsm | [1 sample file](https://telparia.com/fileFormatSamples/music/digitalSoundInterfaceKit/)
music | [DigiTrekker](http://fileformats.archiveteam.org/wiki/DigiTrekker_module) | .dtm | [4 sample files](https://telparia.com/fileFormatSamples/music/digiTrekker/) - DigiTrekker for MSDOS can play these and convert to a 'SND' format, but only in 'realtime' and I couldn't determine the format of the output SND. milkytracker claims support for this format, but I couldn't get it to play any DTM files.
music | DirectMusic Segment |  | 
music | DirectMusic Style | .sty | 
music | DreamStation Module | .dss | [3 sample files](https://telparia.com/fileFormatSamples/music/dreamStation/)
music | [Drum Traker Module](http://fileformats.archiveteam.org/wiki/Drum_Traker_module) | .dtl | [15 sample files](https://telparia.com/fileFormatSamples/music/drumTraker/)
music | [Dynamic Studio Professional Module](http://fileformats.archiveteam.org/wiki/Dynamic_Studio_Professional_module) | .dsm .dsp | [3 sample files](https://telparia.com/fileFormatSamples/music/dynamicStudio/)
music | Encore Musical Notation | .enc .mus | [3 sample files](https://telparia.com/fileFormatSamples/music/encoreMusicalNotation/)
music | [Extended MOD](http://fileformats.archiveteam.org/wiki/Extended_MOD) | .emd | [2 sample files](https://telparia.com/fileFormatSamples/music/extendedMOD/)
music | FAC Soundtracker Module | .mus | 
music | [Face The Music Module](http://eab.abime.net/showthread.php?t=62254) | .ftm | [5 sample files](https://telparia.com/fileFormatSamples/music/faceTheMusic/)
music | FamiTracker Module | .fmt | [4 sample files](https://telparia.com/fileFormatSamples/music/famiTracker/) - I tried using FamiTracker under WinXP http://famitracker.com/ but it just created a WAV of zero bytes long. Maybe because I'm not emulating a sound card...
music | Finale Music Score | .mus | 
music | Flash Tracker | .fls | [5 sample files](https://telparia.com/fileFormatSamples/music/flashTracker/)
music | FMTracker Module | .fmt | [4 sample files](https://telparia.com/fileFormatSamples/music/fmTracker/)
music | Fred Editor Soundtrack |  | [2 sample files](https://telparia.com/fileFormatSamples/music/fredEditorSoundTrack/)
music | [Fuxoft AY Language](http://fileformats.archiveteam.org/wiki/Fuxoft_AY_Language) | .fxm | [8 sample files](https://telparia.com/fileFormatSamples/music/fuxoftAYLanguage/) - Ay_Emul can play these under linux, but they don't offer a command line conversion option. Source is available (delphi) so I could add support for this feature myself.
music | [GMOD Module](http://www.exotica.org.uk/wiki/MultiPlayer) | .gmod | 
music | GoatTracker Module | .sng | [6 sample files](https://telparia.com/fileFormatSamples/music/goatTracker/)
music | Improvise Music Data | .imp | [5 sample files](https://telparia.com/fileFormatSamples/unsupported/improviseMusicData/)
music | Ixalance Module | .ixs | [5 sample files](https://telparia.com/fileFormatSamples/music/ixalance/)
music | JayTrax Module | .jxs | [4 sample files](https://telparia.com/fileFormatSamples/music/jayTrax/)
music | Jeskola Buzz Module | .bmx .bmw | [3 sample files](https://telparia.com/fileFormatSamples/music/buzz/)
music | Klystrack Module | .kt | [5 sample files](https://telparia.com/fileFormatSamples/music/klystrack/)
music | Korg Song | .sng | 
music | Koustracker Module | .sok | 
music | [Master Tracker AdLib Module](http://fileformats.archiveteam.org/wiki/Master_Tracker_module) | .mtr | [4 sample files](https://telparia.com/fileFormatSamples/music/masterTracker/)
music | Master Tracks Pro | .mts | [1 sample file](https://telparia.com/fileFormatSamples/music/masterTracksPro/)
music | MaxTrax Module | .mxtx | [8 sample files](https://telparia.com/fileFormatSamples/music/maxTrax/)
music | Melody Maker Sing | .mm | 
music | MSX Moon Blaster Music | .mbm | [6 sample files](https://telparia.com/fileFormatSamples/music/msxMBM/) - Conversion works great, but kss2wav will take almost any .mbm file and convert it to garbage. No magic I can find and no current way to check output audio, so since the format is so rare, sadly need to mark it unsupported.
music | MSX Protracker Module | .pro | 
music | [Music Studio Song](http://fileformats.archiveteam.org/wiki/The_Music_Studio) | .sng | [10 sample files](https://telparia.com/fileFormatSamples/music/musicStudioSong/) - In theory the Atari program 'MIDI Music Maker' can convert .sng files to .midi
music | [Music-X Performance](http://www.retrocastaway.com/retro-computing/music-x-making-music-on-the-amiga-in-the-80s/) | .mx .perf | [6 sample files](https://telparia.com/fileFormatSamples/music/musicXPerformance/)
music | [Music-X Sequence](http://www.retrocastaway.com/retro-computing/music-x-making-music-on-the-amiga-in-the-80s/) | .seq | [6 sample files](https://telparia.com/fileFormatSamples/music/musicXSequence/)
music | MusicMaker Module | .mm8 | [5 sample files](https://telparia.com/fileFormatSamples/music/musicMakerModule/)
music | MVSTracker Module | .mus | [2 sample files](https://telparia.com/fileFormatSamples/music/mvsTracker/)
music | MVX Module | .mvm | [4 sample files](https://telparia.com/fileFormatSamples/music/mvxModule/)
music | NerdTracker Module | .ned | [4 sample files](https://telparia.com/fileFormatSamples/music/nerdTracker/)
music | NoiseRunner Module | .nr | [1 sample file](https://telparia.com/fileFormatSamples/music/noiseRunner/)
music | [NoiseTrekker Module](http://fileformats.archiveteam.org/wiki/Noisetrekker_module) | .ntk | [5 sample files](https://telparia.com/fileFormatSamples/music/noiseTrekker/)
music | Onyx Music File Module | .omf | [4 sample files](https://telparia.com/fileFormatSamples/music/onyxMusicFile/)
music | Organya Module | .org | [7 sample files](https://telparia.com/fileFormatSamples/music/organya/)
music | Palladix | .plx | [3 sample files](https://telparia.com/fileFormatSamples/music/palladix/)
music | Paragon 5 Gameboy Tracker Module | .mgb | [4 sample files](https://telparia.com/fileFormatSamples/music/gameboyTracker/)
music | Piston Collage Module | .ptcop | [6 sample files](https://telparia.com/fileFormatSamples/music/pistonCollage/)
music | PlayerPro Module | .mad | [6 sample files](https://telparia.com/fileFormatSamples/music/playerPro/)
music | PollyTracker Module | .mod | [4 sample files](https://telparia.com/fileFormatSamples/music/pollyTracker/)
music | Pro Trekkr Module | .ixs | [6 sample files](https://telparia.com/fileFormatSamples/music/proTrekkr/)
music | Psycle Module | .psy | [4 sample files](https://telparia.com/fileFormatSamples/music/psycle/)
music | [Quartet 4V Module](http://fileformats.archiveteam.org/wiki/4v) | .4v | [9 sample files](https://telparia.com/fileFormatSamples/music/quartet4V/)
music | RamTracker Module | .trk | [4 sample files](https://telparia.com/fileFormatSamples/music/ramTracker/)
music | [Renoise Module](http://fileformats.archiveteam.org/wiki/Renoise_song) | .xrns .rns | [8 sample files](https://telparia.com/fileFormatSamples/music/renoise/) - The XRNS format is just a ZIP file with samples inside as FLACS and a song XML. The archive/zip format will end up handling that. I tried using renoise program, but it doesn't have CLI conversion nor did it even work anyways to render a song. Sigh.
music | Roland MIDI Music Recorder Song | .sng | 
music | Roland Music Sequence | .svq | [7 sample files](https://telparia.com/fileFormatSamples/music/rolandMusicSequence/) - Awave Studio claims support for these, but I was not able to get it to convert any SVQ files.
music | SBStudio Module | .pac | [3 sample files](https://telparia.com/fileFormatSamples/music/sbStudio/)
music | Scrull Music File | .smf | 
music | Sequencer One Song | .one | 
music | ShroomPlayer Module | .sho | [5 sample files](https://telparia.com/fileFormatSamples/music/shroomPlayer/)
music | Skale Tracker Module | .skm | [5 sample files](https://telparia.com/fileFormatSamples/music/skaleTracker/)
music | Sound Club Module | .sn .sn2 | [9 sample files](https://telparia.com/fileFormatSamples/music/soundClub/)
music | [Soundtrakker 128](http://justsolve.archiveteam.org/wiki/Soundtrakker_128_module) | .128 | [3 sample files](https://telparia.com/fileFormatSamples/music/soundtrakker128/) - No known converter. The sample files identify as Soundtrakker 128, but not sure if they really are or not.
music | Squirrel Module | .sqm | [1 sample file](https://telparia.com/fileFormatSamples/music/squirrelModule/)
music | [Star 3 MIDI Karaoke](https://wiki.multimedia.cx/index.php?title=Star_3) | .st3 | [3 sample files](https://telparia.com/fileFormatSamples/music/star3MIDIKaraoke/)
music | STarKos Module | .psy | [4 sample files](https://telparia.com/fileFormatSamples/music/starkos/)
music | StoneTracker Module | .spm .sps | [6 sample files](https://telparia.com/fileFormatSamples/music/stoneTracker/)
music | SunVox Module | .psy | [4 sample files](https://telparia.com/fileFormatSamples/music/sunVox/)
music | [SVArTracker Module](https://www.kvraudio.com/product/svartracker-by-svar-software) | .svar | [3 sample files](https://telparia.com/fileFormatSamples/music/svarTracker/) - I tried using sandbox/app/svartracker_1_22_free_inst.exe under win2k but got lots of errors and couldn't even figure out how to 'render' the file to WAV, VERY clumsy program and only a tiny handful of songs seem to exist for it.
music | Sweet Sixteen Song | .sng | 
music | Synder SNG-Player Module | .sng | [5 sample files](https://telparia.com/fileFormatSamples/music/synderSNG/) - An old 32bit linux player binary can be found sandbox/app/Synder SNG-Player Linux32 build 2008-05-19.rar   Could get an OLD linux OS and install: https://soft.lafibre.info/
music | Synder Tracker Module | .sng | [2 sample files](https://telparia.com/fileFormatSamples/music/synderTrackerModule/)
music | T'SoundSystem Source Module | .tss | [4 sample files](https://telparia.com/fileFormatSamples/music/tss/)
music | TechnoSound Turbo 2 Track | .track | [1 sample file](https://telparia.com/fileFormatSamples/music/technoSoundTurbo2Track/)
music | The 0ok Amazing Synth Tracker Module | .t0ast | [4 sample files](https://telparia.com/fileFormatSamples/music/t0ast/)
music | TraX Music Track | .mts | [5 sample files](https://telparia.com/fileFormatSamples/music/traXTrack/)
music | VGM Music Maker Module | .vge | [4 sample files](https://telparia.com/fileFormatSamples/music/vgmMusicMaker/)
music | Vic-Tracker Module | .vt | [5 sample files](https://telparia.com/fileFormatSamples/music/vicTracker/)
music | Wanton Packer | .wn | [1 sample file](https://telparia.com/fileFormatSamples/music/wantonPacker/)
music | Yamaha e-SEQ Music | .esq .fil | 



## Other (440)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
other | 3D Construction Kit Area | .3ad | 
other | 3D Construction Kit Brushes | .3bd | 
other | 3D Construction Kit Object | .3od .obj | 
other | 3D Construction Kit Shape Data | .3sd | 
other | 3D Construction Kit World Data | .kwd .kit | 
other | 3D Movie Maker | .3mm .3th .chk .3cn | 
other | 3D Studio Project | .prj | 
other | 3DFX Glide driver | .dxe | 
other | 4D Paint Project | .4dp | [1 sample file](https://telparia.com/fileFormatSamples/other/fourDPaintProject/)
other | Abuse Level | .lvl .spe | 
other | ActivInspire Flipchart | .flipchart | 
other | Actor Image Snapshot | .ima | 
other | Adobe Duotone Options | .ado | 
other | Adobe Hyphenation/Spelling Dictionary | .hyp | 
other | Adobe Multiple Master Metrics | .mmm | 
other | Adobe Photoshop Color Book | .acb | 
other | Adobe Photoshop Custom Shape | .csh | 
other | Adobe Photoshop Gradient | .grd | 
other | Adobe Type Manager Font Information | .inf | 
other | Adorage preferences |  | 
other | Adventure Game Toolkit Strings | .d$$ | 
other | Aegis Impact! Slideshow | .sld | 
other | Aegis Pro Motion Geometry | .geo | 
other | AIBB load Module | .module .aibb | 
other | Alchemy Mindworks Resource | .res | 
other | Allways Printer Driver | .apc .apd .apf | 
other | Alpha Four Script | .scp | 
other | Altera Waveform Design File | .wdf | 
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
other | AMOS Datas Bank | .abk | [8 sample files](https://telparia.com/fileFormatSamples/unsupported/amosDatasBank/)
other | AMOS Work Bank | .abk | 
other | AniMouse Tutorial | .sdemo | 
other | ApAssist Compressed Data |  | 
other | ArtEffect Brush |  | 
other | ArtEffect Convolution |  | 
other | ASCII Font Metrics | .afm | 
other | Astound Actor | .act | 
other | Atari 7800 ROM | .a78 | 
other | Atari CTB File | .ctb | [5 sample files](https://telparia.com/fileFormatSamples/unsupported/atariCTBFile/)
other | Atari GEM OBM File | .obm | [15 sample files](https://telparia.com/fileFormatSamples/unsupported/atariGEMOBM/)
other | Audio Interface Library 3 Digital audio driver | .dig | 
other | Audio Interface Library 3 Music/MIDI driver | .mdi | 
other | Authorware Library | .apl | 
other | AutoCAD Compiled Menu | .mnx | 
other | Autocad DOS Real Mode ADI Driver | .exp .ex% | 
other | AutoCAD Protected LISP | .lsp | 
other | AutoDesk 3D-Studio Material Library | .mli | 
other | AVS Video Editor Project | .vep | 
other | Babble! Data | .bab | 
other | Bars and Pipes File | .gchone .gchord .song | 
other | BeOS CodeWarrior Project | .proj | 
other | Berkeley DB | .db | 
other | Bill of Materials | .bom | 
other | Binary Color Format | .bcf | 
other | Binary Delta Compressed Patch |  | 
other | BinPatch Patch | .utp | 
other | Block Breaker Pattern | .blc | 
other | BNUPORT Patch Table | .pat | 
other | Bolo Map |  | 
other | Borland Delphi Compiled Unit | .dcu | 
other | Borland Graphics Interface Driver | .bgi | 
other | Borland Language Library | .bll | 
other | Borland Overlay | .ovr | 
other | BOYAN Action Model | .bam | 
other | Build Engine Demo Data | .dem | 
other | Butcher Shape | .shape | 
other | BWSB Music and Sound Engine Driver | .mse | 
other | CAD/Draw Library | .tbl | 
other | CAD/Draw Settings | .mpi | 
other | Cakewalk Studio Ware Panel | .CakewalkStudioWare | 
other | CakeWalk Work File | .wrk | 
other | Calamus Farb Color Table | .cft .cf | 
other | Calamus Raster Information | .cri .cr | 
other | Calamus Text Style List | .csl .cs | 
other | Caligari TrueSpace Data |  | 
other | Call of Duty Map | .d3dbsp .bsp | 
other | CHAOSultdGEM Parameters | .chs | [8 sample files](https://telparia.com/fileFormatSamples/unsupported/chaosultdGEMParameters/)
other | Character Table Library | .tlb | 
other | Chemview Animation Data | .d | 
other | Chess Assistant File | .bic .bid .bim .bis .lib .bfi .dsc .ndx .bdy | 
other | Clipper Pre-Linked Library | .pll | 
other | CloneCD CDImage SubChannel Data | .sub | 
other | CodeWarrior Project | .mcp | 
other | COFF Library | .lib .obj .a | 
other | Compiled AppleScript Script |  | [2 sample files](https://telparia.com/fileFormatSamples/unsupported/appleScriptCompiled/)
other | Confusion and Light Compressed Data | .cal | 
other | Cool Page Project | .cpg | 
other | Corel Editor Macro | .edm | 
other | COREL Photo Paint User Defined Filter | .usr | 
other | Corel PhotoPaint Tone Curve | .crv | 
other | Corel Shell Macro | .shm | 
other | Corncob 3D Data File | .cct | 
other | Cornel Huth Compressed Library | .li_ | 
other | Cracklib Password Index | .pwi | 
other | Create Adventure Games Project | .cag | 
other | Create+Shade Lights | .lights | 
other | Creative Graphics Library Driver | .cgl | 
other | Creative Signal Processor Microcode | .csp | 
other | Crystal Atari Browser Module | .mdl | 
other | Cubase Drum Map | .drm | 
other | Cybervision Monitor Info |  | 
other | Cygnus Editor Default Settings |  | 
other | Cygnus Editor Macros |  | 
other | Datastore Database |  | 
other | dBase Compiled Object Program | .dbo | 
other | dBase Index File | .ntx | 
other | dBase Query | .qbe | 
other | dBase Update | .upd | 
other | DeHackEd Patch | .deh | 
other | DemoManiac Vectors | .dat | 
other | DemoShield Demo | .dbd .bdd | 
other | Descent Level | .rdl | 
other | Diablo 1 Item Safe | .itm | 
other | Digita Organiser Theme |  | 
other | Directory Opus Settings |  | 
other | Dive File Format | .dff | 
other | DOOM Save Game | .dsg | 
other | Dr. Hardware Sysinfo | .dat | 
other | Dr.Web Anti-Virus Database | .vdb | 
other | DrawStudio Gradient |  | 
other | DrawStudio Pattern |  | 
other | Dreamcast Disc | .bin | 
other | Dune II Saved Game | .dat | 
other | DVD Info File | .ifo .bup | 
other | Dynamic Message System File | .msg | 
other | Dynamix Bitnmap | .bmp | 
other | Electronic Arts LIB container | .lib | 
other | Emacs Compiled Lisp | .elc | [8 sample files](https://telparia.com/fileFormatSamples/unsupported/emacsCompiledLisp/) - Could decompile it with: https://github.com/rocky/elisp-decompile
other | Ensoniq VFX Patch File | .vfx | 
other | ESRI ArcInfo Coverage Annotation |  | 
other | ESRI ArcInfo Grid NIT | .nit | 
other | ESRI Spatial Index |  | 
other | ESRI/ArcView DataBase Index | .shx | 
other | Expressware Printer Definition File | .pdf | 
other | F1GP-Ed Data | .events .settings | 
other | Fiasco Database File | .fdat .fidx .frec .fdb .fpr | 
other | File Express Index Header | .ixh | 
other | File Express Quick Scan | .qss | 
other | Flashback Object | .obj | 
other | Flight Sim Toolkit Terrain Data | .ftd | 
other | FoxBase Multiple Index | .mdx | 
other | FoxPro Compound Index | .tdx .edx | 
other | FoxPro Memo File | .fpt | 
other | Fractal Design Painter Paper Texture | .pap | 
other | Fractal Weave Parameters | .wwv | 
other | Front Page Binary-Tree Index | .btr | 
other | Full Tilt Pinball Data | .dat | 
other | Game Boy Advance ROM | .gba | 
other | Game Boy ROM | .gb .gbc | 
other | Game Gear ROM | .gg | 
other | GammaCAD Document | .sym .gc1 | 
other | Gee! Printer Driver | .pdr | 
other | GeoWorks GEOS Data | .000 .001 .002 .003 .004 .005 .006 .007 .008 .009 .010 .011 .012 .geo | 
other | Gettext Machine Object | .gmo | 
other | GfxLab24 Convolution Matrix |  | 
other | GfxLab24 Filter |  | 
other | [glibc Locale File](http://fileformats.archiveteam.org/wiki/Microsoft_Agent_character) |  | [9 sample files](https://telparia.com/fileFormatSamples/other/glibcLocaleFile/)
other | GoDot C64 Image Processing |  | 
other | GW-BASIC Protected Source | .bas | 
other | Half-Life 2 Save Game | .sav | 
other | High Speed Pascal Unit | .unit | 
other | HomeBrew Level | .hle | 
other | HomeBrew Palette | .hpa | 
other | HomeBrew Tile | .hti | 
other | HotMap VBX Regions Description | .hmd | 
other | Human Machine Interfaces Sound Driver | .386 | 
other | HyperPAD Pad | .pad | 
other | iBrowse Global Cache |  | 
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
other | International Patching System | .ips | 
other | Java Class File | .class | [4 sample files](https://telparia.com/fileFormatSamples/unsupported/javaClass/)
other | Javelin Printer Driver | .pr .pr2 | 
other | Jazz Jackrabbit File | .0sc .0fn | 
other | Kapersky Anti-Virus License Key | .key | 
other | KICK-Pascal Unit Interface | .u | 
other | KiSS CEL Color Palette | .kcf | 
other | Klik'n'Play Game | .gam | 
other | Kodak Precision Transform | .pt | 
other | KOLEKO Save State | .rom | 
other | KORG File | .pcg .bsq .arr .sty .sng | 
other | KryoFlux Raw Stream | .raw | [1 sample file](https://telparia.com/fileFormatSamples/unsupported/kryoFluxRawStream/)
other | LabView Virtual Instrument | .vi | 
other | LDIFF Differences Data | .lzd | 
other | Legend of Kyrandia EMC File | .emc | 
other | LIFE 3000 Status | .lif | 
other | Linux 8086 Object File | .o | 
other | Linux i386 Object File | .o | 
other | Linux Kernel |  | 
other | Linux Swap File |  | 
other | LogicSim Circuit |  | 
other | Lotus 1-2-3 Formatting Data | .fm3 | 
other | Lotus 1-2-3 SQZ! Compressed | wq! | 
other | Lotus Approach View | .vew | 
other | Lotus Freelance Presentation | .prz | 
other | Lotus Magellan Viewer | .vw2 | 
other | Lua bytecode |  | 
other | LucasFilm Data | .lfd | 
other | Mach-O HPPA Object | .o | 
other | Mach-O m68k Object | .o | 
other | Mach-O Object | .o | 
other | Mach-O SPARC Object | .o | 
other | Macromedia Xtra Cache | .mch | 
other | Maestro Music |  | 
other | MagiC64 Preferences | .prefs | 
other | MapBrowser/MapWriter Vector Map Data | cbd | 
other | Maple Common Binary | .m | 
other | MASI Music Driver | .mus | 
other | MathCad Document | .mcd | 
other | Maxon Resource Creation Tool Data | .rct | 
other | MDIFF Patch File | .mdf | 
other | MegaPaint Printer Driver | .trb | 
other | MegaZeux Board | .mzb | 
other | MegaZeux Save | .sav | 
other | MegaZeux World | .mzx | [3 sample files](https://telparia.com/fileFormatSamples/other/megaZeuxWorld/)
other | Memory Manager Resource Data |  | 
other | MetaCreations Resource Composite File |  | 
other | Micro Focus File | .dat | 
other | Micro Focus Index File | .idx | 
other | Micro Lathe Object | .lat | 
other | [Microsoft Agent Character](http://fileformats.archiveteam.org/wiki/Microsoft_Agent_character) | .acs .acf .aca | [4 sample files](https://telparia.com/fileFormatSamples/other/microsoftAgentCharacter/) - Step 1 would just be extracting the embedded images and audio. Full file format details available in sandbox/txt/MSAgentDataSpecification_v1_4.htm 		Bonus points: Animate the character in a couple poses/animations and create animated GIFs
other | [Microsoft Comic Chat Character](http://fileformats.archiveteam.org/wiki/Microsoft_Comic_Chat) | .avb | [5 sample files](https://telparia.com/fileFormatSamples/other/microsoftChatCharacter/)
other | Microsoft DirectInput Force Feedback Effect | .ffe | 
other | Microsoft DirectMusic Segments Type | .sgt | 
other | Microsoft FastFind Index | .ffx | 
other | Microsoft Incremental Linker Data | .ilk | 
other | Microsoft Printer Definition | .prd | 
other | Microsoft Private Key | .pkv | 
other | Microsoft Program Database | .pdb | 
other | Microsoft Security Catalog | .cat | 
other | Microsoft Separate Debug Format | .dbg | 
other | Microsoft Serialized Certificate Store | .sst | 
other | Microsoft Visual C Files | .bsc .sbr .wsp | 
other | Microsoft Visual C Library | .lib | 
other | Microsoft Windows Program Information File | .pif | 
other | Microsoft Word Glossary | .gly | 
other | Microsoft Word Style Sheet | .sty | 
other | MIDI Drum Machine | .drm | Program and source at: /browse/111/130%20MIDI%20Tool%20Box.iso/drum
other | MIDI-MAZE II Maze | .mze | 
other | Miles Sound System Driver | .adv | 
other | Moonbase Game Data | .mb | 
other | MS-DOS Code Page Info | .cp .cpi | 
other | MUI Builder Project | .muib | 
other | MySQL Index | .myi | 
other | MySQL Table Definition | .frm | 
other | NeoPaint Palette | .pal | 
other | NeoPaint Printer Driver | .prd | 
other | Nero Cover Designer | .bcd | 
other | NetCDF | .nc | 
other | Netscape Address Book | .nab | 
other | NetShield Virus Pattern Library | .dat | 
other | Netware Loadable Module | .nlm | 
other | Netware Message | .msg | 
other | Nintendo 64 ROM | .v64 | 
other | Nintendo ROM | .nes | 
other | Norton Change Directory Info | .ncd | 
other | Novell System PrintDef Device Definition | .pdf | 
other | NWiper Show | .nw | 
other | Oberon Symbol | .sym | 
other | OLB Library |  | [7 sample files](https://telparia.com/fileFormatSamples/unsupported/olbLib/)
other | OS/2 Device Driver | .sys | 
other | OS/2 Dynamic Link Library | .dll | 
other | OS/2 Extended File Attributes |  | 
other | OS9/68k Module |  | 
other | PA-RISC Object Code | .o | 
other | Painter's Apprentice Printer Info | .pri | 
other | PaperPort Slide Show | .fss | 
other | Papillon Palette | .pal .ppal | 
other | Pascal Compiled Unit | .tpu .ppu | 
other | PatchMeister Driver | .pmdriver | 
other | PCAnywhere Data | .bhf | 
other | Peak Graphical Waveform | .pk | 
other | PGP Key Ring | .key .pgp | 
other | PhotoImpressions Album | .abm | 
other | Platinen Layout Program Layout | .pla | 
other | Platinen Layout Programm Bibliotheken/library | .bib | 
other | Polyfilm Preferences | .prf | 
other | Ports of Call Save Game | .trp | 
other | Power Up! Album Project | .alb | 
other | PowerBASIC Help | .pbh | 
other | PowerBuilder Dynamic Library | .pbd | 
other | Printer Font Metrics | .pfm | 
other | Proximity Technology Lexicon/Thesaurus | .lex .ths | 
other | PRS Format Resource Data | .prs | 
other | Psion Application Alias | .als | 
other | Psion Library | .dyl | 
other | Psion Physical Device Driver | .pdd | 
other | Psion Printer Driver | .wdr | 
other | Puzzle Buster Puzzle | .puz | 
other | QL Plugin-ROM |  | 
other | Qt Message | .qm | 
other | Quake II Map | .bsp | 
other | Quake II Sprite Reference | .sp2 | 
other | Quake III Map | .bsp | 
other | Quake Map | .bsp | 
other | QuickText Titles |  | 
other | QuickTime Installer Cache | .qdat .qda | 
other | Raptor GLB Encrypted Container | .glb | 
other | Raven Software Compiled Script | .ibi | 
other | RealBasic Project | .rbp | 
other | Reflections Camera | .kam | 
other | Reflections Data | .r3 | 
other | Reflections Material | .mat | 
other | Reflections Scene |  | 
other | Relocatable Object Module | .obj .o | 
other | RFFlow Diagram | .flo | 
other | RIFF MSFX File | .sfx | Just contains meta info about a given soundeffect usually distributed alongside it as a .wav
other | RIFF MxSt File | .si | References to other files, seems to be meta info only. Only info I could find, failed to process: https://github.com/dutchcoders/extract-riff
other | RIFF Palette | .pal | 
other | RIFF STYL File | .par | References a font for mac and windows and includes some text in a TEXT chunk
other | RISC OS ALF Library |  | 
other | RISC OS ARM Object File |  | 
other | Rise of the Triad Level | .rtc .rtl | 
other | ROT Object 3D Action | .rotact | 
other | RPG Maker Map | .lmu | EasyRPG-Tools has lmu2png but requires lots of aux files and I couldn't get it to work
other | RTPatch File | .rtp | 
other | Samplitude Project | .rap .vip | 
other | Scenery Animator Landscape | .scape | 
other | SciTech Driver | .drv | 
other | Scorched Earth Mountain Data | .mtn | 
other | Sculpt 3D Take | .take | 
other | SCUMM main data container |  | 
other | Sega Genesis/Megadrive/32x ROM | .bin .md | 
other | Sega Master System ROM | .sms | 
other | Settlers II Map | .swd .wld | 
other | SGML Compiled | .mtl | 
other | Show Partner Mastered Show | .pro | 
other | SimCity 2000 Save Game Data | .sc .sc2 | 
other | SimCity City | .cty | 
other | Skunny Kart Library Game Data | .lid | 
other | Slicks 'n' Slide Track | .ss | 
other | SmartDraw Template | .sdt .sdr | 
other | Sniffer Capture | .snf .trc | 
other | Snoop Capture | .snoop | 
other | SNX Snapshot | .snx | 
other | SoftDisk Library | .shl | 
other | Sonix MIDI Instrument | .instr | 
other | Sound Forge Peak Data | .sfk | 
other | Sound Images Sound Driver | .bin | 
other | Speculator Snapshot | .zx82 .zx | 
other | SQLite2 Database | .sqlite .sqlite2 .db | 
other | StarCraft Map | .scm .scx | 
other | StarCraft Replay | .rep | 
other | Startrekker Module Info | .nt | 
other | StarWriter Formula | .frm | 
other | StarWriter Printer Driver | .gpm | 
other | StarWriter Video Driver | .hgd | 
other | StormWizard Resource | .wizard .wizard-all | 
other | Su-27 Flanker Mission | .mis | 
other | Super ZZT File | .szt | 
other | Superbase Form | .sbv | 
other | SuperJAM! File | .chords .style .section .band .keyboard .patch .drummap | 
other | symlink |  | This format is a hardcoded match at the beginning of identify.js
other | Syslinux COM32 Module | .c32 | 
other | SYSLINUX loader | .sys | 
other | TADS | .t .gam | 
other | TCPDUMP Style Capture | .dmp .pcap | 
other | Telix Compiled Script | .slc | 
other | TermInfo |  | 
other | TeX Font Metric Data | .tfm | 
other | TeX Virtual Font | .vf | 
other | Texas Instruments Calculator Backup | .73b .82b .83b .85b .86b .89b .92b | 
other | Thunderbyte AV | .dat .eci .ec .sig sig | 
other | THX Tracker Instrument | .ins | 
other | TimeZone Data | .tz | 
other | Turbo Lightning Environment | .env | 
other | Turbo Modula-2 Symbol Data | .sym | 
other | Turbo Pascal Help | .hlp | 
other | TVPaint Project | .tvpp .deep .aur | 
other | Type Library | .tlb | 
other | Ulead Imageioo Thumbnail Info | .pe3 .pe4 | [5 sample files](https://telparia.com/fileFormatSamples/other/uleadImageiioThumbnailInfo/)
other | Valve Source Map | .bsp | 
other | VCD Entries File | .vcd | 
other | Vectrex Game ROM | .vec .gam .bin | 
other | Vektor Grafix Driver | .drv | 
other | VESA Display Identification File | .vdb | 
other | Video Music Box Progression | .prgn | 
other | Video Music Box Style | .stle | 
other | VideoFX2 Sequence | .seq | 
other | VideoPad Project | .vpj | 
other | VideoTracker Routine | .rot | [10 sample files](https://telparia.com/fileFormatSamples/unsupported/videoTrackerRoutine/)
other | Visionaire Mesh | .mesh | 
other | Visionaire Project | .vis | 
other | Vista Digital Elevation Map | .dem | 
other | Vista Makepath Session | .ses | 
other | Visual Basic Extension | .vbx | 
other | Visual Basic Tokenized Source | .bas | 
other | Visual FoxPro Compound Index | .cdx | 
other | Visual Smalltalk Enterprise Objects Library | .sll | 
other | Visual SourceSafe Control File | .scc | 
other | Vocal-Eyes Set | .set | 
other | WarCraft III Map | .w3m | 
other | WarCraft III Recorded Game | .w3g | 
other | WarCraft Map | .pud | 
other | Watcom Profiler Sampling Data | .smp | 
other | Winamp Advanced Visualization Studio File | .avs | 
other | Windows Calendar | .cal | 
other | Windows Help Full Text Search Index | .fts | 
other | Windows Help Global Index Data | .gid | 
other | Windows LOGO Drawing Code | .lgo .lg | 
other | Windows Shim Database | .sdb | 
other | Windows Shortcut | .lnk | 
other | Wipeout 2097 Track Data | .wad | 
other | WordPerfect Driver | .vrs | 
other | WordPerfect for Windows Button Bar | .wwb | 
other | WordPerfect keyboard file | .wpk | 
other | WordPerfect Macro File | .wpm .wcm | 
other | WordPerfect Printer Data | .all .prd | 
other | WordStar Printer Description File | .pdf | 
other | WordWorth Preferences |  | 
other | X-CAD Modifier Table | .obj | 
other | X-CAD Overlay |  | 
other | XPCOM Type Library | .xpt | 
other | YAFA Compression Options |  | 
other | ZBASIC | .bas | [6 sample files](https://telparia.com/fileFormatSamples/other/zbasic/)
other | ZSNES Save State | .zst | 



## Poly (52)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
poly | 3-D Professional Scene |  | 
poly | 3D Dgf Model | .dgf .3dgfo | 
poly | 3D Studio Loft Object | .lft | 
poly | [3D Studio Mesh](http://fileformats.archiveteam.org/wiki/3DS) | .3ds | [2 sample files](https://telparia.com/fileFormatSamples/poly/studioMesh3D/)
poly | Amapi 3D Model | .a3d .x | 
poly | AutoShade Rendering Slide | .rnd | 
poly | Blender 3D | .blend | 
poly | [Blitz3D Object](http://fileformats.archiveteam.org/wiki/Blitz3D_Model) | .b3d | 
poly | [Caligari TrueSpace 3D Object](http://fileformats.archiveteam.org/wiki/Caligari_trueSpace) | .sobj | [7 sample files](https://telparia.com/fileFormatSamples/poly/trueSpace3D/)
poly | [Cinema 4D](http://fileformats.archiveteam.org/wiki/C4D) | .c4d .mc4d | [12 sample files](https://telparia.com/fileFormatSamples/poly/cinema4D/)
poly | Create+Shade 3D Scene | .3d | 
poly | [Cyber Studio/CAD-3D](http://fileformats.archiveteam.org/wiki/CAD-3D) | .3d2 .3d | [14 sample files](https://telparia.com/fileFormatSamples/poly/cyberStudioCAD3D/)
poly | Direct3D Object | .x | [1 sample file](https://telparia.com/fileFormatSamples/poly/direct3DObject/)
poly | DynaCADD Part | .prt .dpt | 
poly | Electric Image 3D File | .fact | 
poly | ESRI/ArcView Shape | .shp | 
poly | Half Life Model | .mdl | [12 sample files](https://telparia.com/fileFormatSamples/poly/halfLifeModel/)
poly | [IFF TDDD 3-D Render Document](http://fileformats.archiveteam.org/wiki/TDDD) | .tdd .cel .obj | [18 sample files](https://telparia.com/fileFormatSamples/poly/iffTDDD/) - A 3D rendering file format. Some of these files may have been created by "Impulse 3D" I've never bothered trying to convert or render these into anything else
poly | Infini-D Scene | .ids .id4 | 
poly | Kaydara Filmbox Model | .fbx | 
poly | [LightWave 3D Object](http://fileformats.archiveteam.org/wiki/LightWave_Object) | .lwo .lw .lightwave | [1 sample file](https://telparia.com/fileFormatSamples/poly/lightWave/)
poly | Maya Scene | .mb | 
poly | MilkShape 3D Model | .ms3d | 
poly | [Mobile 3D Graphic](http://www.j2megame.org/j2meapi/JSR_184_Mobile_3D_Graphics_API_1_1/file-format.html) | .m3g | 
poly | MoRay 3D Model | .mdl | [18 sample files](https://telparia.com/fileFormatSamples/poly/moRay/)
poly | [NetImmerse File](http://fileformats.archiveteam.org/wiki/NIF) | .nif | [5 sample files](https://telparia.com/fileFormatSamples/poly/netImmerse/)
poly | NorthCAD-3D | .n3d | 
poly | OGRE Mesh | .mesh | 
poly | [OpenNURBS 3D Model](http://fileformats.archiveteam.org/wiki/3DM) | .3dm | [1 sample file](https://telparia.com/fileFormatSamples/poly/openNURBS/)
poly | Polyfilm 3D Model | .3d | [8 sample files](https://telparia.com/fileFormatSamples/poly/polyfilm/)
poly | [POV-Ray Scene](http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description) | .pov | [1 sample file](https://telparia.com/fileFormatSamples/poly/povRay/) - POV Ray is not backwards compatible with old versions. So v1.0 files need to ran with 1.0. Old versions available from: http://www.povray.org/ftp/pub/povray/Old-Versions/ 		So I'd need to try most recent (system installed version) to oldest until one works 		I have compiled povray1 as dexvert/bin/povray/povray1 		Additionally povray files can include pointers to files in other directories so I'd have to go 'fetch' them and bring them into the same directory 		Next, includes are 'case sensitive' but originally on things like DOS, they were not, so I'd need to ensure the included files and include directives have the same case 		POVRAY1 also generates broken TGA output that only seem to convert with nconvert
poly | [Quake 2 Model](http://fileformats.archiveteam.org/wiki/MD2) | .md2 | [6 sample files](https://telparia.com/fileFormatSamples/poly/quake2Model/)
poly | Quake 3 Model | .md3 | 
poly | Rad Cad Drawing | .cad | 
poly | Raven Object File Format | .rof | 
poly | Ray Dream BRW | .brw | 
poly | Ray Dream Designer Scene | .rd4 .rds | 
poly | Real 3D | .real .obj | [4 sample files](https://telparia.com/fileFormatSamples/poly/real3D/) - Realsoft 3D may be able to view/render these. See linux version in: sandbox/app/realsoft3d-8.2.tar
poly | Renderit3D Data | .r3d | 
poly | ROT! Object | .rotobj | [5 sample files](https://telparia.com/fileFormatSamples/poly/rotObject/)
poly | Sculpt 3D Scene | .scene | [2 sample files](https://telparia.com/fileFormatSamples/poly/sculpt3DScene/) - A 3D rendering file format. I didn't bother investigating it.
poly | SGI Open Inventor Scene Graph | .iv | 
poly | [SGI Yet Another Object Description Language](http://fileformats.archiveteam.org/wiki/SGI_YAODL) | .ydl | [3 sample files](https://telparia.com/fileFormatSamples/poly/ydl/)
poly | Shockwave 3D Scene Export | .w3d | 
poly | Simply 3D Geometry | .ged | 
poly | Strata 3D Shape | .ssh | 
poly | Strata StudioPro Vis |  | 
poly | SuperScape Virtual Reality | .svr | 
poly | Valve Studio Model Vertices | .vvd | 
poly | Vertex Binary 3D Object | .3d | 
poly | [Virtual Reality Modeling Language](http://fileformats.archiveteam.org/wiki/VRML) | .wrl .wrz | [1 sample file](https://telparia.com/fileFormatSamples/poly/vrml/) - A 3D rendering file format meant for the web.
poly | Virtus VR Scene | .vvr | 



## Video (25)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
video | Accent Software DemoMaker Sequence | .seq | [2 sample files](https://telparia.com/fileFormatSamples/video/accentDemoMakerSequence/)
video | Accent Software Show Sequence | .seq | [11 sample files](https://telparia.com/fileFormatSamples/video/accentShowSequence/) - Old MS-DOS software. Couldn't find a standalone player/converter, and also probably wasn't very popular.
video | Adorage Animation | .awm | [1 sample file](https://telparia.com/fileFormatSamples/video/adorageAnimation/)
video | [Amiga Murder Film](https://wiki.multimedia.cx/index.php/Murder_FILM) | .film | [6 sample files](https://telparia.com/fileFormatSamples/video/amigaMurder/)
video | Animation Works Movie | .awm | [5 sample files](https://telparia.com/fileFormatSamples/video/animationWorks/) - Couldn't locate a converter or extractor
video | Astound Animation | .awa | 
video | [ClariSSA Super Smooth Animation](http://fileformats.archiveteam.org/wiki/IFF-SSA) | .ssa .anim | [7 sample files](https://telparia.com/fileFormatSamples/video/iffSSA/) - Couldn't find any working modern converter that works on any of the sample files.
video | [Delphine CIN Video](https://wiki.multimedia.cx/index.php/Delphine_CIN) | .cin | [5 sample files](https://telparia.com/fileFormatSamples/video/delphineCIN/) - FFMPEG has support for something called Delphine Software International CIN, but it couldn't convert the test files
video | [Deluxe Video](https://wiki.multimedia.cx/index.php/Electronic_Arts_MAD) |  | [1 sample file](https://telparia.com/fileFormatSamples/video/eaMADVideo/)
video | [Deluxe Video](http://fileformats.archiveteam.org/wiki/VDEO) |  | [1 sample file](https://telparia.com/fileFormatSamples/video/deluxeVideo/) - Couldn't find a converter for it. Could fire up an amiga with deluxe video program from Electronic Arts.
video | DK Multimedia Animation | .ani | [7 sample files](https://telparia.com/fileFormatSamples/video/dkAnimation/)
video | Fujitsu Movie | .mve | 
video | [Id Software RoQ Video](https://wiki.thedarkmod.com/index.php?title=Playing_ROQ_Video_Files) | .roq | [3 sample files](https://telparia.com/fileFormatSamples/video/idRoQ/)
video | [Knowledge Adventure MoVie](https://wiki.multimedia.cx/index.php?title=Space_Adventure_MOV) | .mov | 
video | Magic Lantern DIFF Animation | .diff | No known converter
video | NTitler Animation | .nt | [8 sample files](https://telparia.com/fileFormatSamples/video/ntitler/) - Couldn't locate a converter or extractor. Original Amiga program is here: http://aminet.net/package/gfx/misc/ntpro
video | [Optonica Videostream VAXL](http://fileformats.archiveteam.org/wiki/VAXL) | .vaxl | [15 sample files](https://telparia.com/fileFormatSamples/video/iffVAXL/) - Could only find this potential viewer, but no download link: https://www.ultimateamiga.com/index.php?topic=9605.0
video | [Psygnosis MultiMedia Video](https://wiki.multimedia.cx/index.php?title=PMM) | .pmm | Couldn't locate a converter
video | RATVID Video | .vdo | 
video | RIFF ANIM | .paf | [9 sample files](https://telparia.com/fileFormatSamples/video/riffANIM/) - Couldn't find any evidence of this out in the public. Could very well be a proprietary format
video | [RIFF Multimedia Movie](http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie) | .mmm | [14 sample files](https://telparia.com/fileFormatSamples/video/riffMultimediaMovie/) - Couldn't find a converter or player for it
video | [ScreenCam Video](https://wiki.multimedia.cx/index.php/SCM) | .scm | 
video | [Sony Vegas Video](https://en.wikipedia.org/wiki/Vegas_Pro) | .veg | [1 sample file](https://telparia.com/fileFormatSamples/video/sonyVegas/)
video | The Complete Animator Film | .tca | 
video | [Zoetrope Animation](https://elisoftware.org/w/index.php/Zoetrope_(Amiga,_3_1/2%22_Disk)_Antic_Software_-_1988_USA,_Canada_Release) | .rif | [4 sample files](https://telparia.com/fileFormatSamples/video/zoetropeAnimation/)

