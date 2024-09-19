import {Format} from "../../Format.js";

export class mrnz extends Format
{
	name           = "MRNZ";
	website        = "http://fileformats.archiveteam.org/wiki/MRNZ";
	ext            = ["_"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["MRNZ installer/obfuscated format"];
	converters     = ["deark[module:mrnz]"];
}
