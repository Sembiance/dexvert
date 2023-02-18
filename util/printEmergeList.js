import {xu} from "xu";
import {programs} from "../src/program/programs.js";

console.log("Ensure you have both docker and qemu installed and working.\n");
console.log("emerge vanilla-source");	// to pick up on kernel patch
console.log("USE=minimal emerge -1 mono");
console.log("USE=minimal emerge -p libsndfile");
console.log("emerge -1 glibc");	// to pick up on patch
console.log("emerge --noreplace -p cifs-utils convmv dosbox mplayer vncsnapshot libpuzzle");
console.log(`emerge --noreplace -p ${Object.values(programs).flatMap(program => Array.force(program.package)).unique().sortMulti().join(" ").innerTrim()}`);
console.log("emerge mono libsndfile");
