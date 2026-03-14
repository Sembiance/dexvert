import {Format} from "../../Format.js";

export class americanConquest2GameArchive extends Format
{
	name           = "American Conquest 2 game archive";
	ext            = [".gs1", ".gsc"];
	forbidExtMatch = true;
	magic          = ["American Conquest 2 game data archvie", /^geArchive: GSC_GSCFMT( |$)/];
	converters     = ["gameextractor[codes:GSC_GSCFMT]"];
}
