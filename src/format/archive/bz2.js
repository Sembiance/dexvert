import {Format} from "../../Format.js";

export class bz2 extends Format
{
	name         = "BZip2 archive";
	website      = "http://fileformats.archiveteam.org/wiki/BZ2";
	ext          = [".bz2", ".bzip2"];
	keepFilename = true;
	magic        = ["bzip2 compressed data", "bzip2 compressed archive", "BZIP2 Compressed Archive"];
	converters   = ["bunzip2", "sevenZip", "UniExtract"];	// UniExtract will fully extract, but this is better than not handling at all
}
