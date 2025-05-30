import {Format} from "../../Format.js";

export class bfli extends Format
{
	name       = "Big Flexible Line Interpretation";
	website    = "http://fileformats.archiveteam.org/wiki/BFLI";
	ext        = [".bfli"];
	magic      = ["Big Flexible Line Interpretation bitmap"];
	fileSize   = 33795;
	converters = ["recoil2png"];
}
