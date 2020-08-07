# Supported File Formats

The following 332 file formats are support by dexvert.



## Archive (43)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
archive | [Amiga Disk Format (FFS)](http://fileformats.archiveteam.org/wiki/ADF_(Amiga)) | .adf | 
archive | [Amiga Disk Format (OFS)](http://fileformats.archiveteam.org/wiki/ADF_(Amiga)) | .adf |  Not all ADF disk images are properly extracted by unar/unadf/adf-extractor. I've tried TONS of programs and they all fail on these disks, which are identified as the OFS variety. Yet fs-uae emulator loads the disks and runs them fine in an emulated amiga. So I could create an amiga workbench script that will convert all contents of an amiga disk into a ZIP file and put it on a shared folder/hard drive and get the contents that way. That's a lot more work, but doable.
archive | [Amiga Disk Master System Archive](http://fileformats.archiveteam.org/wiki/Disk_Masher_System) | .dms .fms | 
archive | [Amiga XPK Archive](http://fileformats.archiveteam.org/wiki/XPK) | .xpk | 
archive | [AMOS Basic Source Code Archive](http://fileformats.archiveteam.org/wiki/AMOS_BASIC_tokenized_file) | .amos | 
archive | [ARJ Archive](http://fileformats.archiveteam.org/wiki/ARJ) | .arj | 
archive | [Atari ATR Floppy Disk Image](http://fileformats.archiveteam.org/wiki/ATR) | .atr | 
archive | [Atari ST Floppy Disk Image](http://fileformats.archiveteam.org/wiki/ST_disk_image) | .st | 
archive | BOLT Game Data Archive | .blt | 
archive | [BZip2 archive](http://fileformats.archiveteam.org/wiki/BZ2) | .bz2 .bzip2 | 
archive | [Commodore Disk Image](http://fileformats.archiveteam.org/wiki/D64) | .d64 .d81 .d71 | 
archive | [Crunch-Mania Archive](http://fileformats.archiveteam.org/wiki/Crunchmania) |  | 
archive | [Disk Image](http://fileformats.archiveteam.org/wiki/Disk_Image_Formats) | .img | 
archive | [Genus Graphics Library Compressed Archive](http://fileformats.archiveteam.org/wiki/Genus_Graphics_Library) | .gx .gxl | 
archive | [GRASP Animation Archive](http://fileformats.archiveteam.org/wiki/GRASP_GL) | .gl |  This is an animation format, but the GRASPRT.EXE program won't play any of them and I can't find any modern players. However 'deark' will extract all the files, the artwork, code, etc. So for now I just treat this as an archive file.
archive | [GZip archive](http://fileformats.archiveteam.org/wiki/GZ) | .gz .gzip .z | 
archive | [HyperCard Stack](http://fileformats.archiveteam.org/wiki/HyperCard_stack) |  | 
archive | [ISO Disc Image](http://fileformats.archiveteam.org/wiki/ISO_image) | .iso | 
archive | [LBR Archive](http://fileformats.archiveteam.org/wiki/LBR) | .lbr | 
archive | [Lempel-Ziv Archive](http://fileformats.archiveteam.org/wiki/LZX) | .lzx | 
archive | [LHArc Archive](http://fileformats.archiveteam.org/wiki/LHA) | .lha .lhz | 
archive | [Mac Compact Pro Archive](http://fileformats.archiveteam.org/wiki/Compact_Pro) | .cpt | 
archive | [MacOS Resource Fork](http://fileformats.archiveteam.org/wiki/Macintosh_resource_file) | .rsrc | 
archive | [Macromedia Director](http://fileformats.archiveteam.org/wiki/Shockwave_(Director)) | .dxr .dir | 
archive | [Mailbox](http://fileformats.archiveteam.org/wiki/ARJ) | .mbox | 
archive | [Microsoft Compound Document](http://fileformats.archiveteam.org/wiki/Microsoft_Compound_File) |  | 
archive | [MS Compress Archive](http://fileformats.archiveteam.org/wiki/MS-DOS_installation_compression) | _ | 
archive | [Nero CD Image](http://fileformats.archiveteam.org/wiki/NRG) | .nrg | 
archive | [Pack-Ice Archive](http://fileformats.archiveteam.org/wiki/Pack-Ice) |  | 
archive | [PAK/ARC Compressed Archive](http://fileformats.archiveteam.org/wiki/ARC_(compression_format)) | .arc .pak | 
archive | [PCXlib Compressed Archive](http://fileformats.archiveteam.org/wiki/PCX_Library) | .pcl | 
archive | [PKZip Archive](http://fileformats.archiveteam.org/wiki/ZIP) | .zip | 
archive | [PowerPacker Archive](http://fileformats.archiveteam.org/wiki/PowerPacker) | .pp | 
archive | [Print Shop Graphic POG Archive](http://fileformats.archiveteam.org/wiki/The_Print_Shop) | .pog | 
archive | [Pro-Pack - Rob Northern Compression](http://fileformats.archiveteam.org/wiki/RNC) | .rnc | 
archive | [Roshal Archive](http://fileformats.archiveteam.org/wiki/RAR) | .rar | 
archive | [Self Extracting Stuffit Archive](http://fileformats.archiveteam.org/wiki/SIT) | .sea | 
archive | [StoneCracker Archive](http://fileformats.archiveteam.org/wiki/StoneCracker) | .stc | 
archive | [Stuffit Archive](http://fileformats.archiveteam.org/wiki/SIT) | .sit | 
archive | [Tape Archive](http://fileformats.archiveteam.org/wiki/Tar) | .tar .gtar | 
archive | [The Sterling COMPressor archive](http://fileformats.archiveteam.org/wiki/TSComp) |  | 
archive | [TTComp Archive](http://fileformats.archiveteam.org/wiki/TTComp_archive) |  | 
archive | [WAD2](http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm) | .wad | 



## Audio (9)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
audio | [Amiga 8-bit Sampled Voice](http://fileformats.archiveteam.org/wiki/8SVX) | .8svx .iff | Some 8SVX files don't have a sample rate in the file. In these cases I try multiple different common sample rates.
audio | [AMOS Samples Bank](http://fileformats.archiveteam.org/wiki/AMOS_Memory_Bank#AMOS_Samples_Bank) | .abk | 
audio | [Audio Interchange File Format](http://fileformats.archiveteam.org/wiki/AIFF) | .aif .aiff .aff | 
audio | [Beam Software SIFF Sound](http://fileformats.archiveteam.org/wiki/SIFF) | .son |  The .son test files are technically supported by libavformat and ffmpeg/cvlc, yet it often produces very distored WAVs. My hunch is the decompression algo doesn't quite work with my particular test SIFF files. I couldn't locate ANY OTHER converters.
audio | [Creative Voice](http://fileformats.archiveteam.org/wiki/Creative_Voice_File) | .voc | 
audio | [Free Lossless Audio Codece](http://fileformats.archiveteam.org/wiki/FLAC) | .flac | 
audio | [MPG Layer 3 Audio File](http://fileformats.archiveteam.org/wiki/MP3) | .mp3 | 
audio | [Ogg Vorbis Audio](http://fileformats.archiveteam.org/wiki/Ogg) | .ogg .oga | 
audio | [Waveform Audio File Format](http://fileformats.archiveteam.org/wiki/WAV) | .wav | 



## Document (16)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
document | AmigaBASIC Source Code | .bas | 
document | [Amigaguide Document](http://fileformats.archiveteam.org/wiki/AmigaGuide) | .guide | 
document | [Comma Seperated Value File](http://fileformats.archiveteam.org/wiki/CSV) | .csv | 
document | [dBase/FoxBase/XBase Database File](http://fileformats.archiveteam.org/wiki/DBF) | .dbf | 
document | [DjVu Document](http://fileformats.archiveteam.org/wiki/DjVu) | .djvu .djv | 
document | [HP Printer Command Language](http://fileformats.archiveteam.org/wiki/PCL) | .pcl .prn | 
document | [JavaScript Object Notation](http://fileformats.archiveteam.org/wiki/JSON) | .json | 
document | [Lotus 1-2-3 File](http://fileformats.archiveteam.org/wiki/Lotus_1-2-3) | .wks .wk1 .wk2 .wk3 .wk4 .123 .wkb | 
document | [MaciCardfile Document](http://fileformats.archiveteam.org/wiki/Cardfile) | .crd | 
document | [Macintosh Word Document](http://fileformats.archiveteam.org/wiki/Microsoft_Word_for_Macintosh) |  | 
document | [PC-Outline Document](http://fileformats.archiveteam.org/wiki/PC-Outline) | .pco | 
document | [Portable Document Format](http://fileformats.archiveteam.org/wiki/PDF) | .pdf | 
document | [Rich Text Format](http://fileformats.archiveteam.org/wiki/RTF) | .rtf | 
document | [Windows Help File](http://fileformats.archiveteam.org/wiki/HLP) | .hlp | 
document | [Windows Write Document](http://fileformats.archiveteam.org/wiki/WRI) | .wri | 
document | [WordPerfect document](http://fileformats.archiveteam.org/wiki/WordPerfect) | .wp .wpd .wp4 .wp5 .wp6 .wp7 | 



## Image (211)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
image | 3D Construction Kit | .run | 
image | [Adobe Photoshop](http://fileformats.archiveteam.org/wiki/PSD) | .psd | 
image | [AFLI-Editor Image](http://fileformats.archiveteam.org/wiki/AFLI-Editor) | .afl | 
image | [Alias PIX Image](http://fileformats.archiveteam.org/wiki/Alias_PIX) | .pix .alias .img .als | 
image | [Alias Wavefront RLA](http://fileformats.archiveteam.org/wiki/RLA) | .rla | 
image | [Amica Paint](http://fileformats.archiveteam.org/wiki/Amica_Paint) | .ami | 
image | [Amiga Workbench Icon](http://fileformats.archiveteam.org/wiki/Amiga_Workbench_icon) | .info | 
image | [AMOS Icons Bank](http://fileformats.archiveteam.org/wiki/AMOS_Icon_Bank) | .abk | 
image | [AMOS Picture Bank](http://fileformats.archiveteam.org/wiki/AMOS_Picture_Bank) | .abk | 
image | [AMOS Sprites Bank](http://fileformats.archiveteam.org/wiki/AMOS_Sprite_Bank) | .abk |  Sometimes the spite frames output are all the same size and make a nice animated image (abydosconvert does this with webp output) However often this format contains multiple frames of different sizes and the 'positioning' and timing information for animation is not processed So we also run deark which just outputs all the sprite frames individually
image | Amstrad CPC Mode 5 Image | .cm5 .gfx | 
image | [Ani ST](http://fileformats.archiveteam.org/wiki/AniST) | .scr .str | 
image | [Anime 4ever!!! Image](http://fileformats.archiveteam.org/wiki/Anime_4ever_slideshow) | .a4r | 
image | [ANSI Art File](http://fileformats.archiveteam.org/wiki/ANSI_Art) | .ans | 
image | [Art Studio](http://fileformats.archiveteam.org/wiki/Art_Studio) | .art .aas | 
image | [ArtWorx Data Format](http://fileformats.archiveteam.org/wiki/ArtWorx_Data_Format) | .adf | 
image | [Asperite](https://www.aseprite.org/) | .ase .aseprite | 
image | [Atari AP* Image](http://fileformats.archiveteam.org/wiki/AP*) | .256 .ap2 .apa .apc .plm .mic | 
image | [Atari APAC3 APP Image](http://fileformats.archiveteam.org/wiki/Apac3_APP) | .app .aps | 
image | [Atari CAD](http://fileformats.archiveteam.org/wiki/AtariCAD) | .drg | 
image | Atari Graph Image | .all | 
image | [Atari Graphics Studio](http://g2f.atari8.info/) | .ags | 
image | [AV1 Image File Format](http://fileformats.archiveteam.org/wiki/AVIF) | .avif .avifs | 
image | [Avatar/0](http://fileformats.archiveteam.org/wiki/AVATAR) | .avt | 
image | BBC Micro Image | .bb0 .bb1 .bb2 .bb4 .bb5 | 
image | [BBC Micro LdPic Image](http://fileformats.archiveteam.org/wiki/LdPic) | .bbg | 
image | [Better Portable Graphics](http://fileformats.archiveteam.org/wiki/BPG) | .bpg | Some BPG files are animated, but dexvert doesn't support these yet. All BPG files are just converted into single PNG Files.
image | [Big Flexible Line Interpretation](http://fileformats.archiveteam.org/wiki/BFLI) | .bfli | 
image | [Binary Text](http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)) | .bin | 
image | [Bitmap Image](http://fileformats.archiveteam.org/wiki/BMP) | .bmp .rle .dib | 
image | [Blazing Paddles](http://fileformats.archiveteam.org/wiki/Blazing_Paddles) | .pi | 
image | [Blazing Paddles - Window](http://fileformats.archiveteam.org/wiki/Blazing_Paddles) | .wnd | 
image | [Bugbiter APAC239i](http://fileformats.archiveteam.org/wiki/Bugbiter_APAC239i) | .bgp | 
image | [Canon RAW 2](http://fileformats.archiveteam.org/wiki/Canon_RAW_2) | .cr2 | 
image | [CDU-Paint Image](http://fileformats.archiveteam.org/wiki/CDU-Paint) | .cdu | 
image | [Champions' Interlace Image](http://fileformats.archiveteam.org/wiki/Champions%27_Interlace) | .cci .cin | 
image | [Cheese](http://fileformats.archiveteam.org/wiki/Cheese) | .che | 
image | [ColoRIX](http://fileformats.archiveteam.org/wiki/ColoRIX) | .rix .sca .scb .scc .sce .scf .scg .sci .sck .scl .scn .sco .scp .scq .scr .sct .scu .scv .scw .scx .scy .scz | 
image | [ColorViewSquash](http://fileformats.archiveteam.org/wiki/ColorViewSquash) | .rgb | 
image | [Computer Aided Acquisition and Logistics Support](http://fileformats.archiveteam.org/wiki/CALS_raster) | .ct1 .cal .ras .ct2 .ct3 .nif .ct4 .c4 | 
image | [Computer Graphics Metafile](http://fileformats.archiveteam.org/wiki/CGM) | .cgm | allprims.cgm test file fails to convert
image | [ComputerEyes](http://fileformats.archiveteam.org/wiki/ComputerEyes) | .ce1 .ce2 .ce3 | 
image | [Corel Metafile Exchange Image](http://fileformats.archiveteam.org/wiki/CMX) | .cmx | 
image | [CorelDraw Document](http://fileformats.archiveteam.org/wiki/CorelDRAW) | .cdr .cdt .cdx .cpx | 
image | [Crack Art](http://fileformats.archiveteam.org/wiki/Crack_Art) | .ca1 .ca2 .ca3 | 
image | [Cyber Paint Cell](http://fileformats.archiveteam.org/wiki/Cyber_Paint_Cell) | .cel | 
image | [Dali](http://fileformats.archiveteam.org/wiki/Dali) | .sd0 .sd1 .sd2 | 
image | [Degas Elite Brush](http://fileformats.archiveteam.org/wiki/DEGAS_Elite_brush) | .bru | 
image | [Degas High Resolution Picture](http://fileformats.archiveteam.org/wiki/DEGAS_image) | .pc3 | 
image | [Degas High Resolution Picture (PI)](http://fileformats.archiveteam.org/wiki/DEGAS_image) | .pi3 | 
image | [Degas Low Resolution Picture](http://fileformats.archiveteam.org/wiki/DEGAS_image) | .pc1 | 
image | [Degas Low Resolution Picture (PI)](http://fileformats.archiveteam.org/wiki/DEGAS_image) | .pi1 | 
image | [Degas Medium Resolution Picture](http://fileformats.archiveteam.org/wiki/DEGAS_image) | .pc2 | 
image | [Degas Medium Resolution Picture (PI)](http://fileformats.archiveteam.org/wiki/DEGAS_image) | .pi2 | 
image | [DICOM Bitmap](http://fileformats.archiveteam.org/wiki/DICOM) | .dcm .dic | 
image | [Digi Paint](http://fileformats.archiveteam.org/wiki/Digi_Paint) | .ap3 .apv .dgi .dgp .ilc .esc .pzm .g09 .bg9 | 
image | [Digital Negative](http://fileformats.archiveteam.org/wiki/DNG) | .dng | 
image | [Digital Picture Exchange](http://fileformats.archiveteam.org/wiki/DPX) | .dpx | 
image | [DirectDraw Surface](http://fileformats.archiveteam.org/wiki/DDS) | .dds | 
image | [Doodle Atari](http://fileformats.archiveteam.org/wiki/Doodle_(Atari)) | .doo | 
image | [Doodle C64](http://fileformats.archiveteam.org/wiki/Doodle!_(C64)) | .dd .jj | 
image | [Dr. Halo](http://fileformats.archiveteam.org/wiki/Dr._Halo) | .cut .pal .pic | 
image | [Draw 256 Image](http://fileformats.archiveteam.org/wiki/Draw256) | .vga | 
image | [Drawing Exchange Format](http://fileformats.archiveteam.org/wiki/DXF) | .dxf | 
image | [Draz Paint](http://fileformats.archiveteam.org/wiki/Drazpaint) | .drz .drp | 
image | [Dune AAI Image](http://fileformats.archiveteam.org/wiki/AAI) | .aai | 
image | [Encapsulated PostScript](http://fileformats.archiveteam.org/wiki/EPS) | .eps .epsf .epsi .epi .ept | 
image | [Enhanced Simplex](http://fileformats.archiveteam.org/wiki/Enhanced_Simplex) | .esm | 
image | [Epson RAW File](http://fileformats.archiveteam.org/wiki/ERF) | .erf | 
image | [Extended Binary](http://fileformats.archiveteam.org/wiki/XBIN) | .xb | 
image | [Face Painter](http://fileformats.archiveteam.org/wiki/Face_Painter) | .fcp .fpt | 
image | [Farbfeld](http://fileformats.archiveteam.org/wiki/Farbfeld) | .ff | 
image | [Flexible Image Transport System](http://fileformats.archiveteam.org/wiki/Flexible_Image_Transport_System) | .fit .fits .fts .fz | 
image | [FLI Graph Image](http://fileformats.archiveteam.org/wiki/FLI_GraphF) | .bml .fli | 
image | [Flickering Flexible Line Interpretation](http://fileformats.archiveteam.org/wiki/FFLI) | .ffli | 
image | [Free Lossless Image Format](http://fileformats.archiveteam.org/wiki/FLIF) | .flif | 
image | [Fujifilm RAW](http://fileformats.archiveteam.org/wiki/RAF) | .raf | 
image | [GEM Raster Bitmap](http://fileformats.archiveteam.org/wiki/GEM_Raster) | .img .ximg | 
image | [GFA Artist](http://fileformats.archiveteam.org/wiki/GFA_Artist) | .art | 
image | [GoDot 4Bit Image](http://fileformats.archiveteam.org/wiki/GoDot) | .4bt | 
image | [Graphics Interchange Format](http://fileformats.archiveteam.org/wiki/GIF) | .gif | 
image | [Graphics Processor](http://fileformats.archiveteam.org/wiki/Graphics_Processor) | .pg1 .pg2 .pg3 | 
image | [GX1 Bitmap](http://fileformats.archiveteam.org/wiki/GX1) | .gx1 | 
image | [GX2 Bitmap](http://fileformats.archiveteam.org/wiki/GX2) | .gx2 | 
image | [Haiku Vector Icon Format](http://fileformats.archiveteam.org/wiki/Haiku_Vector_Icon_Format) | .hvif |  Several HVIF files don't appear to convert correctly with abydosconvert. I located an hvif2svg haskell program but it's even worse. So for now these particular HVIF files just won't be supported.
image | [Hi-Eddi](http://fileformats.archiveteam.org/wiki/Hi-Eddit) | .hed | 
image | [Hi-Pic Creator](http://fileformats.archiveteam.org/wiki/Hi-Pic_Creator) | .hpc | 
image | [Hierarchical Data Format v4](http://fileformats.archiveteam.org/wiki/HDF) | .hdf | 
image | [Hierarchical Data Format v5](http://fileformats.archiveteam.org/wiki/HDF) | .h5 | Only support converting to grayscale.
image | [High Efficiency Image File](http://fileformats.archiveteam.org/wiki/HEIF) | .heic .heif | 
image | [HRU](http://fileformats.archiveteam.org/wiki/HRU) | .hru | 
image | [iCEDraw Format](http://fileformats.archiveteam.org/wiki/ICEDraw) | .idf | 
image | [IFF Amiga Contiguous Bitmap](http://fileformats.archiveteam.org/wiki/ILBM#ACBM) | .lbm .ilbm .iff .acbm | 
image | [IFF Interleaved Bitmap Image](http://fileformats.archiveteam.org/wiki/ILBM) | .lbm .ilbm .iff .beam .dhr .dr .mp |  Some ILBM files were only used to hold a palette and nothing more. This won't convert those. Others have EMPTY (zeros) CMAP palettes which confuse the converter programs. So I detect this and remove the CMAP entry which allows the converters to fallback to a default converter. DPPS chunk - Present in some files and they don't convert correctly. Probably a 'Deluxe Paint' chunk of some sort. CRNG chunk - Used for color shifting. Abydos supports some of these (used by Deluxe Paint)
image | [IFF RGBN Image](http://fileformats.archiveteam.org/wiki/ILBM) | .iff .rgbn | 
image | [Image System](http://fileformats.archiveteam.org/wiki/Image_System) | .ish .ism | 
image | [ImageLab Image](http://fileformats.archiveteam.org/wiki/ImageLab/PrintTechnic) | .b_w .b&w | 
image | [Inset PIX](http://fileformats.archiveteam.org/wiki/Inset_PIX) | .pix | 
image | [Interpaint](http://fileformats.archiveteam.org/wiki/Interpaint) | .iph .ipt | 
image | [Joint Bi-Level Image experts Group](http://fileformats.archiveteam.org/wiki/JBIG) | .jbg .jbig .bie | 
image | [Joint Photographic Experts Group Image](http://fileformats.archiveteam.org/wiki/JPG) | .jpg .jpeg .jpe .jfif | 
image | [JPEG 2000](http://fileformats.archiveteam.org/wiki/JPEG_2000) | .jp2 | 
image | [JPEG Network Graphics](http://fileformats.archiveteam.org/wiki/JNG) | .jng | 
image | [JPEG XR](http://fileformats.archiveteam.org/wiki/JPEG_XR) | .jxr .hdp .wdp .wmp | 
image | [Khoros Visualization Image](http://fileformats.archiveteam.org/wiki/VIFF) | .viff .xv | 
image | [Kisekae Set System Cell](http://fileformats.archiveteam.org/wiki/KiSS_CEL) | .cel .kcf | 
image | Koala Paint | .gig .koa .kla | 
image | [Kodak Cineon](http://fileformats.archiveteam.org/wiki/Cineon) | .cin | 
image | [Kodak FlashPix](http://fileformats.archiveteam.org/wiki/FPX) | .fpx | 
image | [Kodak Photo CD](http://fileformats.archiveteam.org/wiki/Photo_CD) | .pcd | 
image | [Kolor Raw](http://fileformats.archiveteam.org/wiki/Kolor_Raw) | .kro | 
image | [Krita](http://fileformats.archiveteam.org/wiki/Krita) | .kra | 
image | [LEADTools Compressed Image](http://fileformats.archiveteam.org/wiki/CMP) | .cmp | 
image | [libgd GD Image](https://libgd.github.io/manuals/2.3.0/files/gd_gd-c.html) | .gd | 
image | [libgd GD2 Image](https://libgd.github.io/manuals/2.3.0/files/gd_gd2-c.html) | .gd2 | 
image | [Macintosh Picture Format](http://fileformats.archiveteam.org/wiki/PICT) | .pict .pic .pct | 
image | [MacOS Icon](http://fileformats.archiveteam.org/wiki/ICNS) | .icns | 
image | [MacPaint Image](http://fileformats.archiveteam.org/wiki/MacPaint) | .mac .pntg .pic | 
image | [Magick Image File Format](http://fileformats.archiveteam.org/wiki/MIFF) | .miff .mif | 
image | [MegaPaint BLD](http://fileformats.archiveteam.org/wiki/MegaPaint_BLD) | .bld | 
image | [Micro Illustrator](http://fileformats.archiveteam.org/wiki/Micro_Illustrator) | .mil | 
image | [Microsoft Paint](http://fileformats.archiveteam.org/wiki/MSP_(Microsoft_Paint)) | .msp | 
image | [Microsoft Windows Animated Cursor](http://fileformats.archiveteam.org/wiki/ANI) | .ani | 
image | [Microsoft Windows Cursor](http://fileformats.archiveteam.org/wiki/CUR) | .cur | 
image | [Microsoft Windows Enhanced Metafile](http://fileformats.archiveteam.org/wiki/EMF) | .emf | 
image | [Microsoft Windows Icon File](http://fileformats.archiveteam.org/wiki/ICO) | .ico | 
image | [Microsoft Windows Metafile](http://fileformats.archiveteam.org/wiki/WMF) | .wmf .apm .wmz | 
image | [Milti Palette Picture](http://fileformats.archiveteam.org/wiki/Multi_Palette_Picture) | .mpp | 
image | [Movie Maker](http://fileformats.archiveteam.org/wiki/Movie_Maker) | .bkg .shp | 
image | [MTV Ray-Tracer](http://fileformats.archiveteam.org/wiki/MTV_ray_tracer_bitmap) | .mtv .pic | 
image | [Multi-Page PCX](http://fileformats.archiveteam.org/wiki/DCX) | .dcx | 
image | [Multiple-image Network Graphics](http://fileformats.archiveteam.org/wiki/MNG) | .mng | 
image | [NAPLPS Image](http://fileformats.archiveteam.org/wiki/NAPLPS) | .nap |  Some NAP files are actually animations. TURSHOW does actually show these, but sadly I can't detect this. So for now I treat all NAP files as just single images.  There also exists .SCR files which are naplps Script files. The EAGMD.SCR file was created from using the P2NV02 program (can't locate anywhere, just a reference to it here: https://groups.google.com/g/alt.bbs/c/jFgKRCoBedA/m/zSW-AkORqIoJ?pli=1). My hunch is if I can find the P2NV02.ZIP archive, it probably has more info, maybe even a way to convert the SCR script back into an image. Note I learned a little bit about this format from README.EXE in eag2nap.zip
image | [Neochrome](http://fileformats.archiveteam.org/wiki/NEOchrome) | .neo | 
image | [Nikon Electronic Format](http://fileformats.archiveteam.org/wiki/Nikon) | .nef .nrw | 
image | [Nokia Over the Air Bitmap](http://fileformats.archiveteam.org/wiki/OTA_bitmap) | .otb | 
image | [Olympus RAW](http://fileformats.archiveteam.org/wiki/ORF) | .orf | 
image | [OpenDocument Drawing](http://fileformats.archiveteam.org/wiki/OpenDocument_Drawing) | .odg .otg .fodg | 
image | [OpenEXR](http://fileformats.archiveteam.org/wiki/OpenEXR) | .exr | 
image | [OpenRaster](http://fileformats.archiveteam.org/wiki/OpenRaster) | .ora | 
image | [OS/2 Icon File](http://fileformats.archiveteam.org/wiki/OS/2_Icon) | .ico | 
image | [PabloPaint](http://fileformats.archiveteam.org/wiki/PabloPaint) | .pa3 .ppp | 
image | [Paintworks](http://fileformats.archiveteam.org/wiki/Paintworks) | .cl0 .sc0 .cl1 .sc1 .cl2 .sc2 | 
image | [Palm Database ImageViewer format](http://fileformats.archiveteam.org/wiki/Palm_Database_ImageViewer) | .pdb | 
image | [Panasonic RAW](http://fileformats.archiveteam.org/wiki/Panasonic_RAW) | .rw2 .raw .rwl | 
image | [PC Paint Image](http://fileformats.archiveteam.org/wiki/PCPaint_PIC) | .pic .clp | 
image | [PC Paintbrush Image](http://fileformats.archiveteam.org/wiki/PCX) | .pcx | 
image | [PC-Board](http://fileformats.archiveteam.org/wiki/PCBoard) | .pcb | 
image | [Pentax RAW](http://fileformats.archiveteam.org/wiki/Pentax_PEF) | .pef .ptx | 
image | [PES Embroidery File](http://fileformats.archiveteam.org/wiki/PES) | .pes |  It's a vector format, but uniconvertor just embeds a PNG into the resulting SVG file. Imagemagick's convert can produce .svg versions, but it doesn't output all the original lines and no color. So we convert to both SVG and PNG with convert.
image | [PETSCII Screen Code Sequence](http://fileformats.archiveteam.org/wiki/PETSCII) | .seq | 
image | [PFS First Publisher](http://fileformats.archiveteam.org/wiki/ART_(PFS:_First_Publisher)) | .art | 
image | [PhotoChrome](http://fileformats.archiveteam.org/wiki/PhotoChrome) | .pcs | 
image | [Picasso 64](http://fileformats.archiveteam.org/wiki/Picasso_64) | .p64 | 
image | [Planetary Data System](http://fileformats.archiveteam.org/wiki/PDS) | .imq .img .pds | 
image | [Portable Arbitrary Map](http://fileformats.archiveteam.org/wiki/PAM) | .pam | 
image | [Portable Bitmap](http://fileformats.archiveteam.org/wiki/PBM) | .pbm | 
image | [Portable Float Map](http://fileformats.archiveteam.org/wiki/PFM) | .pfm | 
image | [Portable Greyscale](http://fileformats.archiveteam.org/wiki/PGM) | .pgm | 
image | [Portable Network Graphic](http://fileformats.archiveteam.org/wiki/PNG) | .png | 
image | [Portable Pixmap](http://fileformats.archiveteam.org/wiki/Netpbm_formats) | .ppm | 
image | [PostScript](http://fileformats.archiveteam.org/wiki/Postscript) | .ps | 
image | [Prism Paint](http://fileformats.archiveteam.org/wiki/Prism_Paint) | .pnt .tpi | 
image | [QRT Ray Tracer Bitmap](http://fileformats.archiveteam.org/wiki/QRT_Ray_Tracer_bitmap) | .qrt .dis .raw | 
image | [Quantum Paint](http://fileformats.archiveteam.org/wiki/QuantumPaint) | .pbx | 
image | [QuickBasic BSAVE Image](http://fileformats.archiveteam.org/wiki/BSAVE_Image) | .pic .scn .bsv .cgx | 
image | [QuickTime Image Format](http://fileformats.archiveteam.org/wiki/QTIF) | .qtif .qif | Not all QTIF sub formats are not supported.
image | [Radiance HDR](http://fileformats.archiveteam.org/wiki/Radiance_HDR) | .hdr .rgbe .xyze .pic .rad | 
image | [Rainbow Painter](http://fileformats.archiveteam.org/wiki/Rainbow_Painter) | .rp | 
image | [RUN Paint](http://fileformats.archiveteam.org/wiki/RUN_Paint) | .rpm | 
image | [Saracen Paint](http://fileformats.archiveteam.org/wiki/Saracen_Paint) | .sar | 
image | [Scalable Vectory Graphics](http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics) | .svg .svgz | 
image | [Segmented Hypergraphics Bitmap](http://fileformats.archiveteam.org/wiki/Segmented_Hypergraphics) | .shg | 
image | [Silicon Graphics Image](http://fileformats.archiveteam.org/wiki/SGI_(image_file_format)) | .sgi .bw .rgba .rgb | 
image | [Sinbad Slideshow](http://fileformats.archiveteam.org/wiki/Sinbad_Slideshow) | .ssb | 
image | [SlideShow for VBXE](http://fileformats.archiveteam.org/wiki/SlideShow_for_VBXE) | .dap | 
image | [Spectrum 512 Compressed](http://fileformats.archiveteam.org/wiki/Spectrum_512_formats) | .spc | 
image | [Spectrum 512 Uncompressed](http://fileformats.archiveteam.org/wiki/Spectrum_512_formats) | .spu | 
image | [STAD PAC](http://fileformats.archiveteam.org/wiki/STAD_PAC) | .pac .seq | 
image | [Stardent AVS X](http://fileformats.archiveteam.org/wiki/AVS_X_image) | .avs .mbfavs .x | 
image | [STOS Memory Bank](http://fileformats.archiveteam.org/wiki/STOS_memory_bank) | .mbk .mbs | 
image | [STOS Picture Packer](http://fileformats.archiveteam.org/wiki/Picture_Packer) | .pp3 | 
image | [STOS Picture Packer](http://fileformats.archiveteam.org/wiki/Picture_Packer) | .pp1 | 
image | [STOS Picture Packer](http://fileformats.archiveteam.org/wiki/Picture_Packer) | .pp2 | 
image | [Sun Icon](http://fileformats.archiveteam.org/wiki/Sun_icon) | .ico .icon | Color currently isn't supported. Don't know of a converter that supports it due to palettes not being embedded within the file.
image | [Sun Raster Bitmap](http://fileformats.archiveteam.org/wiki/Sun_Raster) | .ras .rast .rs .scr .sr .sun .im1 .im8 .im24 .im32 | 
image | [Synthetic Arts](http://fileformats.archiveteam.org/wiki/Synthetic_Arts) | .srt | 
image | [Tagged Image File Format](http://fileformats.archiveteam.org/wiki/TIFF) | .tif .tiff | 
image | [Tencent TAP](http://fileformats.archiveteam.org/wiki/TAP_(Tencent)) | .tap | 
image | [Texas Instruments Calculator Image](http://fileformats.archiveteam.org/wiki/TI_picture_file) | .82i .8ca .8ci .92i .73i .83i .8xi .85i .86i .89i .9xi .v2i | 
image | [The GIMP Image Format](http://fileformats.archiveteam.org/wiki/XCF) | .xcf | 
image | [TheDraw File](http://fileformats.archiveteam.org/wiki/TheDraw_Save_File) | .td | 
image | [Tobias Richter Fullscreen Slideshow](http://fileformats.archiveteam.org/wiki/Tobias_Richter_Fullscreen_Slideshow) | .pci | 
image | TRS-80 CLP File | .clp | 
image | [Truevision Targa Graphic](http://fileformats.archiveteam.org/wiki/TGA) | .tga .targa .tpic .icb .vda .vst | 
image | [TUNDRA Text-Mode Graphic](http://fileformats.archiveteam.org/wiki/TUNDRA) | .tnd | 
image | [Valve Texture Format](http://fileformats.archiveteam.org/wiki/Valve_Texture_Format) | .vtf | 
image | [VDC BitMap](http://fileformats.archiveteam.org/wiki/VBM_(VDC_BitMap)) | .vbm .bm | 
image | [Vidcom 64](http://fileformats.archiveteam.org/wiki/Vidcom_64) | .vid | 
image | [Video Image Communication and Retrieval](http://fileformats.archiveteam.org/wiki/VICAR) | .vicar .vic .img | 
image | [WebP Image](http://fileformats.archiveteam.org/wiki/Webp) | .webp | 
image | [Wigmore Artist 64](http://fileformats.archiveteam.org/wiki/Wigmore_Artist_64) | .a64 .wig | 
image | [Wireless Bitmap](http://fileformats.archiveteam.org/wiki/WBMP) | .wbmp .wap wbm | 
image | [WordPerfect Graphic](http://fileformats.archiveteam.org/wiki/WordPerfect_Graphics) | .wpg | 
image | [X Window Dump](http://fileformats.archiveteam.org/wiki/XWD) | .xwd .dmp | 
image | [X11 Bitmap](http://fileformats.archiveteam.org/wiki/XBM) | .xbm .bm | 
image | [X11 Pixmap](http://fileformats.archiveteam.org/wiki/XPM) | .xpm .pm | 
image | [XGA](http://fileformats.archiveteam.org/wiki/XGA_(Falcon)) | .xga | 
image | ZX Spectrum Attributes Image | .atr | 
image | ZX Spectrum Border Screen | .bmc4 .bsc | 
image | ZX Spectrum CHR$ | .ch$ | 



## Music (21)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
music | [Abyss Highest Experience Module](http://fileformats.archiveteam.org/wiki/AHX_(Abyss)) | .ahx | 
music | [AdLib/Roland Song](http://fileformats.archiveteam.org/wiki/AdLib_Visual_Composer_/_Roland_Synthesizer_song) | .rol | 
music | [AMOS Music Bank](http://fileformats.archiveteam.org/wiki/AMOS_Music_Bank) | .abk | 
music | [AMOS Tracker Bank](https://www.exotica.org.uk/wiki/AMOS_file_formats#Regular_memory_bank_format) | .abk | 
music | [Commodore SID Music File](http://fileformats.archiveteam.org/wiki/SID) | .sid .psid | 
music | [Creative Music Format](http://fileformats.archiveteam.org/wiki/Creative_Music_Format) | .cmf | 
music | [Extended MIDI](http://fileformats.archiveteam.org/wiki/XMI_(Extended_MIDI)) | .xmi | 
music | [Extended Module](http://fileformats.archiveteam.org/wiki/XM) | .xm | 
music | [Human Machine Interfaces MIDI Format](http://fileformats.archiveteam.org/wiki/HMI) | .hmi .hmp | 
music | [MIDI Music File](http://fileformats.archiveteam.org/wiki/MIDI) | .mid | 
music | [OctaMED Module](http://fileformats.archiveteam.org/wiki/MED) | .med .mmd1 .mmd2 .mmd3 .mmd4 | 
music | [Oktalyzer Module](http://fileformats.archiveteam.org/wiki/Oktalyzer_module) | .okt .okta | 
music | [Prorunner Module](http://fileformats.archiveteam.org/wiki/Prorunner) | .pru2 | 
music | [Protracker Module](http://fileformats.archiveteam.org/wiki/Amiga_Module) | .mod | 
music | [RIFF MIDI Music](http://fileformats.archiveteam.org/wiki/RIFF_MIDI) | .rmi | 
music | [RIFF MIDS File](http://fileformats.archiveteam.org/wiki/RIFF_MIDS) | .mds | 
music | [Scream Tracker Module](http://fileformats.archiveteam.org/wiki/S3M) | .s3m .stm | 
music | [Sidmon II Module](http://fileformats.archiveteam.org/wiki/Sidmon) | .sid2 | 
music | [Simple Musical Score](http://fileformats.archiveteam.org/wiki/Amiga_Module) | .smus .song | 
music | [Star Tracker Module](http://fileformats.archiveteam.org/wiki/StarTrekker_/_Star_Tracker_module) | .mod | 
music | [The Player Module](http://fileformats.archiveteam.org/wiki/The_Player) | .p61 .p61a .p60 .p60a .p50 .p50a .p41 .p40 p40a .p40b .p30 p30a .p22 .p22a | 



## Text (21)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
text | [AmigaDOS Script File](https://amigasourcecodepreservation.gitlab.io/mastering-amigados-scripts/) |  | 
text | AMOS Source Code | .amossourcecode | 
text | [Assembly Source File](http://fileformats.archiveteam.org/wiki/Assembly_language) | .asm | 
text | [BASIC Source File](http://fileformats.archiveteam.org/wiki/BASIC) | .bas | 
text | [C Source or Header File](http://fileformats.archiveteam.org/wiki/C) | .c .h | 
text | [C++ Source File](http://fileformats.archiveteam.org/wiki/AIFF) | .cpp .cxx .cc .c++ .hpp | 
text | [Cascading Style Sheet File](http://fileformats.archiveteam.org/wiki/CSS) | .css | 
text | [DOS Batch File](http://fileformats.archiveteam.org/wiki/BAT) | .bat | 
text | [Extensible Markup Language](http://fileformats.archiveteam.org/wiki/XML) | .xml | 
text | File List | .bbs .lst .lis .dir .ind | 
text | [Hypertext Markup Language File](http://fileformats.archiveteam.org/wiki/HTML) | .html .htm .xhtml .xht | 
text | [INI File](http://fileformats.archiveteam.org/wiki/INI) | .ini .cfg .conf | 
text | [Lingo Script](http://fileformats.archiveteam.org/wiki/CSS) |  | 
text | [Linux/UNIX/POSIX Shell Script](http://fileformats.archiveteam.org/wiki/Bourne_shell_script) | .sh .x11 .gnu .csh .tsch | 
text | [Lisp/Scheme](http://fileformats.archiveteam.org/wiki/Lisp) | .lsp | 
text | [Makefile](http://fileformats.archiveteam.org/wiki/CSS) | .mak | 
text | [OS/2 REXX Batch file](https://www.tutorialspoint.com/rexx/index.htm) | .cmd .rexx | 
text | [Pascal/Delphi Source File](http://fileformats.archiveteam.org/wiki/Pascal) | .pas .tp5 | 
text | [Text File](http://fileformats.archiveteam.org/wiki/Text) | .txt .rea .doc .docs .english .credits .cfg .config .78x20 .78*20 .38x20 .38x17 .36x20 .36*20 .advert .advert2 | 
text | [Text File](http://fileformats.archiveteam.org/wiki/Text) |  | 
text | [Windows Registry Data](http://fileformats.archiveteam.org/wiki/Windows_Registry) | .reg .dat | 



## Video (11)
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
video | [Apple QuickTime movie](http://fileformats.archiveteam.org/wiki/MOV) | .mov | 
video | [Audio Video Interleaved Video](http://fileformats.archiveteam.org/wiki/AVI) | .avi | 
video | [Cyber Paint Sequence](http://fileformats.archiveteam.org/wiki/Cyber_Paint_Sequence) | .seq | 
video | Fantavision Movie | .mve |  PLAYER.EXE just loops the video forever, haven't figured out a way to get it to stop after playing once. So I just record for 1 minute and that's the result. Also, there is sound effects but my runUtil Xvfb doesn't support sound recording yet, so no sound. Lastly, I just cheat by running DOSbox and recording the screen, so there is dosbox video at the start heh.
video | [FLIC FLC Video](http://fileformats.archiveteam.org/wiki/FLIC) | .flc | 
video | [FLIC FLI Video](http://fileformats.archiveteam.org/wiki/FLIC) | .fli | 
video | [Interchange File Format Animation](http://fileformats.archiveteam.org/wiki/ANIM) | .anim .anm .sndanim | 
video | [MovieSetter Video](http://fileformats.archiveteam.org/wiki/MovieSetter) | .avi |  Xanim doesn't play sound and my runUtil.recordVirtualX also doesn't record sound Couldn't find another linux based converter that supports sound. Only known solution now would be to convert it on a virtual amiga with MovieSetter itself probably.
video | [MPEG-1](http://fileformats.archiveteam.org/wiki/MPEG-1) | .mpg .mp1 .mpeg .m1v | 
video | [MPEG4 Video](http://fileformats.archiveteam.org/wiki/MP4) | .mp4 .m4v | 
video | [Smacker Video](http://fileformats.archiveteam.org/wiki/Smacker) | .smk | 

