import {Format} from "../../Format.js";

export class fliGraph extends Format
{
	name       = "FLI Graph/Designer Image";
	website    = "http://fileformats.archiveteam.org/wiki/FLI_Graph";
	ext        = [".bml", ".fli"];
	magic      = ["FLI :bfli:"];
	fileSize   = {".bml" : 17474, ".fli" : 17409};
	converters = [
		"recoil2png[format:FLI.Fli,FLI.Bml,BML]",	// the ordering here matters, it matches the order recoil uses when not passing --format, which appears to be the proper order since both Bml and Fli share .fli extension
		"view64", "nconvert[format:bfli]"
	];
}
