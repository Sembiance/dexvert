import {Format} from "../../Format.js";

export class wad2GameArchive extends Format
{
	name           = "WAD2 Game Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Quake_WAD";
	ext            = [".wad"];
	forbidExtMatch = true;
	magic          = ["WAD2 file", "Quake WAD", /^geArchive: WAD_WAD2( |$)/];
	converters     = ["gameextractor[codes:WAD_WAD2]"];
}
