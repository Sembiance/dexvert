import {Format} from "../../Format.js";

export class pma extends Format
{
	name       = "PMA Aachive";
	website    = "http://fileformats.archiveteam.org/wiki/PMA";
	ext        = [".pma"];
	magic      = ["PMarc archive data", "PMarc compressed archive"];
	converters = ["unar", "lha"];
}
