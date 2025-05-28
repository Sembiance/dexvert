import {Format} from "../../Format.js";
import {_PS_MAGIC} from "./ps.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class pcl extends Format
{
	name           = "HP Printer Command Language";
	website        = "http://fileformats.archiveteam.org/wiki/PCL";
	ext            = [".pcl", ".prn", ".hp", ".hp2"];
	forbidExtMatch = [".prn"];
	forbiddenMagic = [
		..._PS_MAGIC,	// Often Postscript files are mis-identified as PCL files. If it ends in .ps just never allow a match
		...TEXT_MAGIC_STRONG	// Many things are mis-identified as PCL, so if we have a strong text match, don't allow a PCL match
	];
	mimeType   = "application/vnd.hp-PCL";
	magic      = ["HP Printer Command Language", "HP PCL printer data"];
	converters = ["gpcl6[matchType:magic]"];
}
