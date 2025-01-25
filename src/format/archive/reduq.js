import {Format} from "../../Format.js";

export class reduq extends Format
{
	name       = "Reduq Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Reduq";
	ext        = [".rdq"];
	magic      = ["Reduq compressed data", /^ReDuq archive data$/];
	converters = ["unreduq"];
}
