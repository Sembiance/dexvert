import {Format} from "../../Format.js";

export class fpr extends Format
{
	name        = "FLI Profi";
	website     = "http://fileformats.archiveteam.org/wiki/FLI_Profi";
	ext         = [".fpr", ".flp"];
	unsupported = true;
	notes       = "Due to no known magic and how recoil2png/view64 will convert ANYTHING, we disable this for now.";
	converters  = ["recoil2png[format:FPR]", "view64"];
}
