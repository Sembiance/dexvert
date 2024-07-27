import {Format} from "../../Format.js";

export class akt extends Format
{
	name       = "AKT Archive";
	website    = "http://fileformats.archiveteam.org/wiki/AKT";
	ext        = [".akt"];
	magic      = ["AKT compressed archive", "AKT9 Archiv gefunden", /^AKT archive data/];
	converters = ["akt"];
}
