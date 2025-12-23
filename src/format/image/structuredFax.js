import {Format} from "../../Format.js";

export class structuredFax extends Format
{
	name       = "Structured Fax";
	website    = "http://fileformats.archiveteam.org/wiki/Structured_Fax_File";
	ext        = [".sff"];
	magic      = ["structured fax file", "Structured Fax Format bitmap"];
	converters = ["nconvertWine", "irfanView"];
}
