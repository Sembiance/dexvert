import {Format} from "../../Format.js";

export class goatTracker extends Format
{
	name           = "GoatTracker Module";
	ext            = [".sng"];
	forbidExtMatch = true;
	magic          = ["GoatTracker chiptune", /^GoatTracker 2 song/];
	unsupported    = true;	// only 36 unique files on discmaster
}
