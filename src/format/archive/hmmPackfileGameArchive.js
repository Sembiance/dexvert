import {Format} from "../../Format.js";

export class hmmPackfileGameArchive extends Format
{
	name           = "HMM Packfile Game Archive";
	ext            = [".wdt", ".pak"];
	forbidExtMatch = true;
	magic          = ["Rising Kingdoms game data archive", /^fmt\/1876( |$)/, /^geArchive: PAK_HMMSYS( |$)/];
	converters     = ["gameextractor[codes:PAK_HMMSYS]"];
}
