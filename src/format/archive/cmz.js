import {Format} from "../../Format.js";

export class cmz extends Format
{
	name       = "CMZ Compressed Archive";
	website    = "http://fileformats.archiveteam.org/wiki/CMZ_(archive_format)";
	ext        = [".cmz"];
	magic      = ["CMZ Compressed archive"];
	converters = ["uncmz"];
}
