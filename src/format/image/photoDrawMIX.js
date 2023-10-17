import {Format} from "../../Format.js";

export class photoDrawMIX extends Format
{
	name       = "PhotoDraw MIX";
	website    = "http://fileformats.archiveteam.org/wiki/MIX_(PhotoDraw)";
	ext        = [".mix"];
	magic      = ["Microsoft PhotoDraw drawing", /^fmt\/594( |$)/];
	converters = ["deark[module:cfb]", "nconvert"];
	notes      = "Only thumbnail extraction is supported.";
}
