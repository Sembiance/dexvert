import {Format} from "../../Format.js";

export class uharc extends Format
{
	name       = "UHARC";
	website    = "http://fileformats.archiveteam.org/wiki/UHARC";
	ext        = [".uha"];
	magic      = ["UHARC compressed archive", /^UHarc archive data/];
	converters = ["uharcd"];
}
