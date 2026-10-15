import {Format} from "../../Format.js";

export class rnc extends Format
{
	name       = "Pro-Pack - Rob Northern Compression";
	website    = "http://fileformats.archiveteam.org/wiki/Pro-Pack";
	ext        = [".rnc"];
	magic      = ["Rob Northen Compression", "PRO-PACK archive data", /^RNC\d: Rob Northen RNC\d Compressor/, "Archive: Rob Northen Compressor", /^idarc: PRO-PACK( |$)/];
	packed     = true;
	converters = ["ancient"];
}
