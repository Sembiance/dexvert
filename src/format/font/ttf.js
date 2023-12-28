import {Format} from "../../Format.js";

export class ttf extends Format
{
	name         = "TrueType Font";
	website      = "http://fileformats.archiveteam.org/wiki/TrueType";
	ext          = [".ttf"];
	magic        = ["TrueType Font", "TrueType Font data", /^x-fmt\/453( |$)/];
	metaProvider = ["fc_scan"];
	converters   = ["convert[format:TTF][background:#C0C0C0]"];
}
