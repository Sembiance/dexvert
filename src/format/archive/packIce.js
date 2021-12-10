import {Format} from "../../Format.js";

export class packIce extends Format
{
	name       = "Pack-Ice Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Pack-Ice";
	magic      = ["Pack-Ice compressed data"];
	converters = ["unice68"];
}
