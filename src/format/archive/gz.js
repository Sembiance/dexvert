import {Format} from "../../Format.js";

export class gz extends Format
{
	name       = "GZip archive";
	website    = "http://fileformats.archiveteam.org/wiki/GZ";
	ext        = [".gz", ".gzip", ".z"];
	magic      = ["gzip compressed data", "GZipped data", "UNIX compressed data", "compress'd data"];
	converters = ["gunzip", "sevenZip[singleFile]", "UniExtract"];
}
