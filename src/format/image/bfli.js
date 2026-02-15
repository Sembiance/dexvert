import {Format} from "../../Format.js";

export class bfli extends Format
{
	name       = "Big Flexible Line Interpretation";
	website    = "http://fileformats.archiveteam.org/wiki/BFLI";
	ext        = [".bfli"];
	magic      = ["Big Flexible Line Interpretation bitmap", "BFLI :bfli:"];
	fileSize   = 33795;
	converters = ["recoil2png[format:BFLI]", "nconvert[format:bfli]"];
}
