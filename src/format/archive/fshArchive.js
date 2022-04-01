import {Format} from "../../Format.js";

export class fshArchive extends Format
{
	name       = "FSH Archive";
	website    = "http://fileformats.archiveteam.org/wiki/FSH_(EA_Sports)";
	ext        = [".fsh"];
	magic      = ["The Need For Speed graphics"];
	converters = ["fshtool"];
}
