import {Format} from "../../Format.js";

export class daveDAT extends Format
{
	name           = "Dave DAT Archive";
	ext            = [".ar", ".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_DAVE( |$)/];
	converters     = ["gameextractor[codes:DAT_DAVE]"];
}
