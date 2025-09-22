import {Format} from "../../Format.js";

export class tpk extends Format
{
	name       = "TPK Archive";
	website    = "http://fileformats.archiveteam.org/wiki/TPK_(compressed_archive)";
	magic      = ["TPK Archive", "deark: tpk (TPK)"];
	converters = ["deark[module:tpk]"];
}
