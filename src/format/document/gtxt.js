import {Format} from "../../Format.js";

export class gtxt extends Format
{
	name           = "GTXT";
	website        = "http://fileformats.archiveteam.org/wiki/GTXT";
	ext            = [".com"];
	forbidExtMatch = true;
	idCheck        = inputFile => inputFile.size>190;
	magic          = ["GTXT"];
	converters     = ["deark[module:gtxt][opt:text:encconv=0][opt:text:fmtconv=0]"];
}
