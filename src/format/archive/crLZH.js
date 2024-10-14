import {Format} from "../../Format.js";

export class crLZH extends Format
{
	name           = "CrLZH Compressed";
	website        = "http://fileformats.archiveteam.org/wiki/CrLZH";
	ext            = [".yyy"];
	forbidExtMatch = true;
	magic          = ["CrLZH compressed", "LZH compressed data", "Crunch-LZHUF"];
	packed         = true;
	converters     = ["unar", "deark[module:crlzh]", "lbrate"];
}
