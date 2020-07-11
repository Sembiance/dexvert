# dexvert - Decompress EXtract conVERT

This is a nodejs based program that can decompress, extract and convert a wide variety of old file formats to modern day equilivants.

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
    Valid families: archive document audio database 3d font video image other executable text or all
    Successes will be stored in <outputDirPath>/<family>/<format>/ sub dirs
    WARNING: Multiple successes could use a lot of disk space

   --keepGoing
    When brute forcing, don't stop at the first success. Try them all.

   --tmpDirPath=/mnt/tmp
    Use a different tmp dir (default is os.tmpdir())
  
   --help
    Displays this usage message

```

```
Usage: dexid [options] <inputFilePath>

Identifies <inputFilePath>. Like an advanced 'file' command

Options:
  --help
    Display help/usage
  
  --json
    Output JSON

```

Use as a nodejs module:

```javascript
const dexvert = require("dexvert");

dexvert.process(inputFilePath, outputDirPath, options, cb);
dexvert.identify(inputFilePath, cb);
```

# Requirements

## Kernel
WIP

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
app-arch/lbrate | [lbrate](http://www.svgalib.org/rus/lbrate.html) | dexvert
app-arch/lha | [lha](https://github.com/jca02266/lha) | 
app-arch/mscompress | [msexpand](http://gnuwin32.sourceforge.net/packages/mscompress.htm) | 
app-arch/p7zip | [7z](http://p7zip.sourceforge.net/) | 
app-arch/tar | [tar](https://www.gnu.org/software/tar/) | 
app-arch/trid | [trid](https://mark0.net/soft-trid-e.html) | dexvert
app-arch/ttdecomp | [ttdecomp](http://www.exelana.com/techie/c/ttdecomp.html) | dexvert
app-arch/unar | [unar](https://unarchiver.c3.cx/) | 
app-arch/unpcx | [unpcx](http://www.ctpax-x.org/?goto=files&show=104) | dexvert
app-arch/unrar | [unrar](https://www.rarlab.com/rar_add.htm) | 
app-arch/unzip | [unzip](http://infozip.sourceforge.net/) | dexvert
app-cdr/bchunk | [bchunk](http://he.fi/bchunk/) | 
app-shells/bash | [bash](http://tiswww.case.edu/php/chet/bash/bashtop.html) | 
dev-lang/amostools | [dumpamos](https://github.com/kyz/amostools/) | dexvert
dev-lang/amostools | [listamos](https://github.com/kyz/amostools/) | dexvert
dev-util/stackimport | [stackimport](https://github.com/uliwitness/stackimport/) | 
media-video/ffmpeg | [ffmpeg](https://ffmpeg.org/) | 
sys-apps/file | [file](https://www.darwinsys.com/file/) | 
sys-fs/hfsutils | [*](https://www.mars.org/home/rob/proj/hfs/) | 
sys-process/parallel | [parallel](https://www.gnu.org/software/parallel) | 
x11-base/xorg-server | [Xvfb](https://www.x.org/wiki/) | 
x11-misc/hsetroot | [hsetroot](https://wiki.gentoo.org/wiki/No_homepage) | 

Gentoo users can install all the above with this single command:
```
USE="acl alsa amr bzip2 encode fontconfig gpl iconv jpeg2k libglvnd lzma mp3 natspec network nls opengl openssl opus pch postproc seccomp smith svg theora threads truetype unicode v4l vaapi vdpau vorbis vpx webp X x264 xattr xorg xvfb xvid zlib" emerge app-admin/sudo app-arch/amigadepacker app-arch/amitools app-arch/ancient app-arch/arc app-arch/bzip2 app-arch/deark app-arch/decrmtool app-arch/drxtract app-arch/extract-adf app-arch/fido app-arch/gameextractor app-arch/gzip app-arch/lbrate app-arch/lha app-arch/mscompress app-arch/p7zip app-arch/tar app-arch/trid app-arch/ttdecomp app-arch/unar app-arch/unpcx app-arch/unrar app-arch/unzip app-cdr/bchunk app-shells/bash dev-lang/amostools dev-util/stackimport media-video/ffmpeg sys-apps/file sys-fs/hfsutils sys-process/parallel x11-base/xorg-server x11-misc/hsetroot
```
		