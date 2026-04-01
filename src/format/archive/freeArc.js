import {Format} from "../../Format.js";

export class freeArc extends Format
{
	name       = "FreeArc Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ARC_(FreeArc)";
	ext        = [".arc"];
	magic      = ["FreeArc archive", "FreeArc compressed archive", "Archive: FreeARC Archive", /^fmt\/1096( |$)/];
	converters = ["vibeExtract"];
}
