import {Format} from "../../Format.js";

export class timexHiColor extends Format
{
	name       = "Timex 2048 Hi-Color";
	website    = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	ext        = [".scr"];
	fileSize   = 12288;
	idCheck    = inputFile => !["custom", "gr", "strings"].includes(inputFile.name.toLowerCase());	// These are false positives that recur in the wild
	converters = ["recoil2png"];
}
