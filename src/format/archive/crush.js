import {Format} from "../../Format.js";

export class crush extends Format
{
	name           = "Crush Archive";
	website        = "http://fileformats.archiveteam.org/wiki/CRUSH";
	ext            = [".cru"];
	forbidExtMatch = true;
	magic          = ["Crush archive", /^Crush archive data/, "deark: crush (CRUSH archive)"];
	converters     = ["deark[module:crush]", "uncrush"];
}
