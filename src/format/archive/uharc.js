import {Format} from "../../Format.js";

export class uharc extends Format
{
	name       = "UHARC";
	website    = "http://fileformats.archiveteam.org/wiki/UHARC";
	ext        = [".uha"];
	magic      = ["UHARC compressed archive", "UHA Archiv gefunden (Auflistung ist deaktiviert)", /^idarc: UHarc( |$)/, /^UHarc archive data/];
	converters = ["uharcd", "uharc"];
}
