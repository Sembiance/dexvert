import {Format} from "../../Format.js";

export class cpr extends Format
{
	name       = "Trzmiel";
	website    = "http://fileformats.archiveteam.org/wiki/Trzmiel";
	ext        = [".cpr"];
	byteCheck  = [{offset : 0, match : [0x02]}];	// have not encountered any that start with anything other than 2
	converters = ["recoil2png[format:CPR]"];
}
