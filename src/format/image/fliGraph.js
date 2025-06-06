import {Format} from "../../Format.js";

export class fliGraph extends Format
{
	name       = "FLI Graph/Designer Image";
	website    = "http://fileformats.archiveteam.org/wiki/FLI_Graph";
	ext        = [".bml", ".fli"];
	magic      = ["FLI :bfli:"];
	fileSize   = {".bml" : 17474, ".fli" : 17409};
	converters = ["recoil2png", "view64", "nconvert[format:bfli]"];
}
