import {Format} from "../../Format.js";

export class ppd extends Format
{
	name           = "PostScript Printer Description";
	website        = "http://fileformats.archiveteam.org/wiki/PostScript_Printer_Description";
	ext            = [".ppd", ".pp"];
	forbidExtMatch = true;
	magic          = ["PPD file", "PostScript Printer Description"];
	untouched      = true;
	metaProvider   = ["text"];
}
