import {Format} from "../../Format.js";

export class moonArchive extends Format
{
	name           = "MOON Archive";
	ext            = [".000"];
	forbidExtMatch = true;
	magic          = [/^geArchive: 000_MOON(_2)?( |$)/];
	converters     = ["gameextractor[codes:000_MOON_2,000_MOON]"];
}
