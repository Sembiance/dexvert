import {Format} from "../../Format.js";

export class epfGameArchive extends Format
{
	name           = "EPF Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/EPF_Format";
	ext            = [".epf"];
	forbidExtMatch = true;
	magic          = ["EPF game data archive", /^geArchive: EPF_EPFS( |$)/];
	converters     = ["gameextractor[codes:EPF_EPFS]", "gamearch"];
}
