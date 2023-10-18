import {Format} from "../../Format.js";

export class arc extends Format
{
	name       = "PAK/ARC Compressed Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ARC_(compression_format)";
	ext        = [".arc", ".pak"];
	magic      = ["PAK/ARC Compressed archive", "ARC archive data"];
	converters = ["unar", "arc", "xarc", "deark[module:arc]", "deark[module:arcmac]", "izArc", "UniExtract[matchType:magic]"];
}
