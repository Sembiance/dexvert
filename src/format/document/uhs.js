import {Format} from "../../Format.js";

export class uhs extends Format
{
	name       = "Universal Hint System Document";
	website    = "http://fileformats.archiveteam.org/wiki/UHS";
	ext        = [".uhs"];
	magic      = ["Universal Hint System"];
	converters = ["uhs2html[matchType:magic]"];
}
