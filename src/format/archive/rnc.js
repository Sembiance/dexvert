import {Format} from "../../Format.js";

export class rnc extends Format
{
	name       = "Pro-Pack - Rob Northern Compression";
	website    = "http://fileformats.archiveteam.org/wiki/RNC";
	ext        = [".rnc"];
	magic      = ["Rob Northen Compression", "PRO-PACK archive data", "RNC1: Rob Northen RNC1 Compressor"];
	packed     = true;
	converters = ["ancient"];
}
