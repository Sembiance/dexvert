import {Format} from "../../Format.js";

export class goatTracker extends Format
{
	name        = "GoatTracker Module";
	ext         = [".sng"];
	magic       = ["GoatTracker chiptune", /^GoatTracker 2 song/,];
	unsupported = true;
}
