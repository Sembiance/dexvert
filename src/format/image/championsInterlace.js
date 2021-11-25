import {Format} from "../../Format.js";

export class championsInterlace extends Format
{
	name     = "Champions' Interlace Image";
	website  = "http://fileformats.archiveteam.org/wiki/Champions%27_Interlace";
	ext      = [".cci", ".cin"];
	fileSize = {".cin" : [15360, 16004, 16384]};

	converters = ["recoil2png"]
}
