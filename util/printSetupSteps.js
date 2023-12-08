import {xu} from "xu";
import {programs, init as initPrograms} from "../src/program/programs.js";
await initPrograms();

console.log("Run the following as root on a fresh Gentoo system to be able to run dexvert:\n");

[
	`cd /etc/portage/package.use && ln -s /mnt/compendium/overlay/dexvert/package.use/wine-32 && ln -s /mnt/compendium/overlay/dexvert/package.use/xanim`,
	`USE="-harfbuzz" emerge -1 media-libs/freetype`,
	`emerge -uDN world`,
	`USE=minimal emerge mono`,
	`USE=minimal emerge -1 libsndfile`,
	`emerge -1 glibc`,	// to pick up on patch
	`emerge --noreplace ${[
		"cifs-utils",
		"convmv",
		"mplayer",
		"vncsnapshot",
		"libpuzzle",
		"dev-lang/go",
		"games-emulation/dosbox",
		"86Box",
		"app-emulation/virtualbox",
		"x11vnc",
		"wine-vanilla"
	].join(" ")}`
].forEach(line => console.log(line));

const postPackages =
[
	// these require mono which is 'fully' installed later
	"media-gfx/pablodraw",

	// dunno why these don't work in the 'big' emerge, but best done in a smaller batch
	"games-util/EasyRPG-Tools"
];

const programPackages = Object.values(programs).flatMap(program => Array.force(program.package)).unique().subtractAll(postPackages).sortMulti().join(" ").innerTrim();

[
	`emerge --noreplace ${programPackages}`,
	`emerge mono`,
	`emerge -1 libsndfile`,
	`emerge -uDN world`,
	`emerge --noreplace ${postPackages.sortMulti().join(" ")}`,
	`eix-update`,
	`depmod -a`,
	`modinfo vhba`,
	`modprobe vhba`,
	`lsmod`,
	`mkdir /mnt/dexvert`,
	`chown sembiance:sembiance /mnt/dexvert`,
	`usermod -aG vboxusers sembiance`,
	`cd /usr/lib64 && ln -s libimagequant.so libimagequant.so.0`	// required for uniconvertor
].forEach(line => console.log(line));
