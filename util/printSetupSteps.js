import {xu} from "xu";
import {programs, init as initPrograms} from "../src/program/programs.js";
await initPrograms();

console.log("Install gentoo with: installGentoo --phase=2 --scrubPartitionMap --withX --withQEMU --withNode --withSound --gateway=<gateway> <ip> <hostname>");
console.log("Run the following as root on a fresh Gentoo system to be able to run dexvert:\n");

[
	`cd /etc/portage/package.use && ln -s /mnt/compendium/overlay/dexvert/package.use/wine-32 && ln -s /mnt/compendium/overlay/dexvert/package.use/xanim`,
	`USE="-harfbuzz" emerge -1 media-libs/freetype`,
	`emerge -uDN world`,
	`USE=minimal emerge mono`,
	`USE=minimal emerge -1 libsndfile`,
	`emerge -1 glibc`,	// to pick up on patch
	`emerge --noreplace ${[
		// uniconvertor
		"media-gfx/libimagequant",

		// monitors for changes to files
		"sys-fs/inotify-tools",
		
		// fixes bad filenames
		"app-text/convmv",

		// video meta provider
		"media-video/mplayer",

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
		"sys-devel/clang"
	].join(" ")}`
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
	`# Pabldraw sometimes fails, if so just emerge it again, second time usually works fine`,
	`emerge --noreplace ${postPackages.sortMulti().join(" ")}`,
	`emerge pablodraw`,
	`eix-update`,
	`depmod -a`,
	`modinfo vhba`,
	`modprobe vhba`,
	`lsmod`,
	`mkdir /mnt/dexvert`,
	`chown sembiance:sembiance /mnt/dexvert`,
	`usermod -aG vboxusers sembiance`,
	`cd /usr/lib64 && ln -s libimagequant.so libimagequant.so.0`,	// required for uniconvertor
	`sudo su - sembiance`,
	`echo "Aaru needs to build a database and ask some questions, run it once. Answer 'y' to question #1 about decription and 'n' to all others."`,
	`aaru`,
	`cd ~/bin && ln -s /mnt/compendium/DevLab/dexvert/bin/dextry && ln -s /mnt/compendium/DevLab/dexvert/bin/stopDexserver && ln -s /mnt/compendium/DevLab/dexvert/bin/startDexserver`
].forEach(line => console.log(line));
