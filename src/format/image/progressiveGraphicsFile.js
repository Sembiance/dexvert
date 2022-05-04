import {Format} from "../../Format.js";

export class progressiveGraphicsFile extends Format
{
	name       = "Progressive Graphics File";
	website    = "http://fileformats.archiveteam.org/wiki/PGF_(Progressive_Graphics_File)";
	ext        = [".pgf"];
	magic      = ["Progressive Graphics image data", /^fmt\/1128( |$)/];
	mimeType   = "image/x-pgf";
	converters = ["pgf"];
}
