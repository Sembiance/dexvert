import {Format} from "../../Format.js";

export class runPaint extends Format
{
	name       = "RUN Paint";
	website    = "http://fileformats.archiveteam.org/wiki/RUN_Paint";
	ext        = [".rpm", ".rph", ".rpo"];
	fileSize   = [10003, 10006];
	magic      = ["Koala Paint", "RunPaint Multicolor :rpm:"];	// Shares magic with Koala Paint
	weakMagic  = true;
	trustMagic = true;	// Koala Paint is normally untrustworthy, but we trust it here
	converters = ["recoil2png[format:RPM,RPH,RPO]", "nconvert[format:rpm]", "view64"];
}
