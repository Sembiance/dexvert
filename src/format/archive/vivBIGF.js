import {Format} from "../../Format.js";

export class vivBIGF extends Format
{
	name           = "VIV/BIGF/BIG4 EA Game Archive";
	website        = "http://fileformats.archiveteam.org/wiki/VIV";
	ext            = [".viv", ".big"];
	forbidExtMatch = true;
	magic          = ["VIV/BIGF Electronic Arts Game Archive", "Archive: BIGF", "BIG4 Electronic Arts game data archive", /^geArchive: VIV( |$)/, /^geArchive: (BIG_BIGF|BIG_BIGF_3)( |$)/];
	weakMagic      = [/^geArchive: VIV( |$)/];
	converters     = ["gameextractor[codes:VIV,BIG_BIGF,BIG_BIGF_3]"];
}
