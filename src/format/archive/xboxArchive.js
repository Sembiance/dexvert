import {Format} from "../../Format.js";

export class xboxArchive extends Format
{
	name           = "American Conquest 2 game archive";
	ext            = [".xpr"];
	forbidExtMatch = true;
	magic          = ["Xbox archive", /^geArchive: XPR_XPR1( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:XPR_XPR1]"];
}
