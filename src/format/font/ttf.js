import {Format} from "../../Format.js";

export class ttf extends Format
{
	name         = "TrueType Font";
	website      = "http://fileformats.archiveteam.org/wiki/TrueType";
	ext          = [".ttf"];
	magic        = ["TrueType Font", "TrueType Font data", "Truetype Schriftart", "Format: TrueType font", "font/ttf", /^x-fmt\/453( |$)/];
	weakMagic    = ["font/ttf"];
	metaProvider = ["fc_scan"];
	converters   = ["convert[format:TTF][background:#C0C0C0][matchType:magic]"];
}
