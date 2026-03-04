import {Format} from "../../Format.js";

export class cazip extends Format
{
	name           = "CAZIP File";
	website        = "http://fileformats.archiveteam.org/wiki/CAZIP";
	ext            = [".caz", "_"];
	forbidExtMatch = ["_"];
	packed         = true;
	magic          = ["CAZIP compressed file", "deark: cazip"];
	converters     = ["deark[module:cazip]", "cazip"];
}

