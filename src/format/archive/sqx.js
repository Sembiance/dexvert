import {Format} from "../../Format.js";

export class sqx extends Format
{
	name       = "Squeez SQX Archive";
	website    = "http://fileformats.archiveteam.org/wiki/SQX";
	ext        = [".sqx"];
	magic      = ["SQX compressed archive"];
	converters = ["sqc"];
}
