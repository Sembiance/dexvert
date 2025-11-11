import {Format} from "../../Format.js";

export class bz2 extends Format
{
	name       = "BZip2 archive";
	website    = "http://fileformats.archiveteam.org/wiki/bzip2";
	ext        = [".bz2", ".bzip2"];
	packed     = true;
	magic      = [
		// generic
		"bzip2 compressed data", "bzip2 compressed archive", "BZIP2 Compressed Archive", "bz2: bzip2", "BZ Archiv gefunden", "bzip2-compressed data", "Archive: BZip2", "application/x-bzip2", "bar archive bzip2-compressed data", /^Bzip2$/,
		/^x-fmt\/268( |$)/,

		// app specific
		"Gentoo binary package (XPAK)"
	];
	converters = ["bunzip2", "sevenZip", "ancient", "unar", "sqc", "izArc[matchType:magic]", "UniExtract[matchType:magic]"];	// izArc & UniExtract will fully extract, but this is better than not handling at all
}
