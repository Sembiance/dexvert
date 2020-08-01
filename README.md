# dexvert - Decompress EXtract conVERT

Convert 259 old file formats into modern ones. Powered by NodeJS, Gentoo and a ton of helper programs.

See [SUPPORTED.md](SUPPORTED.md) and [UNSUPPORTED.md](UNSUPPORTED.md) for file formats that are supported or unsupported.

## Install
dexvert requires a LOT of programs and some kernel options to be set. See Requirements below. Once satisified, install with:
`npm install dexvert -g`

## Usage
```
Usage: dexvert [options] <inputFilePath> <outputDirPath>

Processes <inputFilePath> converting or extracting files into <outputDirPath>

Options:
  --verbose=<level>
    Show additional info when processing. Levels 1 to 5 where 5 is most verbose

   --brute=<family>,<family>
    If unable to identify <inputFilePath>, try converting anyways
    Pass a comma delimited list of families to brute force try
    Valid families: archive document audio music video image 3d font other executable rom text or all
    Successes will be stored in <outputDirPath>/<family>/<format>/ sub dirs
    WARNING: Multiple successes could use a lot of disk space

   --keepGoing
    When brute forcing, don't stop at the first success. Try them all.

   --alwaysBrute
    When brute forcing, always brute force, even if we have an exact id match.

   --tmpDirPath=/mnt/tmp
    Use a different tmp dir (default is os.tmpdir())
	I suggest setting this to a 'tmpfs' mounted RAM disk.

   --brutePrograms
    If unable to identify <inputFilePath> just run every available program on it

   --midiFont=<midiFont>
    Convert MIDI files with a specific midi font. Default: eaw
	Other available fonts: fluid, roland, creative, freepats, windows
  
   --help
    Displays this usage message

```

In order for documents to convert correctly, a single 'unoconv' daemon needs to be running. So 'dexserv' must be running in the background:
```
Usage: dexserv [options]

Starts a server to assist dexvert. Required for 'unoconv' doc conversion.

Options:
  --help
    Display help/usage

```

You can also just 'identify' what a file is, without processing it by running 'dexid':
```
Usage: dexid [options] <inputFilePath>

Identifies <inputFilePath>. Like an advanced 'file' command

Options:
  --verbose=<level>
    Show additional info when identifying. Levels 1 to 5 where 5 is most verbose

  --help
    Display help/usage
  
  --json
    Output JSON

```

Use as a nodejs module:

```javascript
const dexvert = require("dexvert");

dexvert.process(inputFilePath, outputDirPath, options, cb);
dexvert.identify(inputFilePath, options, cb);
```

# Requirements

