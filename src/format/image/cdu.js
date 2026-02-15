import {Format} from "../../Format.js";

export class cdu extends Format
{
	name       = "CDU-Paint Image";
	website    = "http://fileformats.archiveteam.org/wiki/CDU-Paint";
	ext        = [".cdu"];
	magic      = ["CDU Paint :cdu:"];
	fileSize   = 10277;
	converters = ["recoil2png[format:CDU]", "nconvert[format:cdu]", "view64"];
}
