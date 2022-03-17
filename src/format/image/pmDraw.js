import {Format} from "../../Format.js";

export class pmDraw extends Format
{
	name        = "PMDraw";
	website     = "http://fileformats.archiveteam.org/wiki/PmDraw";
	ext         = [".pmd"];
	magic       = ["PMDraw drawing/presentation"];
	unsupported = true;
	notes       = "No known converter. OS/2 drawing program. I could emulate OS/2 and run actual PMDraw and export.";
}
