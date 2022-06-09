import {Format} from "../../Format.js";

export class diet extends Format
{
	name       = "DIET";
	website    = "http://fileformats.archiveteam.org/wiki/DIET_(compression)";
	magic      = ["DIET compressed data"];
	packed     = true;
	converters = ["diet"];
}
