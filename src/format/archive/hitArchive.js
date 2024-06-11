import {Format} from "../../Format.js";

export class hitArchive extends Format
{
	name       = "HIT Archive";
	website    = "http://fileformats.archiveteam.org/wiki/HIT_(compressed_archive)";
	ext        = [".hit"];
	magic      = ["HIT archive data", "HIT compressed archive"];
	converters = ["hit"];
}
