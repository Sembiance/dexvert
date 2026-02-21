import {Format} from "../../Format.js";
import {flexMatch} from "../../identify.js";

const MAGIC = [
	// generic
	"zlib compressed data", "ZLIB compressed data",

	// app specific
	"Easy CD Creator Drag to Disk File"
];
const WEAK_MAGIC = ["deark: zlib"];

export class zlib extends Format
{
	name         = "ZLIB Compressed Data";
	website      = "http://fileformats.archiveteam.org/wiki/Zlib";
	forbiddenExt = [".dmg"];	// some DMG files identify as ZLIB data, which gameextractor errors out in converting, so never match .dmg files to ZLIB
	magic        = [...MAGIC, ...WEAK_MAGIC];
	idCheck      = (inputFile, detections) => detections.some(detection => MAGIC.some(m => flexMatch(detection.value, m)));	// ensure we have at least 1 stronger match
	converters   = ["zlib_flate", "deark[module:zlib][extractAll]"];
}
