import {Format} from "../../Format.js";

export class dmk extends Format
{
	name       = "TRS-80 Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/DMK";
	ext        = [".dmk", ".dsk"];
	magic      = ["TRS-80 DMK"];
	converters = ["trsread"];
}
