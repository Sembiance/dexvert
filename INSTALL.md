# Install
`npm install dexvert -g`
		
# Requirements

## Kernel
```
File systems  --->
	  Processor type and features --->
	    [*] NUMA Memory Allocation and Scheduler Support
      CD-ROM/DVD Filesystems  --->
	    <*> ISO 9660 CDROM file system support
	    [*]   Microsoft Joliet CDROM extensions
	    [*]   Transparent decompression extension
	    <*>   UDF file system support
	  DOS/FAT/EXFAT/NT Filesystems  --->
	    <*> MSDOS fs support
	    <*> VFAT (Windows-95) fs support
	    (iso8859-1) Default iocharset for FAT
	    <*> exFAT filesystem support
  [*] Miscellaneous filesystems  --->
        <*> Amiga FFS file system support
		<*> Apple Macintosh file system support
		<*> Apple Extended HFS file system support
  -*- Native language support  --->
        <*> Codepage 437 (United States, Canada)
		<*> ASCII (United States)
		<*> NLS ISO 8859-1  (Latin 1; Western European Languages)
		-*- NLS UTF-8
```

## Wine/Amiga
Some win32 wine programs and amiga files are not included due to being commercial software that is still available.

## Programs
Gentoo users can simply install the packages below, some are available in my Gentoo [dexvert overlay](https://github.com/Sembiance/dexvert-gentoo-overlay). Certain Gentoo USE flags may also be require, see further below. Other operating systems have not been tested at all. A docker container could be possible, but there would still need to be certain kernel options set for proper functioning.

Package | Program | Overlay
------- | ------- | -------
app-admin/sudo | [sudo](https://www.sudo.ws/) | 
app-arch/amigadepacker | [amigadepacker](http://zakalwe.fi/~shd/foss/amigadepacker/) | dexvert
app-arch/amitools | [xdftool](http://lallafa.de/blog/amiga-projects/amitools/) | dexvert
app-arch/ancient | [ancient](https://github.com/temisu/ancient_format_decompressor) | dexvert
app-arch/arc | [arc](http://arc.sourceforge.net) | 
app-arch/atari-tools | [atr](https://github.com/jhallen/atari-tools) | dexvert
app-arch/bzip2 | [bunzip2](https://gitlab.com/federicomenaquintero/bzip2) | 
app-arch/deark | [deark](https://entropymine.com/deark/) | dexvert
app-arch/decrmtool | [decrmtool](http://aminet.net/package/util/pack/decrunchmania-mos) | dexvert
app-arch/drxtract | [undirector](https://github.com/System25/drxtract) | dexvert
app-arch/extract-adf | [extract-adf](https://github.com/mist64/extract-adf) | dexvert
app-arch/gameextractor | [gameextractor](http://www.watto.org/game_extractor.html) | dexvert
app-arch/gzip | [gunzip](https://www.gnu.org/software/gzip/) | 
app-arch/helpdeco | [helpdeco](https://sourceforge.net/projects/helpdeco/) | dexvert
app-arch/isextract | [isextract](https://github.com/OmniBlade/isextract) | 
app-arch/lbrate | [lbrate](http://www.svgalib.org/rus/lbrate.html) | dexvert
app-arch/lha | [lha](https://github.com/jca02266/lha) | 
app-arch/mscompress | [msexpand](http://gnuwin32.sourceforge.net/packages/mscompress.htm) | 
app-arch/p7zip | [7z](http://p7zip.sourceforge.net/) | 
app-arch/tar | [tar](https://www.gnu.org/software/tar/) | 
app-arch/trid | [trid](https://mark0.net/soft-trid-e.html) | dexvert
app-arch/ttdecomp | [ttdecomp](http://www.exelana.com/techie/c/ttdecomp.html) | dexvert
app-arch/unar | [unar](https://unarchiver.c3.cx/) | 
app-arch/unice68 | [unice68](https://sourceforge.net/projects/sc68/) | dexvert
app-arch/unlzx | [unlzx](http://xavprods.free.fr/lzx/) | dexvert
app-arch/unrar | [unrar](https://www.rarlab.com/rar_add.htm) | 
app-arch/unrar | [unrar](https://www.rarlab.com/rar_add.htm) | 
app-arch/unshield | [unshield](https://github.com/twogood/unshield) | 
app-arch/unzip | [unzip](http://infozip.sourceforge.net/) | dexvert
app-arch/zoo | [zoo](https://packages.debian.org/jessie/zoo) | 
app-cdr/bchunk | [bchunk](http://he.fi/bchunk/) | 
app-crypt/blake3 | [b3sum](hhttps://github.com/BLAKE3-team/BLAKE3) | 
app-emulation/uade | [uade](http://zakalwe.fi/uade) | 
app-emulation/uade | [uade123](http://zakalwe.fi/uade) | 
app-emulation/vice | [c1541](https://vice-emu.sourceforge.io/) | 
app-emulation/wine-vanilla | [wine](https://www.winehq.org/) | 
app-emulation/wine-vanilla | [winedump](https://www.winehq.org/) | 
app-misc/jq | [jq](https://stedolan.github.io/jq/) | 
app-office/scribus | [scribus](https://www.scribus.net/) | 
app-office/unoconv | [unoconv](http://dag.wiee.rs/home-made/unoconv/) | 
app-shells/bash | [bash](http://tiswww.case.edu/php/chet/bash/bashtop.html) | 
app-text/convmv | [convmv](https://www.j3e.de/linux/convmv/) | 
app-text/djvu | [ddjvu](http://djvu.sourceforge.net/) | 
app-text/ghostpcl-bin | [gpcl6](https://www.ghostscript.com/download/gpcldnld.html) | dexvert
app-text/grotag | [grotag](http://grotag.sourceforge.net/) | dexvert
app-text/lcdf-typetools | [otfinfo](http://www.lcdf.org/type/#typetools) | 
app-text/poppler | [pdfinfo](https://poppler.freedesktop.org/) | 
app-text/xmlstarlet | [xmlstarlet](http://xmlstar.sourceforge.net/) | 
dev-lang/ab2ascii | [ab2ascii](http://aminet.net/package/dev/misc/ab2ascii-1.3) | dexvert
dev-lang/amosbank | [amosbank](https://github.com/dschwen/amosbank) | dexvert
dev-lang/amostools | [dumpamos](https://github.com/kyz/amostools/) | dexvert
dev-lang/amostools | [listamos](https://github.com/kyz/amostools/) | dexvert
dev-lang/gfalist | [gfalist](https://github.com/Sembiance/gfalist) | dexvert
dev-libs/libcdio | [iso-info](https://www.gnu.org/software/libcdio) | 
dev-python/chardet | [chardetect](https://github.com/chardet/chardet) | 
dev-python/flask | [](https://github.com/pallets/flask/) | 
dev-python/pillow | [](https://python-pillow.org/) | 
dev-util/stackimport | [stackimport](https://github.com/uliwitness/stackimport/) | 
games-emulation/dosbox | [dosbox](http://dosbox.sourceforge.net/) | 
media-gfx/abydosconvert | [abydosconvert](https://github.com/Sembiance/abydosconvert) | dexvert
media-gfx/ansilove | [ansilove](https://www.ansilove.org/) | dexvert
media-gfx/dcraw | [dcraw](https://www.cybercom.net/~dcoffin/dcraw/) | 
media-gfx/fontforge | [fontforge](https://fontforge.org) | 
media-gfx/gifsicle | [gifsicle](https://www.lcdf.org/~eddietwo/gifsicle/) | 
media-gfx/imagemagick | [convert](https://www.imagemagick.org/) | 
media-gfx/imagemagick | [identify](https://www.imagemagick.org/) | 
media-gfx/inkscape | [inkscape](https://inkscape.org/) | 
media-gfx/libpgf-tools | [pgf](https://www.libpgf.org/) | 
media-gfx/nconvert | [nconvert](https://www.xnview.com/en/nconvert/) | dexvert
media-gfx/recoil | [recoil2png](http://recoil.sourceforge.net) | dexvert
media-gfx/seq2mp4 | [seq2mp4](https://github.com/Sembiance/seq2mp4) | dexvert
media-gfx/transfig | [fig2dev](https://www.xfig.org/) | 
media-gfx/uniconvertor | [uniconvertor](https://sk1project.net/uc2/) | dexvert
media-gfx/xcftools | [xcf2png](http://henning.makholm.net/software) | dexvert
media-libs/fontconfig | [fc-scan](https://fontconfig.org) | 
media-libs/gd | [gd2topng](https://libgd.org) | 
media-libs/gd | [gdtopng](https://libgd.org) | 
media-libs/libavif | [avifdec](https://github.com/AOMediaCodec/libavif) | dexvert
media-libs/libbpg | [bpgdec](http://bellard.org/bpg/) | dexvert
media-libs/libwebp | [webpinfo](https://developers.google.com/speed/webp/download) | 
media-libs/netpbm | [cistopbm](http://netpbm.sourceforge.net/) | 
media-libs/rlottie | [lottie2gif](https://github.com/Samsung/rlottie) | 
media-sound/adplay | [adplay](https://github.com/adplug/adplay-unix) | 
media-sound/fluid-soundfont | [*](http://musescore.org/en/handbook/soundfont) | 
media-sound/fluidsynth | [fluidsynth](https://github.com/FluidSynth/fluidsynth) | 
media-sound/midistar2mid | [midistar2mid](https://github.com/Sembiance/midistar2mid) | dexvert
media-sound/mikmod2wav | [mikmod2wav](https://github.com/Sembiance/mikmod2wav) | dexvert
media-sound/mikmodInfo | [mikmodInfo](https://github.com/Sembiance/mikmodInfo) | 
media-sound/openmpt123 | [openmpt123](https://lib.openmpt.org/libopenmpt/) | 
media-sound/openmpt123 | [openmpt123](https://lib.openmpt.org/libopenmpt/) | 
media-sound/sidplay | [sidplay2](http://sidplay2.sourceforge.net/) | 
media-sound/sox | [sox](http://sox.sourceforge.net) | 
media-sound/sox | [soxi](http://sox.sourceforge.net) | 
media-sound/timidity-eawpatches | [undefined](http://www.stardate.bc.ca/eawpatches/html/default.htm) | 
media-sound/timidity-freepats | [*](http://freepats.opensrc.org) | 
media-sound/timidity++ | [timidity](http://timidity.sourceforge.net/) | 
media-sound/timidity++ | [timidity](http://timidity.sourceforge.net/) | 
media-sound/xmp | [xmp](http://xmp.sourceforge.net/) | dexvert
media-sound/xmp | [xmp](http://xmp.sourceforge.net/) | 
media-video/ffmpeg | [ffmpeg](https://ffmpeg.org/) | 
media-video/ffmpeg | [ffprobe](https://ffmpeg.org/) | 
media-video/mediainfo | [mediainfo](https://github.com/MediaArea/MediaInfo) | 
media-video/mplayer | [mplayer](http://www.mplayerhq.hu/) | 
media-video/vcdimager | [vcd-info](https://www.gnu.org/software/vcdimager) | 
media-video/vcdimager | [vcdxrip](https://www.gnu.org/software/vcdimager) | 
media-video/xanim | [xanim](http://xanim.polter.net/) | dexvert
sci-libs/tensorflow | [](https://www.tensorflow.org/) | 
sci-misc/h5utils | [h5topng](https://github.com/NanoComp/h5utils/) | 
sys-apps/file | [file](https://www.darwinsys.com/file/) | 
sys-apps/util-linux | [mount](https://www.kernel.org/pub/linux/utils/util-linux/) | 
sys-fs/fuseiso | [fuseiso](https://sourceforge.net/projects/fuseiso) | 
sys-fs/hfsutils | [*](https://www.mars.org/home/rob/proj/hfs/) | 
sys-process/parallel | [parallel](https://www.gnu.org/software/parallel) | 
x11-apps/bdftopcf | [bdftopcf](https://gitlab.freedesktop.org/xorg/app/bdftopcf) | 
x11-base/xorg-server | [Xvfb](https://www.x.org/wiki/) | 
x11-misc/hsetroot | [hsetroot](https://wiki.gentoo.org/wiki/No_homepage) | 
x11-misc/xdotool | [xdotool](https://www.semicomplete.com/projects/xdotool/) | 

Gentoo users can install all the above required programs with this single command:
```
USE="a52 acl alsa amr boost bzip2 cairo cddb cdio cdr cups curl cxx dav1d dbus dga dia dts dv dvd dvdnav enca encode exif faudio ffmpeg flac fontconfig fpx gif gnutls gpl graphicsmagick gtk heif iconv id3tag introspection ipv6 jbig joystick jpeg jpeg2k kpathsea lcms libass libglvnd live lzma lzo mad minimal mms mng mp3 natspec network nls ogg opengl openmp openssl opus osdmenu pch pdf perl png postproc postscript python qt5 readline realtime rle rtc run-exes sdl sdlsound seccomp shm smith sndfile split-usr ssl svg templates tga theora threads tiff truetype twolame unicode unwind utils v4l vaapi vcd vdpau visio vorbis vpx wavpack webp wmf wpg X x264 xattr xcomposite xinerama xml xorg xpm xscreensaver xv xvfb xvid zlib" emerge app-admin/sudo app-arch/amigadepacker app-arch/amitools app-arch/ancient app-arch/arc app-arch/atari-tools app-arch/bzip2 app-arch/deark app-arch/decrmtool app-arch/drxtract app-arch/extract-adf app-arch/gameextractor app-arch/gzip app-arch/helpdeco app-arch/isextract app-arch/lbrate app-arch/lha app-arch/mscompress app-arch/p7zip app-arch/tar app-arch/trid app-arch/ttdecomp app-arch/unar app-arch/unice68 app-arch/unlzx app-arch/unrar app-arch/unshield app-arch/unzip app-arch/zoo app-cdr/bchunk app-crypt/blake3 app-emulation/uade app-emulation/vice app-emulation/wine-vanilla app-misc/jq app-office/scribus app-office/unoconv app-shells/bash app-text/convmv app-text/djvu app-text/ghostpcl-bin app-text/grotag app-text/lcdf-typetools app-text/poppler app-text/xmlstarlet dev-lang/ab2ascii dev-lang/amosbank dev-lang/amostools dev-lang/gfalist dev-libs/libcdio dev-python/chardet dev-python/flask dev-python/pillow dev-util/stackimport games-emulation/dosbox media-gfx/abydosconvert media-gfx/ansilove media-gfx/dcraw media-gfx/fontforge media-gfx/gifsicle media-gfx/imagemagick media-gfx/inkscape media-gfx/libpgf-tools media-gfx/nconvert media-gfx/recoil media-gfx/seq2mp4 media-gfx/transfig media-gfx/uniconvertor media-gfx/xcftools media-libs/fontconfig media-libs/gd media-libs/libavif media-libs/libbpg media-libs/libwebp media-libs/netpbm media-libs/rlottie media-sound/adplay media-sound/fluid-soundfont media-sound/fluidsynth media-sound/midistar2mid media-sound/mikmod2wav media-sound/mikmodInfo media-sound/openmpt123 media-sound/sidplay media-sound/sox media-sound/timidity-eawpatches media-sound/timidity-freepats media-sound/timidity++ media-sound/xmp media-video/ffmpeg media-video/mediainfo media-video/mplayer media-video/vcdimager media-video/xanim sci-libs/tensorflow sci-misc/h5utils sys-apps/file sys-apps/util-linux sys-fs/fuseiso sys-fs/hfsutils sys-process/parallel x11-apps/bdftopcf x11-base/xorg-server x11-misc/hsetroot x11-misc/xdotool
```