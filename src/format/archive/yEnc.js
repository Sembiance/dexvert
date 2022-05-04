import {Format} from "../../Format.js";

export class yEnc extends Format
{
	name       = "yEnc Encoded Archive";
	website    = "http://fileformats.archiveteam.org/wiki/YEnc";
	ext        = [".ync", ".yenc"];
	magic      = ["yEnc Encoded", /^fmt\/1100( |$)/];
	converters = ["yydecode", "UniExtract"];
}
