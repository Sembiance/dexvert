import {Format} from "../../Format.js";

export class bz2 extends Format
{
	name       = "BZip2 archive";
	website    = "http://fileformats.archiveteam.org/wiki/BZ2";
	ext        = [".bz2", ".bzip2"];
	magic      = ["bzip2 compressed data", "bzip2 compressed archive", "BZIP2 Compressed Archive"];
	converters = ["bunzip2", "sevenZip[singleFile]", "UniExtract"];
}
