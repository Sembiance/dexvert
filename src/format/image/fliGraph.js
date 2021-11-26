import {Format} from "../../Format.js";

export class fliGraph extends Format
{
	name     = "FLI Graph Image";
	website  = "http://fileformats.archiveteam.org/wiki/FLI_Graph";
	ext      = [".bml", ".fli"];
	fileSize = {".bml" : 17474, ".fli" : 17409};

	converters = ["recoil2png", "view64"]
}
