import {Format} from "../../Format.js";

export class packIce extends Format
{
	name       = "Pack-Ice Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Pack-Ice";
	magic      = ["Pack-Ice compressed data", /^fmt\/(1606|1608)( |$)/];
	packed     = true;
	converters = ["unice68"];
}
