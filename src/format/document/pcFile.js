import {Format} from "../../Format.js";

export class pcFile extends Format
{
	name        = "PC-File";
	website     = "http://fileformats.archiveteam.org/wiki/PC-FILE";
	ext         = [".dbf", ".rep"];
	magic       = ["PC-File data"];
	unsupported = true;
	notes       = "Was a somewhat used database program back in the day. Didn't really dig into what converters might be possible.";
}
