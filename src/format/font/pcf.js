import {Format} from "../../Format.js";

export class pcf extends Format
{
	name         = "Portable Compiled Format";
	website      = "http://fileformats.archiveteam.org/wiki/PCF";
	ext          = [".pcf"];
	magic        = ["X11 Portable Compiled Font data"];
	metaProvider = ["fc_scan"];
	converters   = ["deark"];
}
