import {Format} from "../../Format.js";

export class americanConquest2GameArchvie extends Format
{
	name           = "American Conquest 2 game archvie";
	ext            = [".gsc"];
	forbidExtMatch = true;
	magic          = ["American Conquest 2 game data archvie", /^geArchive: GSC_GSCFMT( |$)/];
	converters     = ["gameextractor[codes:GSC_GSCFMT]"];
}
