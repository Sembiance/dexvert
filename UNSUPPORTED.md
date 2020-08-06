# Unsupported File Formats

The following 49 file formats are NOT currently supported by dexvert.



## 3d (5)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
3d | [IFF TDDD 3-D Render Document](http://fileformats.archiveteam.org/wiki/TDDD) | .tdd .cel .obj |  A 3D rendering file format. Some of these files may have been created by "Impulse 3D" I've never bothered trying to convert or render these into anything else
3d | [POV-Ray Scene](http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description) | .pov | 
3d | Sculpt 3D Scene | .scene | A 3D rendering file format. I didn't bother investigating it.
3d | [SGI Yet Another Object Description Language](http://fileformats.archiveteam.org/wiki/SGI_YAODL) | .ydl | 
3d | [Virtual Reality Modeling Language](http://fileformats.archiveteam.org/wiki/VRML) | .wrl .wrz | A 3D rendering file format meant for the web.



## Archive (5)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
archive | [Corel Thumbnails Archvie](http://fileformats.archiveteam.org/wiki/CorelDRAW) |  |  Contains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them. Even went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed. Sent an email to the libcdr creators, to see if they know of any info on the format, but never heard back.
archive | IFF LIST File |  |  The IFF LIST files contain 'shared' entries that are used for all chunks in the remainder of the file. In theory I could parse this file, and "extract" out by creating seperate files for each major FORM entry inside, making sure to also copy into these files the 'shared' entries, adjusting the resulting FORM lengths as needed. Couldn't find any real documentation on the LIST/SSETPROP format. See: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF
archive | [TED5 Archive](http://www.shikadi.net/moddingwiki/TED5) | .wl1 .ck4 .ck6 | An archive format created by TED5. Used for games like Commander Keen. The format is detailed on the wiki link above, so in theory I could create an extractor for it.
archive | [TTW Compressed File](http://fileformats.archiveteam.org/wiki/TTW) | .cr |  Amiga xfdmaster can supposedly decrunch this. 'vamos' won't run it right. Could emulate an amiga to support this. htpps://aminet.net/package/util/pack/xfdmaster
archive | [Viacom New Media Sprite Archive](http://www.shikadi.net/moddingwiki/Viacom_New_Media_Graphics_File_Format) | .vnm .000 |  An obscure format that packs multiple bitmaps and sprites into a single archive. Found the following two projects that extract them: https://github.com/jmcclell/vnmgf-exporter Sadly neither one can correctly process/extract the VNM files I encountered. The github link is much closer and is in modern Go.



## Audio (9)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
audio | [AdLib Instrument Bank](http://fileformats.archiveteam.org/wiki/AdLib_instrument_bank) | .bnk |  These .bnk files include sounds/instruments used by adlib ROL/SNG/SX files to make music. Technically the sounds could be extracted, maybe with 'Bank Manager' for DOS, but meh.
audio | Aegis Sonix Instrument | .instr |  The .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic
audio | [Covox ADPCM Encoded Audio](https://wiki.multimedia.cx/index.php/Covox_ADPCM) | .v8 .cvx |  I've tried using C:\APP\COVOXCONV.EXE but it could never get the WAV output at the correct sample rate, despire me trying different ones I also tried C:\SPUT111\SPUT.COM but it appears only output more COVOX formats. According to that wiki, mplayer might be able to play these, but I couldn't get it to play any of them.
audio | [Creative Music System File](http://fileformats.archiveteam.org/wiki/CMS_(Creative_Music_System)) | .cms |  Creative Music System. Couldn't locate any information on the file format itself, nor can I find any 'converters' for it. Only way to play them is within DOSBOX by setting this in the DOSBOX config: [sblaster] sbtype  = gb sbbase  = 220 irq     = 7 dma     = 1 hdma    = 5 sbmixer = true oplmode = cms oplemu  = default oplrate = 22050 Then going into CMSPLAY, running CMSDRV.COM and then PLAYER.EXE However that just plays the file, on an infinite loop, in real time. So while in theory I could maybe make a virtual WAV sound driver under linux and then have DOSBOX play to that driver and then record the music that way, I'd have to wait for the song to play in real time and there is no info on how long the song is
audio | [DataShow Sound File](http://www.amateur-invest.com/us_datashow.htm) | .snd | 
audio | [DigiTrekker](http://fileformats.archiveteam.org/wiki/DigiTrekker_module) | .dtm | Couldn't locate a player or converter. Tried milkytracker, but it wouldn't play it.
audio | [Inverse Frequency Sound Format](http://fileformats.archiveteam.org/wiki/Inverse_Frequency_Sound_format) |  | Used in various APOGEE games like commander keen. Didn't look that hard for a player/converter.
audio | [Quattro Pro Sound File](http://fileformats.archiveteam.org/wiki/Quattro_Pro) | .snd | Quattro Pro 3.0 allowed creation of slide shows which could include sounds. Couldn't locate any further information on these files except that they might be soundblaster compataible. Couldn't find anything to play them.
audio | Sonix Sound Sample | .ss |  The .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds. These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file. Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic



## Document (6)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
document | Clarion Database File | .dat | Did a Google search, couldn't find anything about it. unoconv didn't do anything with it either.
document | [Envision Publisher Document](http://fileformats.archiveteam.org/wiki/Envision_Publisher) | .evp .evt |  Envision Publisher for MSDOS doesn't have an "Export" option. I could figure out how to 'print to a file' or I could set up DOSBOX PDF Printer emulation: superuser.com/questions/270457/how-can-i-print-with-dosbox
document | [Help Librarian Help File](http://fileformats.archiveteam.org/wiki/Help_Librarian) | .hlp | Help Librarian files. No information about them could be found anywhere.
document | InfoFile Database File | .flr | Did a very quick Google search and didn't turn up any sort of converter program. This was a very obscure amiga database program.
document | [Internet Message Format](http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format) | .eml .msg |  With several RFC files describing the format, uou'd think this would be straight forward to parse, but it's a total nightmare. I had spent some time looking for a good program to parse it, and failed. I spent more time trying to code my own that would output JSON, but there are just a ton of edge cases and I gave up. In addition to the website link above, more details here: https://mailformat.dan.info/
document | [PC-File](http://fileformats.archiveteam.org/wiki/PC-FILE) | .dbf .rep | Was a pretty popular database program back in the day. Didn't really dig into what converters might be possible.



## Font (13)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
font | [Adobe Type 1 Font](http://fileformats.archiveteam.org/wiki/Adobe_Type_1) | .pfa .pfb | 
font | [Amiga Bitmap Font](http://fileformats.archiveteam.org/wiki/Amiga_bitmap_font) | .font | Fony (Win32/wine) (see sandbox/app/) is supposed to be able to open these, but I wasn't able to use it
font | [Blazing Paddles - Font](http://fileformats.archiveteam.org/wiki/Blazing_Paddles) | .chr | This can be converted with recoil2png. So if I ever decide to support fonts, I can use that as a starting point before converting the bitmaps into font files.
font | [Borland Graphics Font](http://fileformats.archiveteam.org/wiki/CHR_(Borland_font)) | .chr .bgi | 
font | C64 8x8 Font | .64c | 
font | [Envision Publisher Font](http://fileformats.archiveteam.org/wiki/Envision_Publisher) | .svf | Font file for the MSDOS program Envsion Publisher. Fontforge doesn't handle it and I didn't bother trying to convert further.
font | [FontForge File Format](http://fileformats.archiveteam.org/wiki/Spline_Font_Database) | .sfd | 
font | [GEM Bitmap Font](http://fileformats.archiveteam.org/wiki/GEM_bitmap_font) | .gft .fnt | Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it
font | LaserJet Soft Font | .sfl .sfp .sft | 
font | LinkWay Font | .fmf | 
font | [OpenType Font](http://fileformats.archiveteam.org/wiki/OpenType) | .otf | 
font | [The Draw Font](http://fileformats.archiveteam.org/wiki/TheDraw_font) | .tdf | Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it
font | [TrueType Font](http://fileformats.archiveteam.org/wiki/TTF) | .ttf | 



## Image (6)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
image | [CebraText](http://fileformats.archiveteam.org/wiki/CebraText) | .ttx | CebraText came out in 2003 for Windows. Sadly, it doesn't work with wine and I couldn't find any converter programs that supported the file format.
image | [Flash XML Graphics](http://fileformats.archiveteam.org/wiki/FXG) | .fxg | Couldn't find a reliable converter.
image | [GrafX2](http://grafx2.chez.com/) | .pkm | This is a modern program and file format which none of the converter programs currently support.
image | MLDF BMHD File | .mld | It's probably an image format. IFF format FORM with MLDFBMHD. Could not locate any info online about it and I didn't investigate further.
image | NeoPaint Pattern | .pat |  While identified via magic as a "NeoPaint Palette" they appear to be "patterns" used as stamps in the MSDOS Neopaint program. Short of reverse engineering it, in theory dexvert could convert these to images by opening up DOS Neopaint, selecting the pattern, stamping it or filling a canvas with it and saving the image. Don't plan on bothing to actually do that though, it's a relatively obscure program and file format.
image | [Teletext](http://snisurset.net/code/abydos/teletext.html) | .bin | Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on.



## Other (2)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
other | [Hewlett-Packard Graphics Language](http://fileformats.archiveteam.org/wiki/HPGL) | .hpgl |  Sometimes used for graphics, sometimes used to control plotters and other machines. I tried to compile this but it's ancient and failed: http://ftp.funet.fi/index/graphics/packages/hpgl2ps/hpgl2ps.tar.Z Quick searches didn't turn up any other 'easy' to grab and use converters, so punt on this for now.
other | [ISO CUE Sheet](http://fileformats.archiveteam.org/wiki/CUE_and_BIN) | .cue | CUE files are not handled directly. Instead target the .BIN file and the CUE is automatically found and taken into account.



## Video (3)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
video | [Deluxe Video](http://fileformats.archiveteam.org/wiki/VDEO) |  | Couldn't find a converter for it. Could fire up an amiga with deluxe video program from Electronic Arts.
video | RIFF ANIM | .paf | Couldn't find any evidence of this out in the public. Could very well be a proprietary format
video | [RIFF Multimedia Movie](http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie) | .mmm | Couldn't find a converter or player for it

