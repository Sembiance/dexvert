import {Format} from "../../Format.js";

export class gz extends Format
{
	name         = "GZip archive";
	website      = "http://fileformats.archiveteam.org/wiki/GZ";
	ext          = [".gz", ".gzip", ".z"];
	keepFilename = true;
	magic        = ["gzip compressed data", "GZipped data", "UNIX compressed data", "compress'd data", "gzip: Deflate"];
	
	// sevenZip will properly set timestamps. UniExtract will fully extract, but this is better than not handling at all
	converters   = ["sevenZip", "gunzip", "ancient", "UniExtract", "deark[module:pack]"];
}