## Kernel
```
File systems  --->
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

## Programs
Gentoo users can simply install the packages below, some are available in my Gentoo [dexvert overlay](https://github.com/Sembiance/dexvert-gentoo-overlay). Certain Gentoo USE flags may also be require, see further below. Other operating systems have not been tested at all. A docker container could be possible, but there would still need to be certain kernel options set for proper functioning.

Package | Program | Overlay
------- | ------- | -------
app-admin/sudo | [sudo](https://www.sudo.ws/) | 
app-arch/amigadepacker | [amigadepacker](http://zakalwe.fi/~shd/foss/amigadepacker/) | dexvert
app-arch/amitools | [xdftool](http://lallafa.de/blog/amiga-projects/amitools/) | dexvert
app-arch/ancient | [ancient](https://github.com/temisu/ancient_format_decompressor) | dexvert
app-arch/arc | [arc](http://arc.sourceforge.net) | 
app-arch/bzip2 | [bunzip2](https://gitlab.com/federicomenaquintero/bzip2) | 
app-arch/deark | [deark](https://entropymine.com/deark/) | dexvert
app-arch/decrmtool | [decrmtool](http://aminet.net/package/util/pack/decrunchmania-mos) | dexvert
app-arch/drxtract | [undirector](https://github.com/System25/drxtract) | dexvert
app-arch/extract-adf | [extract-adf](https://github.com/mist64/extract-adf) | dexvert
app-arch/fido | [fido](https://openpreservation.org/products/fido/) | dexvert
app-arch/gameextractor | [gameextractor](http://www.watto.org/game_extractor.html) | dexvert
app-arch/gzip | [gunzip](https://www.gnu.org/software/gzip/) | 
app-arch/helpdeco | [helpdeco](https://sourceforge.net/projects/helpdeco/) | dexvert
app-arch/lbrate | [lbrate](http://www.svgalib.org/rus/lbrate.html) | dexvert
app-arch/lha | [lha](https://github.com/jca02266/lha) | 
app-arch/mscompress | [msexpand](http://gnuwin32.sourceforge.net/packages/mscompress.htm) | 
app-arch/p7zip | [7z](http://p7zip.sourceforge.net/) | 
app-arch/tar | [tar](https://www.gnu.org/software/tar/) | 
app-arch/trid | [trid](https://mark0.net/soft-trid-e.html) | dexvert
app-arch/ttdecomp | [ttdecomp](http://www.exelana.com/techie/c/ttdecomp.html) | dexvert
app-arch/unar | [unar](https://unarchiver.c3.cx/) | 
app-arch/unice68 | [unice68](https://sourceforge.net/projects/sc68/) | dexvert
app-arch/unrar | [unrar](https://www.rarlab.com/rar_add.htm) | 
app-arch/unzip | [unzip](http://infozip.sourceforge.net/) | dexvert
app-cdr/bchunk | [bchunk](http://he.fi/bchunk/) | 
app-cdr/nrg2iso | [nrg2iso](http://gregory.kokanosky.free.fr/v4/linux/nrg2iso.en.html) | 
app-emulation/uade | [uade](http://zakalwe.fi/uade) | 
app-emulation/uade | [uade123](http://zakalwe.fi/uade) | 
app-emulation/wine-vanilla | [wine](https://www.winehq.org/) | 
app-office/unoconv | [unoconv](http://dag.wiee.rs/home-made/unoconv/) | 
app-shells/bash | [bash](http://tiswww.case.edu/php/chet/bash/bashtop.html) | 
app-text/convmv | [convmv](https://www.j3e.de/linux/convmv/) | 
app-text/djvu | [ddjvu](http://djvu.sourceforge.net/) | 
app-text/ghostpcl-bin | [gpcl6](https://www.ghostscript.com/download/gpcldnld.html) | dexvert
app-text/grotag | [grotag](http://grotag.sourceforge.net/) | dexvert
app-text/poppler | [pdfinfo](https://poppler.freedesktop.org/) | 
dev-lang/ab2ascii | [ab2ascii](http://aminet.net/package/dev/misc/ab2ascii-1.3) | dexvert
dev-lang/amosbank | [amosbank](https://github.com/dschwen/amosbank) | dexvert
dev-lang/amostools | [dumpamos](https://github.com/kyz/amostools/) | dexvert
dev-lang/amostools | [listamos](https://github.com/kyz/amostools/) | dexvert
dev-libs/libcdio | [iso-info](https://www.gnu.org/software/libcdio) | 
dev-util/stackimport | [stackimport](https://github.com/uliwitness/stackimport/) | 
games-emulation/dosbox | [dosbox](http://dosbox.sourceforge.net/) | 
media-gfx/abydosconvert | [abydosconvert](https://github.com/Sembiance/abydosconvert) | dexvert
media-gfx/ansilove | [ansilove](https://www.ansilove.org/) | dexvert
media-gfx/gifsicle | [gifsicle](https://www.lcdf.org/~eddietwo/gifsicle/) | 
media-gfx/imagemagick | [convert](https://www.imagemagick.org/) | 
media-gfx/imagemagick | [identify](https://www.imagemagick.org/) | 
media-gfx/nconvert | [nconvert](https://www.xnview.com/en/nconvert/) | dexvert
media-gfx/recoil | [recoil2png](http://recoil.sourceforge.net) | dexvert
media-gfx/xcftools | [xcf2png](http://henning.makholm.net/software) | dexvert
media-libs/libavif | [avifdec](https://github.com/AOMediaCodec/libavif) | dexvert
media-libs/libbpg | [bpgdec](http://bellard.org/bpg/) | dexvert
media-libs/libwebp | [webpinfo](https://developers.google.com/speed/webp/download) | 
media-sound/adplay | [adplay](https://github.com/adplug/adplay-unix) | 
media-sound/fluid-soundfont | [*](http://musescore.org/en/handbook/soundfont) | 
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
media-video/ffmpeg | [ffmpeg](https://ffmpeg.org/) | 
media-video/mplayer | [mplayer](http://www.mplayerhq.hu/) | 
media-video/xanim | [xanim](http://xanim.polter.net/) | dexvert
sys-apps/file | [file](https://www.darwinsys.com/file/) | 
sys-apps/util-linux | [mount](https://www.kernel.org/pub/linux/utils/util-linux/) | 
sys-fs/hfsutils | [*](https://www.mars.org/home/rob/proj/hfs/) | 
sys-process/parallel | [parallel](https://www.gnu.org/software/parallel) | 
x11-base/xorg-server | [Xvfb](https://www.x.org/wiki/) | 
x11-misc/hsetroot | [hsetroot](https://wiki.gentoo.org/wiki/No_homepage) | 
x11-misc/xdotool | [xdotool](https://www.semicomplete.com/projects/xdotool/) | 

Gentoo users can install all the above with this single command:
```
USE="a52 acl alsa amr bzip2 cairo cddb cdio curl cxx dga dts dv dvd dvdnav enca encode flac fontconfig fpx gif gpl heif iconv id3tag introspection jbig joystick jpeg jpeg2k lcms libass libglvnd live lzma lzo mad mng mp3 natspec network nls ogg opengl openmp openssl opus osdmenu pch png postproc postscript qt5 rtc seccomp shm smith sndfile svg tga theora threads tiff truetype twolame unicode utils v4l vaapi vcd vdpau vorbis vpx wavpack webp wmf X x264 xattr xinerama xml xorg xscreensaver xv xvfb xvid zlib" emerge app-admin/sudo app-arch/amigadepacker app-arch/amitools app-arch/ancient app-arch/arc app-arch/bzip2 app-arch/deark app-arch/decrmtool app-arch/drxtract app-arch/extract-adf app-arch/fido app-arch/gameextractor app-arch/gzip app-arch/helpdeco app-arch/lbrate app-arch/lha app-arch/mscompress app-arch/p7zip app-arch/tar app-arch/trid app-arch/ttdecomp app-arch/unar app-arch/unice68 app-arch/unrar app-arch/unzip app-cdr/bchunk app-cdr/nrg2iso app-emulation/uade app-emulation/wine-vanilla app-office/unoconv app-shells/bash app-text/convmv app-text/djvu app-text/ghostpcl-bin app-text/grotag app-text/poppler dev-lang/ab2ascii dev-lang/amosbank dev-lang/amostools dev-libs/libcdio dev-util/stackimport games-emulation/dosbox media-gfx/abydosconvert media-gfx/ansilove media-gfx/gifsicle media-gfx/imagemagick media-gfx/nconvert media-gfx/recoil media-gfx/xcftools media-libs/libavif media-libs/libbpg media-libs/libwebp media-sound/adplay media-sound/fluid-soundfont media-sound/midistar2mid media-sound/mikmod2wav media-sound/mikmodInfo media-sound/openmpt123 media-sound/sidplay media-sound/sox media-sound/timidity-eawpatches media-sound/timidity-freepats media-sound/timidity++ media-sound/xmp media-video/ffmpeg media-video/mplayer media-video/xanim sys-apps/file sys-apps/util-linux sys-fs/hfsutils sys-process/parallel x11-base/xorg-server x11-misc/hsetroot x11-misc/xdotool
```
		