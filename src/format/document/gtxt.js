import {Format} from "../../Format.js";

export class gtxt extends Format
{
	name           = "GTXT";
	website        = "http://fileformats.archiveteam.org/wiki/GTXT_and_MakeScroll";
	ext            = [".com"];
	forbidExtMatch = true;
	idCheck        = inputFile => inputFile.size>190;
	magic          = ["GTXT", "16bit COM GTXT/MakeScroll reader", "deark: gtxt"];
	converters     = ["deark[module:gtxt][opt:text:encconv=0][opt:text:fmtconv=0]"];
}
