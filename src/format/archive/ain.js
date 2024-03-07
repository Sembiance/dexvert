import {Format} from "../../Format.js";

export class ain extends Format
{
	name       = "AIN Archive";
	website    = "http://fileformats.archiveteam.org/wiki/AIN";
	ext        = [".ain"];
	magic      = ["AIN compressed archive", "AIN Archiv gefunden"];	// I have encountered some files that match from file "AIN archive data" but don't decompress with ain, so likely false positive
	converters = ["ain"];
}
