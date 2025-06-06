import {Format} from "../../Format.js";

export class gigaCad extends Format
{
	name       = "Giga Cad";
	website    = "http://fileformats.archiveteam.org/wiki/Giga Cad";
	ext        = [".gcd"];
	magic      = ["Gigacad Hires :gcd:"];
	converters = ["recoil2png", "nconvert[format:gcd]"];
}
