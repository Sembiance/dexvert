import {Format} from "../../Format.js";

export class sgaGameDataArchive extends Format
{
	name           = "SGA game data archive";
	ext            = [".sga"];
	forbidExtMatch = true;
	magic          = ["SGA game data archive", "SGA archive", /^geArchive: SGA_ARCHIVE(_3)?( |$)/];
	weakMagic      = ["SGA game data archive", "SGA archive"];
	converters     = ["gameextractor[codes:SGA_ARCHIVE]", "gameextractor[codes:SGA_ARCHIVE_3]"];
}
