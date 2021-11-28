import {Format} from "../../Format.js";

export class runPaint extends Format
{
	name       = "RUN Paint";
	website    = "http://fileformats.archiveteam.org/wiki/RUN_Paint";
	ext        = [".rpm", ".rph", ".rpo"];
	fileSize   = [10003, 10006];
	magic      = ["Koala Paint"];	// Shares magic with Koala Paint
	weakMagic  = true;
	trustMagic = true;	// Koala Paint is normally untrustworthy, but we trust it here
	converters = ["recoil2png", "nconvert", "view64"];
}
