import {Format} from "../../Format.js";

export class lotus123 extends Format
{
	name       = "Lotus 1-2-3 File";
	website    = "http://fileformats.archiveteam.org/wiki/Lotus_1-2-3";
	ext        = [".wks", ".wk1", ".wk2", ".wk3", ".wk4", ".123", ".wkb"];
	magic      = ["Lotus 123 Worksheet", /^Lotus 1-2-3 Wor[Kk][Ss]heet/, "Lotus 1-2-3/Symphony worksheet", "Lotus 123/Symphony worksheet"];
	converters = ["soffice"];
}
