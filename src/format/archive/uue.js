import {Format} from "../../Format.js";

export class uue extends Format
{
	name       = "UU Encoded Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Uuencoding";
	ext        = [".uue", ".uu"];
	magic      = ["uuencoded", "UUencoded", /^fmt\/1102( |$)/];
	converters = ["uudecode", "sqc", "UniExtract"];
}
