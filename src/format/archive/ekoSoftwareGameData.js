import {Format} from "../../Format.js";

export class ekoSoftwareGameData extends Format
{
	name           = "Eko Software game data";
	ext            = [".rck"];
	forbidExtMatch = true;
	magic          = ["Eko Software game data", /^geArchive: RCK_RKET( |$)/];
	converters     = ["gameextractor[codes:RCK_RKET]"];
}
