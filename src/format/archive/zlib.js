import {Format} from "../../Format.js";

export class zlib extends Format
{
	name       = "ZLIB Compressed Data";
	website    = "http://fileformats.archiveteam.org/wiki/Zlib";
	magic      = ["zlib compressed data", "ZLIB compressed data"];
	converters = ["gameextractor", "deark[module:zlib]"];
}
