import {Format} from "../../Format.js";

export class evilGeniusGameDataArchive extends Format
{
	name           = "Evil Genius game data archive";
	ext            = [".erb"];
	forbidExtMatch = true;
	magic          = ["Evil Genius game data archive", /^geArchive: ERB_KCAP( |$)/];
	converters     = ["gameextractor[codes:ERB_KCAP]"];
}
