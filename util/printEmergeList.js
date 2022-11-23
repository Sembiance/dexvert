import {xu} from "xu";
import {programs} from "../src/program/programs.js";

console.log("USE=minimal emerge -1 mono");
console.log("USE=minimal emerge -p libsndfile");
console.log(`emerge --noreplace -p ${Object.values(programs).flatMap(program => Array.force(program.package)).join(" ").innerTrim()}`);
