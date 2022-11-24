import {xu} from "xu";
import {programs} from "../src/program/programs.js";

console.log("Ensure you have both docker and qemu installed and working.");
console.log("USE=minimal emerge -1 mono");
console.log("USE=minimal emerge -p libsndfile");
console.log("emerge --noreplace -p cifs-utils convmv dosbox mplayer");
console.log(`emerge --noreplace -p ${Object.values(programs).flatMap(program => Array.force(program.package)).join(" ").innerTrim()}`);
