import {Format} from "../../Format.js";

export class wad2 extends Format
{
	name       = "WAD2";
	website    = "http://fileformats.archiveteam.org/wiki/Quake_WAD";
	ext        = [".wad"];
	magic      = ["WAD2 file"];
	converters = ["gameextractor"];
}
