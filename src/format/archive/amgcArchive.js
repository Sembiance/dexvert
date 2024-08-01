import {Format} from "../../Format.js";

export class amgcArchive extends Format
{
	name       = "AMGC Archive";
	website    = "http://fileformats.archiveteam.org/wiki/AMG_(compressed_archive)";
	ext        = [".amg"];
	magic      = ["AMGC compressed archive", /^AMGC archive data/];
	converters = ["amgc"];
}
