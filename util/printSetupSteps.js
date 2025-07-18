import {xu} from "xu";
import {programs, init as initPrograms} from "../src/program/programs.js";
await initPrograms();

console.log("Follow ipmi.txt and bios.txt to connect and get the server booting from my custom gentooInstall ISO");
console.log("Follow gentoo_install.txt to assign an IP address and get networking working");
console.log("Install gentoo with: gentooInstall --phase=2 --withX --withQEMU --withNode --withSound --gateway=<gateway> <ip> <hostname>");
console.log("Run the following as root on a fresh Gentoo system to be able to run dexvert:\n");

[
	`cd /etc/portage/package.use && ln -s /mnt/compendium/overlay/dexvert/package.use/wine-32 && ln -s /mnt/compendium/overlay/dexvert/package.use/xanim`,
	`cd`,
	`USE="-harfbuzz" emerge -1 media-libs/freetype`,
	`emerge -uDN world`,
	`USE=minimal emerge mono`,
	`USE=minimal emerge -1 libsndfile`,
	`emerge -1 glibc`,	// to pick up on patch
	`emerge --noreplace ${[
		// used by youtube-dl-max and cosmictv
		"net-misc/yt-dlp",
		
		// need the non-bin version of rust for (I forget what program, but I know it has to do with web assembly patch I do on the source)
		"dev-lang/rust",

		// uniconvertor
		"media-gfx/libimagequant",

		// monitors for changes to files
		"sys-fs/inotify-tools",
		
		// fixes bad filenames
		"app-text/convmv",

		// needed by other packages later (mplayer)
		"media-video/ffmpeg",

		// dos
		"games-emulation/dosbox",
		
		// os.js (win2k & winxp)
		"app-emulation/86Box",
		"app-emulation/virtualbox",
		"x11-misc/x11vnc",

		// used by perlTextCheck.js
		"app-arch/trimGarbage",

		// vamos
		"app-arch/amitools",

		// wine
		"app-emulation/wine-vanilla",

		// used by thumbnail creation
		"media-libs/resvg",

		// needed for fontforge, see package.env/fontforge
		"llvm-core/clang",

		// needed for inkscape
		"dev-python/tinycss2",

		// needed for gameViewerLinux and other python things
		"dev-lang/python:3.12",

		// ENSURE that perl is re-compiled with latest system, otherwise perlTextCheck fails on detecting text files properly, such as with: perl -le 'print "Reading: ", -s shift, " bytes\n"; print -B _ ? "Binary File" : "Likely Text (Perl)"' -- test/sample/archive/text/txt/VOTER.DOC
		"dev-lang/perl"
	].join(" ")}`
].forEach(line => console.log(line));

[
	// video meta provider (needed here AFTER ffmpeg above)
	`emerge --noreplace media-video/mplayer`
].forEach(line => console.log(line));

const postPackages =
[
	// these require mono which is 'fully' installed later
	"media-gfx/pablodraw",
	"app-arch/Aaru",

	// dunno why these don't work in the 'big' emerge, but best done after and in a smaller batch
	"games-util/EasyRPG-Tools"
];

const programPackages = Object.values(programs).flatMap(program => Array.force(program.package)).unique().subtractAll(postPackages).sortMulti().join(" ").innerTrim();

[
	`emerge --noreplace ${programPackages}`,
	`emerge mono`,
	`emerge -1 libsndfile`,
	`emerge -uDN world`,
	`# If pablodraw or Aaru below fail to merge, just try again (often works 2nd time)`,
	`emerge --noreplace ${postPackages.sortMulti().join(" ")}`,
	"eselect news read --quiet all",
	"eselect news purge",
	`depmod -a`,
	`modinfo vhba`,
	`modprobe vhba`,
	`lsmod`,
	`mkdir -p /mnt/dexvert`,
	`# If you have a 2nd hard drive, mount to /mnt/dexvert (via blkid/fstab/UUID, see 'Post Install' section in gentoo_install.txt)`,
	`chown sembiance:sembiance /mnt/dexvert`,
	`usermod -aG vboxusers sembiance`,
	`cd /usr/lib64 && ln -s libimagequant.so libimagequant.so.0 && cd`,	// required for uniconvertor
	`echo -e '<?xml version="1.0" encoding="UTF-8"?>\n<oor:data xmlns:oor="http://openoffice.org/2001/registry">\n  <dependency file="main"/>\n  <oor:component-data oor:package="org.openoffice.Office" oor:name="Common">\n    <node oor:name="Misc">\n      <prop oor:name="UseLocking">\n        <value>false</value>\n      </prop>\n    </node>\n  </oor:component-data>\n</oor:data>' > /usr/lib64/libreoffice/share/registry/disable-file-locking.xcd`,
	`find /usr/portage/distfiles/ -mindepth 1 -delete`,
	`emerge --depclean`,
	`revdep-rebuild -pi`,
	`eix-update`,
	`mkdir -p /mnt/dexdrone`,
	`chown sembiance:sembiance /mnt/dexdrone`,
	`grep dexvert ~/.ssh/authorized_keys >> /home/sembiance/.ssh/authorized_keys`,
	`chown sembiance:sembiance /home/sembiance/.ssh/authorized_keys`,
	`chmod 600 /home/sembiance/.ssh/authorized_keys`,
	`# Need to re-install this now, again, to get it to puck up the correct dotnet version`,
	`emerge app-arch/Aaru`,
	`su - sembiance`,
	`mkdir -p /mnt/dexvert/oldLogs`,
	`# Aaru needs to build a database and ask questions, run it once. Answer 'y' to question #1 about decryption and 'n' to all others.`,
	`aaru`,
	`cd ~/bin && ln -s /mnt/compendium/DevLab/dexvert/bin/dextry && ln -s /mnt/compendium/DevLab/dexvert/bin/stopDexserver && ln -s /mnt/compendium/DevLab/dexvert/bin/startDexserver`,
	`cd /mnt/compendium/DevLab/dexvert/util && dra wip.js`,
	`sudo reboot`,
	`# After reboot, as sembiance@host run and ensure works: startDexserver`,
	"# Run a full 'dra testMany.js --format=all' to ENSURE that the new dexdrone is functioning properly! DO NOT SKIP THIS STEP",
	"# Now add new dexdrone# to dexdaemon/src/C.js DEXDRONES array, then pause processing on discmaster2 and once all dexdrones are quiet, stop dexdaemon and start it back up again"
].forEach(line => console.log(line));
