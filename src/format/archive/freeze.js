import {Format} from "../../Format.js";

export class freeze extends Format
{
	name         = "Freeze Frozen Compressed File";
	website      = "http://fileformats.archiveteam.org/wiki/Freeze/Melt";
	ext          = [".f", ".lzc"];
	keepFilename = true;
	magic        = ["Freeze archive data", "frozen file", "Freeze compressed data", "F: Freeze/Melt"];
	packed       = true;
	converters   = ["freeze", "ancient"];
}
