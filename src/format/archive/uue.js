import {Format} from "../../Format.js";

export class uue extends Format
{
	name       = "UU Encoded Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Uuencoding";
	ext        = [".uue", ".uu"];
	magic      = ["uuencoded", "UUencoded"];
	converters = ["uudecode", "sqc", "UniExtract"];
}
