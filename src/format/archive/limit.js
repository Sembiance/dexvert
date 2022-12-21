import {Format} from "../../Format.js";

export class limit extends Format
{
	name       = "LIMIT Archive";
	website    = "http://fileformats.archiveteam.org/wiki/LIMIT";
	ext        = [".lin"];
	magic      = ["Limit compressed archive"];
	converters = ["limit"];
}
