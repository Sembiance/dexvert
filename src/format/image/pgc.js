import {Format} from "../../Format.js";

export class pgc extends Format
{
	name       = "Portfolio Graphics Compressed";
	website    = "http://fileformats.archiveteam.org/wiki/PGC_(Portfolio_Graphics_Compressed)";
	ext        = [".pgc"];
	magic      = ["PGC Portfolio Graphics Compressed bitmap"];
	converters = ["deark[module:pgc]", "recoil2png", "nconvert"];
}
