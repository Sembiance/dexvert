import {Format} from "../../Format.js";

export class cazip extends Format
{
	name           = "CAZIP File";
	website        = "http://fileformats.archiveteam.org/wiki/CAZIP";
	ext            = [".caz", "_"];
	forbidExtMatch = ["_"];
	magic          = ["CAZIP compressed file", "deark: cazip"];
	converters     = ["cazip", "deark[module:cazip]"];
}

