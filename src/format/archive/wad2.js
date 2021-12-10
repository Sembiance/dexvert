import {Format} from "../../Format.js";

export class wad2 extends Format
{
	name       = "WAD2";
	website    = "http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm";
	ext        = [".wad"];
	magic      = ["WAD2 file"];
	converters = ["gameextractor"];
}
