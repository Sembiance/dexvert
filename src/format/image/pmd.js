import {Format} from "../../Format.js";

export class pmd extends Format
{
	name       = "PMG Designer";
	website    = "http://fileformats.archiveteam.org/wiki/PMG_Designer";
	ext        = [".pmd"];
	magic      = ["PMG Designer bitmap"];
	converters = ["recoil2png"]
}
