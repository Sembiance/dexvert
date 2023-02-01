import {Format} from "../../Format.js";

export class wackyWheelsArchive extends Format
{
	name         = "Wacky Wheels Archive";
	website      = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Wacky_Wheels)";
	filename     = [/^wacky\.(dat|lid)$/i];
	magic        = ["Wacky Wheels Archive"];
	converters   = ["gamearch"];
}
