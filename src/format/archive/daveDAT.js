import {Format} from "../../Format.js";

export class daveDAT extends Format
{
	name           = "Dave DAT Archive";
	ext            = [".ar"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_DAVE( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:DAT_DAVE]"];
}
