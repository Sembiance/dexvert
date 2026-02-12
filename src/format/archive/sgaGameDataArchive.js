import {Format} from "../../Format.js";

export class sgaGameDataArchive extends Format
{
	name           = "SGA game data archive";
	ext            = [".sga"];
	forbidExtMatch = true;
	magic          = ["SGA game data archive", "SGA archive", /^geArchive: SGA_ARCHIVE( |$)/];
	weakMagic      = ["SGA game data archive", "SGA archive"];
	converters     = ["gameextractor[codes:SGA_ARCHIVE]"];
}
