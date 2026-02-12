import {Format} from "../../Format.js";

export class darkReignGameArchive extends Format
{
	name           = "Dark Reign Game Archive";
	website        = "http://fileformats.archiveteam.org/wiki/FTG_(Dark_Reign)";
	ext            = [".ftg"];
	forbidExtMatch = true;
	magic          = ["Dark Reign game data archive", /^geArchive: FTG_BOTG( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:FTG_BOTG]"];
}
