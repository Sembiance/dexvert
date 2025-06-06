import {Format} from "../../Format.js";

export class diet extends Format
{
	name       = "DIET";
	website    = "http://fileformats.archiveteam.org/wiki/DIET_(compression)";
	magic      = ["DIET compressed data", "deark: diet (DIET-compressed file"];
	packed     = true;
	converters = ["deark[module:diet]", "diet"];
}
