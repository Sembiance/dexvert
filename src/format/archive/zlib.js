import {Format} from "../../Format.js";

export class zlib extends Format
{
	name         = "ZLIB Compressed Data";
	website      = "http://fileformats.archiveteam.org/wiki/Zlib";
	forbiddenExt = [".dmg"];	// some DMG files identify as ZLIB data, which gameextractor errors out in converting, so never match .dmg files to ZLIB
	magic        = [
		// generic
		"zlib compressed data", "ZLIB compressed data",

		// app specific
		"Easy CD Creator Drag to Disk File"
	];
	converters = ["gameextractor", "zlib_flate", "deark[module:zlib]"];
}
