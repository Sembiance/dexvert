import {Format} from "../../Format.js";

export class wad extends Format
{
	name       = "WAD";
	website    = "http://fileformats.archiveteam.org/wiki/Doom_WAD";
	ext        = [".wad"];
	magic      = ["id Software's DOOM Patch-WAD", "doom patch PWAD", "doom main IWAD", "id Software's DOOM Internal-WAD"];
	converters = ["deark[module:wad]", "gamearch", "gameextractor"];
}
