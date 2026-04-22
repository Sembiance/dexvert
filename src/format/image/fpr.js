import {Format} from "../../Format.js";

export class fpr extends Format
{
	name        = "FLI Profi";
	website     = "http://fileformats.archiveteam.org/wiki/FLI_Profi";
	ext         = [".fpr", ".flp"];
	unsupported = true;	// no magic, unreliable extension, only 1 known sample file and recoil2png/view64 will convert anything
	converters  = ["recoil2png[format:FPR]", "view64"];
}
