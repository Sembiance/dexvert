import {Format} from "../../Format.js";

export class pagePlus extends Format
{
	name        = "Serif PagePlus Publication";
	website     = "http://fileformats.archiveteam.org/wiki/Serif_PagePlus";
	ext         = [".ppp", ".ppx", ".ppb", ".ppt"];
	magic       = ["Serif PagePlus Publication", "Serif PagePlus Pubblication", /^fmt\/(672|673|674|675|676|677|678|679|680|681|1529|1531|1532|1534|1535|1537)( |$)/];
	unsupported = true;
	notes       = "Could probably very easily install PagePlus 9 or 10 (NOT X9) and use it to convert to RTF/PDF, but have only encountered a single CD with these files on it so far.";
}
