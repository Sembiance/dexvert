import {Format} from "../../Format.js";

export class howToSurviveSeriesGameArchive extends Format
{
	name           = "How to Survive series Game Archive";
	ext            = [".rck"];
	forbidExtMatch = true;
	magic          = ["How to Survive series game data", "Format: RCK", /^geArchive: RCK_RKET( |$)/];
	converters     = ["gameextractor[codes:RCK_RKET]"];
}
