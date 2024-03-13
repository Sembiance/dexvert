import {Format} from "../../Format.js";

export class pgc extends Format
{
	name       = "Portfolio Graphics Compressed";
	website    = "http://fileformats.archiveteam.org/wiki/PGC_(Portfolio_Graphics_Compressed)";
	ext        = [".pgc"];
	magic      = ["PGC Portfolio Graphics Compressed bitmap", /^fmt\/1734( |$)/];
	converters = ["deark[module:pgc][matchType:magic]", "recoil2png", "nconvert"];
}
