import {Format} from "../../Format.js";

export class hap extends Format
{
	name       = "Hamarsoft HAP Archive";
	website    = "http://fileformats.archiveteam.org/wiki/HAP";
	ext        = [".hap"];
	magic      = ["Hamarsoft HAP compressed archive (v2", "Hamarsoft HAP compressed archive (v3", "HAP archive data", "HAP Archiv gefunden"];	// only found v2 and v3 files in the wild so far
	converters = ["hap210", "hap306"];
}
