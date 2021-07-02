# WARNING
Over 172 programs are required, including commercial programs and operating systems.
This isn't something you can easily get up and running in an afternoon.
		
# Install
GIT clone the repo
		
# Requirements

## Kernel
Several kernel options need to enabled to support QEMU, docker and mounting various fileystems dexvert may encounter.

```
    General setup  --->
      <*> Control Group support  --->
            [*] Memory controller
            [*] Freezer controller
            [*] Cpuset Controller
            [*]   Include legacy /proc/<pid>/cpuset file
            [*] Simple CPU accounting controller

    Processor type and features --->
      [*] NUMA Memory Allocation and Scheduler Support

[*] Virtualization  --->
      <*> Kernel-based Virtual Machine (KVM) support
	  # Choose either Intel or AMD
      <*>   KVM for Intel (and compatible) processors support
	  <*>   KVM for AMD processors support

[*] Networking support  --->
    Networking options  --->
	  <*> 802.1d Ethernet bridging
	  [*]   IGMP/MLD snooping

    Device Drivers  --->
      [*] PCI support  --->
	        [*] Message Signaled Interrupts (MSI and MSI-X)
      [*] Network device support  --->
            [*]   Network core driver support
            <*>     MAC-VLAN support
            <*>       MAC-VLAN based tap driver
            <*>   Universal TUN/TAP device driver support
      [*] VHOST drivers  --->
            [*] Host kernel accelerator for virtio net
            [*] Cross-endian support for vhost
      [*] IOMMU Hardware Support  --->
	        # Choose either Intel or AMD
			[*] AMD IOMMU support
			<*>   AMD IOMMU Version 2 driver
            [*] Support for Intel IOMMU using DMA Remapping Devices
            [*]   Support for Shared Virtual Memory with Intel IOMMU
            [*]   Enable Intel DMA Remapping Devices by default

    File systems  --->
      <*> The Extended 4 (ext4) filesystem
	  [*]   Ext4 Security Labels
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
    		<*> NTFS file system support
      [*] Miscellaneous filesystems  --->
            <*> ADFS file system support
            <*> Amiga FFS file system support
    		<*> Apple Macintosh file system support
    		<*> Apple Extended HFS file system support
    		<*> BeOS file system (BeFS) support (read only)
    		<*> EFS file system support (read only)
    		<*> Minix file system support
    		<*> OS/2 HPFS file system support
    		<*> ROM file system support
    		<*> System V/Xenix/V7/Coherent file system support
    		<*> UFS file system support
    		<*> EROFS file system support
      [*] Network File Systems  --->
    	    <*> SMB3 and CIFS support (advanced network filesystem)
    		[*]   Support legacy servers which use less secure dialects
    		[*]     Support legacy servers which use weaker LANMAN security
    		[*]   CIFS extended attributes
      -*- Native language support  --->
            <*> Codepage 437 (United States, Canada)
    		<*> ASCII (United States)
    		<*> NLS ISO 8859-1  (Latin 1; Western European Languages)
    		-*- NLS UTF-8

    Kernel hacking  --->
          Generic Kernel Debugging Instruments  --->
            [*] Debug Filesystem
```

Also everything detailed here: https://wiki.gentoo.org/wiki/Docker

## Windows/Amiga
Some windows and amiga files are not included due to being commercial software that is still available. This includes the HD images used by the QEMU layer. Sorry.

