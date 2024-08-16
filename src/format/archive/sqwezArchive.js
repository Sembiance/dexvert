import {Format} from "../../Format.js";

export class sqwezArchive extends Format
{
	name        = "SQWEZ Archive";
	website     = "http://fileformats.archiveteam.org/wiki/SQWEZ";
	ext         = [".sqz"];
	magic       = ["SQWEZ Archiv gefunden", /^SQWEZ archive data/];
	weakMagic   = true;
	unsupported = true;
}
