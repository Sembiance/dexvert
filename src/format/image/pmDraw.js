import {Format} from "../../Format.js";

export class pmDraw extends Format
{
	name        = "PMDraw";
	website     = "http://fileformats.archiveteam.org/wiki/PmDraw";
	ext         = [".pmd"];
	magic       = ["PMDraw drawing/presentation"];
	unsupported = true;
	notes       = "No known converter. OS/2 drawing program. PMDraw on OS/2 does not support exporting from command line, so would need some sort of AutoIt like util for OS/2.";
}
