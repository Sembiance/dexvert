import {Format} from "../../Format.js";

export class ace extends Format
{
	name       = "ACE Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ACE";
	ext        = [".ace"];
	magic      = ["ACE archive data", "ACE compressed archive"];
	converters = ["unace"];
}
