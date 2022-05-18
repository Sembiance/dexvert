import {Format} from "../../Format.js";

export class gz extends Format
{
	name         = "GZip archive";
	website      = "http://fileformats.archiveteam.org/wiki/GZ";
	ext          = [".gz", ".gzip", ".z"];
	keepFilename = true;
	magic        = ["gzip compressed data", "GZipped data", "UNIX compressed data", "compress'd data", "gzip: Deflate", /^x-fmt\/266( |$)/];
	
	// sevenZip will properly set timestamps. izArc & UniExtract will fully extract, but this is better than not handling at all
	converters   = ["sevenZip", "gunzip", "ancient", "sqc", "izArc", "UniExtract", "deark[module:pack]"];
}
