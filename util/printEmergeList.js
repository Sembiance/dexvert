import {xu} from "xu";
import {programs, init as initPrograms} from "../src/program/programs.js";
await initPrograms();

console.log("Ensure you have qemu installed and working.\n");
console.log("emerge vanilla-source");	// to pick up on kernel patch
console.log("USE=minimal emerge -1 mono");
console.log("USE=minimal emerge -p libsndfile");
console.log("emerge -1 glibc");	// to pick up on patch
console.log("emerge --noreplace -p cifs-utils convmv dosbox mplayer vncsnapshot libpuzzle dev-python/flask tensorflow dev-lang/go");
console.log(`emerge --noreplace -p ${Object.values(programs).flatMap(program => Array.force(program.package)).unique().sortMulti().join(" ").innerTrim()}`);
console.log("emerge mono libsndfile");
console.log(`depmod -a`);
console.log(`modinfo vhba`);
console.log(`modprobe vhba`);
