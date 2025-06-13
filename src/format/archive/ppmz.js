import {Format} from "../../Format.js";

export class ppmz extends Format
{
	name       = "PPMZ Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PPMZ";
	magic      = ["PPMZ compressed data", "PPMZ Archiv gefunden", /^PPMZ archive data$/];
	packed     = true;
	converters = ["ppmz"];
}
