import {Format} from "../../Format.js";

export class yacArchive extends Format
{
	name       = "Yet Another Compressor Archive";
	website    = "http://justsolve.archiveteam.org/wiki/YAC";
	ext        = [".yc"];
	magic      = ["YAC compressed archive", /^YAC archive data/, "YC Archiv gefunden"];
	converters = ["yac"];
}
