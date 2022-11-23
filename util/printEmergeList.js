import {xu} from "xu";
import {programs} from "../src/program/programs.js";

console.log(`emerge -p ${Object.values(programs).flatMap(program => Array.force(program.package)).join(" ").innerTrim()}`);
