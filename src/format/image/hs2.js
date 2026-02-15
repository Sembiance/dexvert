import {Format} from "../../Format.js";

export class hs2 extends Format
{
	name       = "HS2 Postering";
	website    = "http://fileformats.archiveteam.org/wiki/HS2_(POSTERING)";
	ext        = [".hs2"];
	magic      = ["deark: hs2"];
	weakMagic  = true;
	converters = ["deark", "recoil2png[format:HS2]"];	// DO NOT SPECIFY [module:hs2] for deark due to weak match against .hs2 and if you specify the module it'll convert almost anything, whereas leaving it empty it will more properly identify the file
}
