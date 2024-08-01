import {Format} from "../../Format.js";

export class gz extends Format
{
	name         = "GZip archive";
	website      = "http://fileformats.archiveteam.org/wiki/Gzip";
	ext          = [".gz", ".gzip"];
	keepFilename = true;
	magic        = [
		// general gzip
		"gzip compressed data", "GZipped data", "gzip: Deflate", "GZip Archiv gefunden", "gzip-compressed data", "Archive: GZIP", "Gzip (Self-extracting)", /^Gzip$/, /^x-fmt\/266( |$)/,

		// app specific gzip
		"bar archive gzip-compressed data"
	];
	idMeta       = ({macFileType}) => ["Gzip"].includes(macFileType);
	
	// sevenZip will properly set timestamps. izArc & UniExtract will fully extract, but this is better than not handling at all
	converters   = ["sevenZip", "gunzip", "ancient", "deark[module:gzip]", "unar", "sqc", "izArc[matchType:magic][hasExtMatch]", "UniExtract[matchType:magic][hasExtMatch]"];
}
