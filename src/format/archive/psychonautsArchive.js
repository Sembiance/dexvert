import {Format} from "../../Format.js";

export class psychonautsArchive extends Format
{
	name           = "Psychonauts Archive";
	ext            = [".isb", ".pkg"];
	forbidExtMatch = true;
	magic          = ["Psychonauts game data archive", /^geArchive: (ISB_RIFF|PKG_ZPKG)( |$)/];
	converters     = ["gameextractor[codes:ISB_RIFF,PKG_ZPKG]"];
}