## Programs
Package | Program | Overlay
------- | ------- | -------
app-admin/sudo | [sudo](https://www.sudo.ws/) | 
app-arch/amigadepacker | [amigadepacker](http://zakalwe.fi/~shd/foss/amigadepacker/) | dexvert
app-arch/amitools | [xdftool](http://lallafa.de/blog/amiga-projects/amitools/) | dexvert
app-arch/ancient | [ancient](https://github.com/temisu/ancient_format_decompressor) | dexvert
app-arch/arc | [arc](http://arc.sourceforge.net) | 
app-arch/atari-tools | [atr](https://github.com/jhallen/atari-tools) | dexvert
app-arch/bzip2 | [bunzip2](https://gitlab.com/federicomenaquintero/bzip2) | 
app-arch/cabextract | [cabextract](https://www.cabextract.org.uk/) | 
app-arch/cpcxfs | [cpcxfs](http://www.cpcwiki.eu/forum/applications/cpcxfs/) | dexvert
app-arch/deark | [deark](https://entropymine.com/deark/) | dexvert
app-arch/decrunchmania | [decrmtool](http://aminet.net/package/util/pack/decrunchmania-mos) | dexvert
app-arch/drxtract | [undirector](https://github.com/System25/drxtract) | dexvert
app-arch/extract-adf | [extract-adf](https://github.com/mist64/extract-adf) | dexvert
app-arch/gzip | [gunzip](https://www.gnu.org/software/gzip/) | 
app-arch/helpdeco | [helpdeco](https://sourceforge.net/projects/helpdeco/) | dexvert
app-arch/inivalidate | [inivalidate](https://github.com/Sembiance/inivalidate) | dexvert
app-arch/isextract | [isextract](https://github.com/OmniBlade/isextract) | 
app-arch/lbrate | [lbrate](http://www.svgalib.org/rus/lbrate.html) | dexvert
app-arch/lha | [lha](https://github.com/jca02266/lha) | 
app-arch/mscompress | [msexpand](http://gnuwin32.sourceforge.net/packages/mscompress.htm) | 
app-arch/p7zip | [7z](http://p7zip.sourceforge.net/) | 
app-arch/resource-dasm | [hypercard_dasm](https://github.com/fuzziqersoftware/resource_dasm) | dexvert
app-arch/resource-dasm | [resource_dasm](https://github.com/fuzziqersoftware/resource_dasm) | dexvert
app-arch/tar | [tar](https://www.gnu.org/software/tar/) | 
app-arch/trid | [trid](https://mark0.net/soft-trid-e.html) | dexvert
app-arch/ttdecomp | [ttdecomp](http://www.exelana.com/techie/c/ttdecomp.html) | dexvert
app-arch/unadf | [unadf](http://lclevy.free.fr/adflib/) | 
app-arch/unar | [unar](https://unarchiver.c3.cx/) | 
app-arch/unice68 | [unice68](https://sourceforge.net/projects/sc68/) | dexvert
app-arch/unlzx | [unlzx](http://xavprods.free.fr/lzx/) | dexvert
app-arch/unrar | [unrar](https://www.rarlab.com/rar_add.htm) | 
app-arch/unrar | [unrar](https://www.rarlab.com/rar_add.htm) | 
app-arch/unshield | [unshield](https://github.com/twogood/unshield) | 
app-arch/unzip | [unzip](http://infozip.sourceforge.net/) | dexvert
app-arch/zoo | [zoo](https://packages.debian.org/jessie/zoo) | 
app-cdr/bchunk | [bchunk](http://he.fi/bchunk/) | 
app-cdr/cdrdao | [toc2cue](http://cdrdao.sourceforge.net/) | 
app-crypt/blake3 | [b3sum](hhttps://github.com/BLAKE3-team/BLAKE3) | 
app-emulation/docker | [](https://www.docker.com/) | 
app-emulation/nvidia-container-toolkit | [](https://github.com/NVIDIA/nvidia-container-toolkit) | dexvert
app-emulation/qemu | [qemu-system-*](http://www.qemu.org) | 
app-emulation/uade | [uade](http://zakalwe.fi/uade) | 
app-emulation/uade | [uade123](http://zakalwe.fi/uade) | 
app-emulation/vice | [c1541](https://vice-emu.sourceforge.io/) | 
app-emulation/wine-vanilla | [winedump](https://www.winehq.org/) | 
app-misc/jq | [jq](https://stedolan.github.io/jq/) | 
app-office/scribus | [scribus](https://www.scribus.net/) | 
app-shells/bash | [bash](http://tiswww.case.edu/php/chet/bash/bashtop.html) | 
app-text/antixls | [antixls](https://packages.gentoo.org/packages/app-text/antixls) | 
app-text/convmv | [convmv](https://www.j3e.de/linux/convmv/) | 
app-text/djvu | [ddjvu](http://djvu.sourceforge.net/) | 
app-text/ghostpcl-bin | [gpcl6](https://www.ghostscript.com/download/gpcldnld.html) | dexvert
app-text/grotag | [grotag](http://grotag.sourceforge.net/) | dexvert
app-text/lcdf-typetools | [otfinfo](http://www.lcdf.org/type/#typetools) | 
app-text/libgxps | [xpstopdf](https://wiki.gnome.org/Projects/libgxps) | 
app-text/poppler | [pdfinfo](https://poppler.freedesktop.org/) | 
app-text/xmlstarlet | [xmlstarlet](http://xmlstar.sourceforge.net/) | 
dev-lang/ab2ascii | [ab2ascii](http://aminet.net/package/dev/misc/ab2ascii-1.3) | dexvert
dev-lang/amosbank | [amosbank](https://github.com/dschwen/amosbank) | dexvert
dev-lang/amostools | [dumpamos](https://github.com/kyz/amostools/) | dexvert
dev-lang/amostools | [listamos](https://github.com/kyz/amostools/) | dexvert
dev-lang/gfalist | [gfalist](https://github.com/Sembiance/gfalist) | dexvert
dev-libs/libcdio | [iso-info](https://www.gnu.org/software/libcdio) | 
dev-python/chardet | [chardetect](https://github.com/chardet/chardet) | 
dev-util/stackimport | [stackimport](https://github.com/uliwitness/stackimport/) | 
games-emulation/dosbox | [dosbox](http://dosbox.sourceforge.net/) | dexvert
games-util/gameextractor | [gameextractor](http://www.watto.org/game_extractor.html) | dexvert
games-util/reko2png | [reko2png](https://github.com/Sembiance/reko2png) | dexvert
media-gfx/abydosconvert | [abydosconvert](https://github.com/Sembiance/abydosconvert) | dexvert
media-gfx/ansilove | [ansilove](https://www.ansilove.org/) | dexvert
media-gfx/darktable | [darktable-cli](https://www.darktable.org/) | 
media-gfx/dcraw | [dcraw](https://www.cybercom.net/~dcoffin/dcraw/) | 
media-gfx/fontforge | [fontforge](https://fontforge.org) | 
media-gfx/gifsicle | [gifsicle](https://www.lcdf.org/~eddietwo/gifsicle/) | 
media-gfx/imagemagick | [convert](https://www.imagemagick.org/) | 
media-gfx/imagemagick | [identify](https://www.imagemagick.org/) | 
media-gfx/inkscape | [inkscape](https://inkscape.org/) | 
media-gfx/libpgf-tools | [pgf](https://www.libpgf.org/) | 
media-gfx/libredwg | [dwg2SVG](https://www.gnu.org/software/libredwg/) | 
media-gfx/nconvert | [nconvert](https://www.xnview.com/en/nconvert/) | dexvert
media-gfx/pablodraw-console | [pablodraw-console](http://picoe.ca/products/pablodraw/) | dexvert
media-gfx/pcdtojpeg | [pcdtojpeg](https://pcdtojpeg.sourceforge.io/Home.html) | dexvert
media-gfx/pfstools | [pfsconvert](http://pfstools.sourceforge.net/) | dexvert
media-gfx/qcad-professional | [dwg2bmp](https://qcad.org/en/) | dexvert
media-gfx/recoil | [recoil2png](http://recoil.sourceforge.net) | dexvert
media-gfx/seq2mp4 | [seq2mp4](https://github.com/Sembiance/seq2mp4) | dexvert
media-gfx/svgdim | [svgdim](https://github.com/Sembiance/svgdim) | dexvert
media-gfx/transfig | [fig2dev](https://www.xfig.org/) | 
media-gfx/uniconvertor | [uniconvertor](https://sk1project.net/uc2/) | dexvert
media-gfx/view64 | [view64pnm](http://view64.sourceforge.net/) | dexvert
media-gfx/xcftools | [xcf2png](http://henning.makholm.net/software) | dexvert
media-libs/fontconfig | [fc-scan](https://fontconfig.org) | 
media-libs/gd | [gd2topng](https://libgd.org) | 
media-libs/gd | [gdtopng](https://libgd.org) | 
media-libs/libavif | [avifdec](https://github.com/AOMediaCodec/libavif) | dexvert
media-libs/libbpg | [bpgdec](http://bellard.org/bpg/) | dexvert
media-libs/libpuzzle | [puzzle-diff](http://www.pureftpd.org/project/libpuzzle) | dexvert
media-libs/libwebp | [webpinfo](https://developers.google.com/speed/webp/download) | 
media-libs/netpbm | [cistopbm](http://netpbm.sourceforge.net/) | 
media-libs/rlottie | [lottie2gif](https://github.com/Samsung/rlottie) | 
media-sound/adplay | [adplay](https://github.com/adplug/adplay-unix) | 
media-sound/asap | [asapconv](http://asap.sourceforge.net/) | dexvert
media-sound/eupmini | [eupplay](https://github.com/gzaffin/eupmini) | dexvert
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
media-sound/zxtune | [zxtune123](https://zxtune.bitbucket.io/) | dexvert
media-video/ffmpeg | [ffmpeg](https://ffmpeg.org/) | 
media-video/ffmpeg | [ffprobe](https://ffmpeg.org/) | 
media-video/mediainfo | [mediainfo](https://github.com/MediaArea/MediaInfo) | 
media-video/mplayer | [mplayer](http://www.mplayerhq.hu/) | 
media-video/vcdimager | [vcd-info](https://www.gnu.org/software/vcdimager) | 
media-video/vcdimager | [vcdxrip](https://www.gnu.org/software/vcdimager) | 
media-video/xanim | [xanim](https://github.com/Sembiance/xanim) | dexvert
net-fs/cifs-utils | [mount.cifs](https://wiki.samba.org/index.php/LinuxCIFS_utils) | 
net-misc/rsync | [rsync](https://rsync.samba.org/) | 
net-misc/vncsnapshot | [vncsnapshot](http://vncsnapshot.sourceforge.net/) | 
sci-misc/h5utils | [h5topng](https://github.com/NanoComp/h5utils/) | 
sys-apps/file | [file](https://www.darwinsys.com/file/) | 
sys-apps/util-linux | [mount](https://www.kernel.org/pub/linux/utils/util-linux/) | 
sys-devel/binutils | [strings](https://www.gnu.org/software/binutils/) | 
sys-fs/fuseiso | [fuseiso](https://sourceforge.net/projects/fuseiso) | 
sys-fs/hfsutils | [*](https://www.mars.org/home/rob/proj/hfs/) | 
sys-process/parallel | [parallel](https://www.gnu.org/software/parallel) | 
x11-apps/bdftopcf | [bdftopcf](https://gitlab.freedesktop.org/xorg/app/bdftopcf) | 
x11-base/xorg-server | [Xvfb](https://www.x.org/wiki/) | 
x11-drivers/xf86-video-qxl | [](https://gitlab.freedesktop.org/xorg/driver/xf86-video-qxl) | 
x11-misc/hsetroot | [hsetroot](https://wiki.gentoo.org/wiki/No_homepage) | 
x11-misc/xdotool | [xdotool](https://www.semicomplete.com/projects/xdotool/) | 

## Gentoo
The [dexvert overlay](https://github.com/Sembiance/dexvert-gentoo-overlay) is required for many programs, it contains patches for other programs too.

Certain Gentoo USE flags may also be required for proper feature support.

You should be able to install everything you need on Gentoo with this one command:

```
USE="a52 acl aio alsa amr boost bzip2 cairo caps cddb cdio cdr creds cups curl cxx dav1d dbus dga dia dts dv dvd dvdnav enca encode exif faudio fdt ffmpeg fftw filecaps flac fontconfig fpx gif gnutls gpl graphicsmagick gsl gtk heif iconv id3tag imagemagick introspection ipv6 jbig joystick jpeg jpeg2k kpathsea lcms libass libglvnd live lua lzma lzo mad minimal mms mng mp3 natspec ncurses netpbm network nls ogg openexr opengl openmp openssl opus osdmenu oss pam pch pdf perl pin-upstream-blobs png postproc postscript python qt5 readline realtime rle rtc run-exes sdl sdlsound seccomp shm slirp smith sndfile spice split-usr ssl svg templates tga theora threads tiff truetype twolame unicode unwind usb usbredir utils v4l vaapi vcd vdpau vhost-net visio vnc vorbis vpx wavpack webp wmf wpg X x264 xattr xcomposite xinerama xml xorg xpm xscreensaver xspice xv xvfb xvid zlib zstd" emerge app-admin/sudo app-arch/amigadepacker app-arch/amitools app-arch/ancient app-arch/arc app-arch/atari-tools app-arch/bzip2 app-arch/cabextract app-arch/cpcxfs app-arch/deark app-arch/decrunchmania app-arch/drxtract app-arch/extract-adf app-arch/gzip app-arch/helpdeco app-arch/inivalidate app-arch/isextract app-arch/lbrate app-arch/lha app-arch/mscompress app-arch/p7zip app-arch/resource-dasm app-arch/tar app-arch/trid app-arch/ttdecomp app-arch/unadf app-arch/unar app-arch/unice68 app-arch/unlzx app-arch/unrar app-arch/unshield app-arch/unzip app-arch/zoo app-cdr/bchunk app-cdr/cdrdao app-crypt/blake3 app-emulation/docker app-emulation/nvidia-container-toolkit app-emulation/qemu app-emulation/uade app-emulation/vice app-emulation/wine-vanilla app-misc/jq app-office/scribus app-shells/bash app-text/antixls app-text/convmv app-text/djvu app-text/ghostpcl-bin app-text/grotag app-text/lcdf-typetools app-text/libgxps app-text/poppler app-text/xmlstarlet dev-lang/ab2ascii dev-lang/amosbank dev-lang/amostools dev-lang/gfalist dev-libs/libcdio dev-python/chardet dev-util/stackimport games-emulation/dosbox games-util/gameextractor games-util/reko2png media-gfx/abydosconvert media-gfx/ansilove media-gfx/darktable media-gfx/dcraw media-gfx/fontforge media-gfx/gifsicle media-gfx/imagemagick media-gfx/inkscape media-gfx/libpgf-tools media-gfx/libredwg media-gfx/nconvert media-gfx/pablodraw-console media-gfx/pcdtojpeg media-gfx/pfstools media-gfx/qcad-professional media-gfx/recoil media-gfx/seq2mp4 media-gfx/svgdim media-gfx/transfig media-gfx/uniconvertor media-gfx/view64 media-gfx/xcftools media-libs/fontconfig media-libs/gd media-libs/libavif media-libs/libbpg media-libs/libpuzzle media-libs/libwebp media-libs/netpbm media-libs/rlottie media-sound/adplay media-sound/asap media-sound/eupmini media-sound/fluid-soundfont media-sound/fluidsynth media-sound/midistar2mid media-sound/mikmod2wav media-sound/mikmodInfo media-sound/openmpt123 media-sound/sidplay media-sound/sox media-sound/timidity-eawpatches media-sound/timidity-freepats media-sound/timidity++ media-sound/xmp media-sound/zxtune media-video/ffmpeg media-video/mediainfo media-video/mplayer media-video/vcdimager media-video/xanim net-fs/cifs-utils net-misc/rsync net-misc/vncsnapshot sci-misc/h5utils sys-apps/file sys-apps/util-linux sys-devel/binutils sys-fs/fuseiso sys-fs/hfsutils sys-process/parallel x11-apps/bdftopcf x11-base/xorg-server x11-drivers/xf86-video-qxl x11-misc/hsetroot x11-misc/xdotool
```