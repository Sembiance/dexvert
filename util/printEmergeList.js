import {xu} from "xu";
import {programs, init as initPrograms} from "../src/program/programs.js";
await initPrograms();

console.log("cd /etc/portage/package.use && ln -s /mnt/compendium/overlay/dexvert/package.use/wine-32");
console.log(`USE="-harfbuzz" emerge media-libs/freetype`);
console.log("emerge -uDN world");
console.log("USE=minimal emerge -1 mono");
console.log("USE=minimal emerge libsndfile");
console.log("emerge -1 glibc");	// to pick up on patch
console.log("emerge --noreplace -p cifs-utils convmv mplayer vncsnapshot libpuzzle dev-lang/go app-emulation/virtualbox games-emulation/dosbox");

const postPackages =
[
	// these require mono which is 'fully' installed later
	"media-gfx/pablodraw",

	// dunno why these don't work in the 'big' emerge, but best done in a smaller batch
	"games-util/EasyRPG-Tools"
];
const programPackages = Object.values(programs).flatMap(program => Array.force(program.package)).unique().subtractAll(postPackages).sortMulti().join(" ").innerTrim();

console.log(`emerge --noreplace ${programPackages}`);
console.log("emerge mono libsndfile");
console.log("emerge -uDN world");
console.log(`emerge --noreplace ${postPackages.sortMulti().join(" ")}`);
console.log(`eix-update`);
console.log(`depmod -a`);
console.log(`modinfo vhba`);
console.log(`modprobe vhba`);
console.log(`lsmod`);
