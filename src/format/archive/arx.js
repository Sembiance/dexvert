import {Format} from "../../Format.js";

export class arx extends Format
{
	name       = "ARX Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ARX";
	ext        = [".arx"];
	magic      = ["ARX compressed archive", "ARX Archiv gefunden", "deark: arx"];
	converters = ["deark[module:arx] -> dexvert[asFormat:archive/lha]"];
}
