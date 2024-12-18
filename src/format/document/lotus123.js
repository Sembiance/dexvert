import {Format} from "../../Format.js";

export class lotus123 extends Format
{
	name       = "Lotus 1-2-3 File";
	website    = "http://fileformats.archiveteam.org/wiki/Lotus_1-2-3";
	ext        = [".wks", ".wk1", ".wk2", ".wk3", ".wk4", ".123", ".wkb"];
	magic      = [
		"Lotus 123 Worksheet", /^Lotus 1-2-3 (unknown )?[Ww]or[Kk][Ss]heet/, "Lotus 1-2-3/Symphony worksheet", "Lotus 123/Symphony worksheet", "Lotus Symphony Worksheet", "Lotus unknown worksheet", "application/vnd.lotus-1-2-3", /^Lotus Symphony WoRksheet/,
		/^fmt\/(1452|1453)( |$)/, /^x-fmt\/(114|115|116|117)( |$)/
	];
	converters = ["soffice[format:Lotus]", "excel97[matchType:magic]", "soffice[matchType:magic]"];
}
