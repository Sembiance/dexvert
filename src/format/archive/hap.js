import {Format} from "../../Format.js";

export class hap extends Format
{
	name       = "Hamarsoft HAP Archive";
	website    = "http://fileformats.archiveteam.org/wiki/HAP";
	ext        = [".hap"];
	magic      = ["Hamarsoft HAP compressed archive (v2.10)"];		// NOTE! Only v2.10 files supported right now. Haven't encountered the 3.00 variant yet in the wild
	converters = ["hap210"];
}
